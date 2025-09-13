import streamlit as st
from rag_chatbot import DSM5Chatbot
import os

# Page config
st.set_page_config(
    page_title="DSM-5 RAG Chatbot",
    page_icon="🧠",
    layout="wide"
)

# Initialize chatbot
@st.cache_resource
def init_chatbot():
    return DSM5Chatbot()

def main():
    st.title("🧠 DSM-5 RAG Chatbot")
    st.markdown("Ask questions about mental health diagnoses based on DSM-5 content.")
    
    # Sidebar for document management
    with st.sidebar:
        st.header("Document Management")
        
        st.info("💡 **Setup Instructions:**\n\n1. Run `python populate_database.py` first to load DSM-5 content\n2. Then use this chatbot interface")
        
        if st.button("🔄 Load DSM-5 from Archive.org"):
            with st.spinner("Downloading and processing DSM-5... This may take several minutes..."):
                try:
                    chatbot = init_chatbot()
                    chatbot.add_documents()
                    st.success("✅ DSM-5 content loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading DSM-5: {str(e)}")
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Or upload additional documents", 
            type=['pdf', 'txt'],
            help="Upload PDF or text files with additional content"
        )
        
        if uploaded_file and st.button("Process Uploaded Document"):
            with st.spinner("Processing document..."):
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Add to vector store
                chatbot = init_chatbot()
                chatbot.add_documents(temp_path)
                
                # Clean up
                os.remove(temp_path)
                st.success("Document processed and added to knowledge base!")
    
    # Main chat interface
    chatbot = init_chatbot()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about DSM-5 diagnoses..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question..."):
                # Use session ID for conversation continuity
                session_id = "streamlit_session"
                response = chatbot.chat(prompt, session_id)
                
                answer = response["answer"]
                sources = response["sources"]
                needs_more_info = response.get("needs_more_info", False)
                assessment = response.get("assessment", "")
                action_taken = response.get("action_taken", "")
                
                # Show status indicators based on assessment
                if assessment == "ASK_CLARIFYING":
                    st.info("🤔 I need to understand your situation better before providing information. Let me ask some clarifying questions.")
                elif assessment in ["PROVIDE_INFO", "PROVIDE_CAUTIOUS"]:
                    st.warning("⚠️ Remember: This is educational information only. Please consult a qualified mental health professional for proper evaluation and diagnosis.")
                
                st.markdown(answer)
                
                # Show sources if available and not just asking clarifying questions
                if sources and not needs_more_info:
                    with st.expander("📚 DSM-5 Sources"):
                        for i, source in enumerate(sources[:3]):  # Show top 3 sources
                            st.markdown(f"**Source {i+1}:**")
                            st.markdown(source.page_content[:300] + "...")
                            if hasattr(source, 'metadata') and 'page' in source.metadata:
                                st.markdown(f"*Page: {source.metadata['page']}*")
                            st.markdown("---")
                
                # Show conversation progress
                summary = chatbot.get_conversation_summary(session_id)
                
                with st.expander("💬 Conversation Analysis"):
                    st.write(f"**Assessment:** {assessment}")
                    st.write(f"**Action Taken:** {action_taken}")
                    st.write(f"**Messages exchanged:** {summary['total_messages']}")
                    st.write(f"**User messages:** {summary['user_messages']}")
                    st.write(f"**Symptom mentions:** {summary['symptom_mentions']}")
                    
                    if not summary['has_enough_context'] and assessment == "ASK_CLARIFYING":
                        st.info("💡 Providing more details about symptoms, their duration, and impact will help me give you more relevant information.")
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": answer})
    
    # Clear chat button
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        chatbot.clear_memory("streamlit_session")
        st.rerun()

if __name__ == "__main__":
    main()