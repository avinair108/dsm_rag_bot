"""
Quick test for diagnostic detection
"""
from rag_chatbot import DSM5Chatbot
import os
from dotenv import load_dotenv

load_dotenv()

def test_detection():
    """Test diagnostic detection with various phrases"""
    
    if not all([os.getenv("OPENAI_API_KEY"), os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")]):
        print("❌ Missing environment variables")
        return
    
    chatbot = DSM5Chatbot()
    
    test_phrases = [
        "if my patient had depression",
        "does my patient have depression", 
        "do I have depression",
        "what are the symptoms of depression",
        "my client shows signs of anxiety",
        "patient exhibits depressive symptoms",
        "these symptoms suggest ADHD",
        "what is depression"
    ]
    
    print("🧪 Testing diagnostic detection:")
    print("="*50)
    
    for phrase in test_phrases:
        is_diagnostic = chatbot._is_diagnostic_request(phrase)
        print(f"'{phrase}' -> {'✅ DIAGNOSTIC' if is_diagnostic else '❌ NOT DIAGNOSTIC'}")
    
    print("\n🧪 Testing full chat response:")
    print("="*50)
    
    response = chatbot.chat("if my patient had depression")
    print(f"Response type: {'Clarifying questions' if response.get('needs_more_info') else 'Direct info'}")
    print(f"Answer preview: {response['answer'][:100]}...")

if __name__ == "__main__":
    test_detection()