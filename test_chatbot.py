"""
Simple test script for the DSM-5 chatbot
"""
from rag_chatbot import DSM5Chatbot
import os
from dotenv import load_dotenv

load_dotenv()

def test_chatbot():
    """Test the chatbot functionality"""
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return
    
    print("🤖 Initializing DSM-5 Chatbot...")
    
    try:
        chatbot = DSM5Chatbot()
        print("✅ Chatbot initialized successfully!")
        
        # Test questions
        test_questions = [
            "What is depression according to DSM-5?",
            "What are the criteria for ADHD?",
            "Tell me about anxiety disorders"
        ]
        
        print("\n🧪 Testing chatbot with sample questions...")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- Test {i} ---")
            print(f"Q: {question}")
            
            response = chatbot.chat(question)
            answer = response["answer"]
            sources = response["sources"]
            
            print(f"A: {answer[:200]}...")
            print(f"Sources found: {len(sources)}")
            
            if "Error:" in answer:
                print("❌ Error in response")
            else:
                print("✅ Response generated successfully")
        
        print("\n🎉 Chatbot test completed!")
        
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        print("💡 Make sure you've uploaded DSM-5 content to Supabase")

if __name__ == "__main__":
    test_chatbot()