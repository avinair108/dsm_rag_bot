"""
Test the clarifying questions feature of the DSM-5 chatbot
"""
from rag_chatbot import DSM5Chatbot
import os
from dotenv import load_dotenv

load_dotenv()

def test_clarifying_questions():
    """Test the chatbot's clarifying questions functionality"""
    
    if not all([os.getenv("OPENAI_API_KEY"), os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")]):
        print("❌ Missing environment variables. Check your .env file.")
        return
    
    print("🤖 Testing DSM-5 Chatbot Clarifying Questions...")
    
    try:
        chatbot = DSM5Chatbot()
        
        # Test scenarios
        scenarios = [
            {
                "name": "Initial diagnostic request (should ask clarifying questions)",
                "messages": ["Do I have depression?"]
            },
            {
                "name": "Providing more context (should ask follow-up questions)",
                "messages": [
                    "Do I have depression?",
                    "I've been feeling sad for a few weeks and have trouble sleeping"
                ]
            },
            {
                "name": "Detailed context (should provide educational info)",
                "messages": [
                    "Do I have depression?",
                    "I've been feeling sad for a few weeks and have trouble sleeping",
                    "I've also lost interest in things I used to enjoy and feel worthless",
                    "These symptoms have been going on for about 2 months and affect my work"
                ]
            },
            {
                "name": "General information request (should provide direct info)",
                "messages": ["What are the symptoms of ADHD according to DSM-5?"]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"🧪 Testing: {scenario['name']}")
            print('='*60)
            
            # Clear chatbot memory for each scenario
            chatbot.clear_memory()
            
            for i, message in enumerate(scenario['messages']):
                print(f"\n👤 User: {message}")
                
                response = chatbot.chat(message)
                answer = response["answer"]
                is_diagnostic = response.get("is_diagnostic_request", False)
                needs_more_info = response.get("needs_more_info", False)
                
                print(f"🤖 Bot: {answer[:300]}...")
                
                # Show status
                if is_diagnostic and needs_more_info:
                    print("📋 Status: Asking clarifying questions")
                elif is_diagnostic:
                    print("📋 Status: Providing educational information")
                else:
                    print("📋 Status: General information")
                
                print(f"📊 Sources found: {len(response['sources'])}")
                
                # Show conversation summary
                summary = chatbot.get_conversation_summary()
                print(f"💬 Context gathered: {len(summary['mentioned_symptoms'])} details")
        
        print(f"\n🎉 Clarifying questions test completed!")
        
    except Exception as e:
        print(f"❌ Error testing chatbot: {e}")

if __name__ == "__main__":
    test_clarifying_questions()