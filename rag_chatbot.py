from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from database import SupabaseDB
from document_processor import DSM5Processor
import os
import re
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class DSM5Chatbot:
    def __init__(self):
        self.db = SupabaseDB()
        self.processor = DSM5Processor()
        self.llm = ChatOpenAI(
            temperature=0.1,
            model_name="gpt-3.5-turbo"
        )
        self.vector_store = self.db.get_vector_store()
        self.store = {}  # Session store for chat histories
        self.setup_chains()
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for a session"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def setup_chains(self):
        """Set up the RAG chains with chat history"""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # Contextualize question prompt
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Create history-aware retriever
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )
        
        # Assessment prompt for determining if clarifying questions are needed
        self.assessment_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a diagnostic assessment agent. Your job is to determine if the user's question requires clarifying questions before providing DSM-5 information.

Analyze the question and chat history to determine:
1. Is this a diagnostic question (asking about having a condition, patient diagnosis, etc.)?
2. Is there sufficient information about symptoms, duration, and impact?

Respond with ONLY one of these actions:
- ASK_CLARIFYING: If it's diagnostic but lacks sufficient detail
- PROVIDE_INFO: If there's enough context or it's a general question
- PROVIDE_CAUTIOUS: If it's diagnostic with some but not complete information

Consider these factors:
- Specific symptoms mentioned (need at least 2-3)
- Duration/timeline mentioned
- Functional impact described
- Whether it's about self, patient, or general information"""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Clarifying questions prompt
        self.clarifying_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a responsible mental health assistant. The user has asked a diagnostic question but hasn't provided enough information.

Generate 2-3 empathetic clarifying questions to gather:
- Specific symptoms or concerns
- Duration and timeline
- Impact on daily functioning

Be supportive and explain that you need more details to provide relevant DSM-5 information. Always emphasize that this is educational only and professional evaluation is needed for diagnosis."""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Main QA prompt
        qa_system_prompt = """You are a helpful assistant providing educational information from the DSM-5 (Diagnostic and Statistical Manual of Mental Disorders, 5th Edition).

CRITICAL GUIDELINES:
- NEVER diagnose or suggest someone has a specific condition
- Always emphasize that only qualified professionals can provide diagnoses
- Provide educational information about conditions and criteria
- Be empathetic and supportive
- Suggest seeking professional help when appropriate
- Always mention this is for informational purposes only

Use the following context from DSM-5 to answer questions accurately while being responsible about mental health.

{context}"""
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Create document chain
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
        
        # Create RAG chain
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)
        
        # Create conversational RAG chain with history
        self.conversational_rag_chain = RunnableWithMessageHistory(
            self.rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
    
    def add_documents(self, file_path: str = None):
        """Add DSM-5 documents to the vector store"""
        if file_path:
            documents = self.processor.load_dsm5_documents(file_path)
            documents = self.processor.add_metadata(documents)
        else:
            # Load from URL
            documents = self.processor.load_dsm5_from_url()
        
        self.vector_store.add_documents(documents)
        print(f"Added {len(documents)} document chunks to the vector store")
    
    def assess_information_need(self, question: str, session_id: str = "default") -> str:
        """Assess if more information is needed using the LLM"""
        history = self.get_session_history(session_id)
        
        # Use the assessment chain
        assessment_chain = self.assessment_prompt | self.llm | StrOutputParser()
        
        result = assessment_chain.invoke({
            "input": question,
            "chat_history": history.messages
        })
        
        return result.strip()
    
    def chat(self, question: str, session_id: str = "default"):
        """Chat with the DSM-5 RAG system using multi-step approach"""
        try:
            # Step 1: Assess if more information is needed
            assessment = self.assess_information_need(question, session_id)
            
            if assessment == "ASK_CLARIFYING":
                # Generate clarifying questions
                clarifying_chain = self.clarifying_prompt | self.llm | StrOutputParser()
                history = self.get_session_history(session_id)
                
                answer = clarifying_chain.invoke({
                    "input": question,
                    "chat_history": history.messages
                })
                
                # Add to history
                history.add_user_message(question)
                history.add_ai_message(answer)
                
                return {
                    "answer": answer,
                    "sources": [],
                    "needs_more_info": True,
                    "assessment": assessment,
                    "action_taken": "asked_clarifying_questions"
                }
            
            else:
                # Use RAG chain to provide information
                response = self.conversational_rag_chain.invoke(
                    {"input": question},
                    config={"configurable": {"session_id": session_id}}
                )
                
                return {
                    "answer": response["answer"],
                    "sources": response.get("context", []),
                    "needs_more_info": False,
                    "assessment": assessment,
                    "action_taken": "provided_information"
                }
                
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}", 
                "sources": [], 
                "needs_more_info": False,
                "assessment": "ERROR",
                "action_taken": "error_handling"
            }
    
    def clear_memory(self, session_id: str = "default"):
        """Clear conversation memory for a session"""
        if session_id in self.store:
            del self.store[session_id]
    
    def get_conversation_summary(self, session_id: str = "default"):
        """Get a summary of the current conversation"""
        history = self.get_session_history(session_id)
        messages = history.messages
        
        # Extract information from messages
        user_messages = [msg.content for msg in messages if hasattr(msg, 'content') and msg.type == 'human']
        
        # Simple symptom detection
        symptom_keywords = ["feel", "feeling", "symptoms", "problems", "difficulty", "trouble"]
        symptom_mentions = 0
        
        for msg in user_messages:
            msg_lower = msg.lower()
            symptom_mentions += sum(1 for keyword in symptom_keywords if keyword in msg_lower)
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "symptom_mentions": symptom_mentions,
            "has_enough_context": symptom_mentions >= 3
        }