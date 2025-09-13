"""
Script to populate the Supabase database with DSM-5 content from archive.org
Run this once to load all DSM-5 content into your vector database.
"""

from rag_chatbot import DSM5Chatbot
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # Check if environment variables are set
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return
    
    print("Initializing DSM-5 RAG Chatbot...")
    chatbot = DSM5Chatbot()
    
    print("Loading DSM-5 from archive.org and populating database...")
    print("This may take several minutes...")
    
    try:
        # Load DSM-5 from URL and add to vector store
        chatbot.add_documents()
        print("✅ Successfully populated database with DSM-5 content!")
        print("You can now run the chatbot with: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        print("Make sure your Supabase database is properly set up and pgvector is enabled")

if __name__ == "__main__":
    main()