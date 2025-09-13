"""
Tools for the DSM-5 multi-step agent
"""
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, List, Dict, Any
import json

class AssessInformationNeedInput(BaseModel):
    """Input for assessing if more information is needed"""
    question: str = Field(description="The user's question")
    conversation_history: List[str] = Field(description="Previous conversation messages")
    
class AssessInformationNeedTool(BaseTool):
    """Tool to assess if more information is needed before providing diagnostic info"""
    name = "assess_information_need"
    description = "Determines if more information is needed before providing diagnostic information"
    args_schema = AssessInformationNeedInput
    
    def _run(self, question: str, conversation_history: List[str]) -> str:
        """Assess if more information is needed"""
        
        # Check if it's a diagnostic question
        diagnostic_keywords = [
            "do i have", "does my patient have", "patient has", "client has",
            "diagnosis", "diagnose", "symptoms suggest", "signs of",
            "my patient had", "if my patient", "think i have", "could i have"
        ]
        
        question_lower = question.lower()
        is_diagnostic = any(keyword in question_lower for keyword in diagnostic_keywords)
        
        if not is_diagnostic:
            return json.dumps({
                "needs_more_info": False,
                "reason": "Not a diagnostic question - can provide general information",
                "action": "provide_information"
            })
        
        # Extract symptoms/details from conversation
        symptom_indicators = [
            "feel", "feeling", "experiencing", "symptoms", "problems",
            "difficulty", "trouble", "can't sleep", "appetite", "mood",
            "energy", "concentration", "anxiety", "depression", "sad",
            "worried", "panic", "restless", "hyperactive", "inattentive"
        ]
        
        details_count = 0
        mentioned_details = []
        
        # Check current question and history for symptom details
        all_text = question + " " + " ".join(conversation_history)
        all_text_lower = all_text.lower()
        
        for indicator in symptom_indicators:
            if indicator in all_text_lower:
                details_count += 1
                # Extract context around the indicator
                words = all_text_lower.split()
                for i, word in enumerate(words):
                    if indicator in word:
                        context_start = max(0, i-3)
                        context_end = min(len(words), i+4)
                        context = " ".join(words[context_start:context_end])
                        mentioned_details.append(context)
                        break
        
        # Check for duration indicators
        duration_indicators = ["weeks", "months", "years", "days", "since", "for", "started"]
        has_duration = any(indicator in all_text_lower for indicator in duration_indicators)
        
        # Check for severity/impact indicators
        impact_indicators = ["work", "school", "relationships", "daily", "functioning", "life", "severe", "mild"]
        has_impact = any(indicator in all_text_lower for indicator in impact_indicators)
        
        # Decision logic
        if details_count >= 3 and has_duration and has_impact:
            return json.dumps({
                "needs_more_info": False,
                "reason": f"Sufficient information provided: {details_count} symptoms, duration mentioned, impact described",
                "action": "provide_information",
                "details_found": mentioned_details[:3]
            })
        elif details_count >= 2 and (has_duration or has_impact):
            return json.dumps({
                "needs_more_info": False,
                "reason": f"Adequate information for educational response: {details_count} symptoms with context",
                "action": "provide_cautious_information",
                "details_found": mentioned_details[:3]
            })
        else:
            missing_aspects = []
            if details_count < 2:
                missing_aspects.append("specific symptoms")
            if not has_duration:
                missing_aspects.append("duration/timeline")
            if not has_impact:
                missing_aspects.append("functional impact")
                
            return json.dumps({
                "needs_more_info": True,
                "reason": f"Need more information about: {', '.join(missing_aspects)}",
                "action": "ask_clarifying_questions",
                "missing_aspects": missing_aspects,
                "details_found": mentioned_details[:2]
            })

class GenerateClarifyingQuestionsInput(BaseModel):
    """Input for generating clarifying questions"""
    question: str = Field(description="The user's question")
    missing_aspects: List[str] = Field(description="What information is missing")
    condition_mentioned: Optional[str] = Field(description="Any specific condition mentioned")

class GenerateClarifyingQuestionsTool(BaseTool):
    """Tool to generate appropriate clarifying questions"""
    name = "generate_clarifying_questions"
    description = "Generates specific clarifying questions based on what information is missing"
    args_schema = GenerateClarifyingQuestionsInput
    
    def _run(self, question: str, missing_aspects: List[str], condition_mentioned: Optional[str] = None) -> str:
        """Generate clarifying questions"""
        
        questions = []
        
        # Questions based on missing aspects
        if "specific symptoms" in missing_aspects:
            if condition_mentioned:
                if "depression" in condition_mentioned.lower():
                    questions.extend([
                        "Can you describe the specific mood changes you've noticed?",
                        "Have there been changes in sleep, appetite, or energy levels?"
                    ])
                elif "anxiety" in condition_mentioned.lower():
                    questions.extend([
                        "What physical symptoms do you experience during anxious moments?",
                        "Are there specific situations that trigger these feelings?"
                    ])
                elif "adhd" in condition_mentioned.lower():
                    questions.extend([
                        "Can you describe the attention or focus difficulties?",
                        "Are there issues with hyperactivity or impulsiveness?"
                    ])
            else:
                questions.extend([
                    "Can you describe the specific symptoms or concerns in more detail?",
                    "What changes have you noticed in thoughts, feelings, or behaviors?"
                ])
        
        if "duration/timeline" in missing_aspects:
            questions.extend([
                "How long have these symptoms been present?",
                "When did you first notice these changes?"
            ])
        
        if "functional impact" in missing_aspects:
            questions.extend([
                "How are these symptoms affecting daily activities, work, or relationships?",
                "What areas of life have been most impacted?"
            ])
        
        # Limit to 3 most relevant questions
        selected_questions = questions[:3]
        
        return json.dumps({
            "clarifying_questions": selected_questions,
            "focus_areas": missing_aspects,
            "approach": "empathetic_information_gathering"
        })

class RetrieveDSM5InfoInput(BaseModel):
    """Input for retrieving DSM-5 information"""
    query: str = Field(description="Search query for DSM-5 information")
    context_details: List[str] = Field(description="Additional context from conversation")

class RetrieveDSM5InfoTool(BaseTool):
    """Tool to retrieve relevant DSM-5 information"""
    name = "retrieve_dsm5_info"
    description = "Retrieves relevant information from DSM-5 knowledge base"
    args_schema = RetrieveDSM5InfoInput
    
    def __init__(self, vector_store):
        super().__init__()
        self.vector_store = vector_store
    
    def _run(self, query: str, context_details: List[str]) -> str:
        """Retrieve DSM-5 information"""
        
        # Enhance query with context
        enhanced_query = query
        if context_details:
            enhanced_query += " " + " ".join(context_details)
        
        # Retrieve relevant documents
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        relevant_docs = retriever.get_relevant_documents(enhanced_query)
        
        # Format the retrieved information
        context_info = []
        for i, doc in enumerate(relevant_docs):
            context_info.append({
                "content": doc.page_content[:500],  # Limit length
                "metadata": doc.metadata,
                "relevance_rank": i + 1
            })
        
        return json.dumps({
            "retrieved_documents": context_info,
            "total_sources": len(relevant_docs),
            "search_query": enhanced_query
        })