"""
Test the new multi-step agent approach
"""
from rag_chatbot import DSM5Chatbot
import os
from dotenv import load_dotenv

load_dotenv()

def test_multistep_agent():
    """Test the multi-step agent functionality"""
    
    if not all([os.getenv("OPENAI_API_KEY"), os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")]):
        print("❌ Missing environment variables. Check your .env file.")
        return
    
    print("🤖 Testing DSM-5 Multi-Step Agent...")
    
    try:
        chatbot = DSM5Chatbot()
        session_id = "test_session"
        
        # Test scenarios
        scenarios = [
            {
                "name": "Initial diagnostic request",
                "messages": ["Do I have depression?"]
            },
            {
                "name": "Patient diagnostic question", 
                "messages": ["If my patient had depression, what would I look for?"]
            },
            {
                "name": "General information request",
                "messages": ["What are the DSM-5 criteria for major depressive disorder?"]
            },
            {
                "name": "Multi-turn diagnostic conversation",
                "messages": [
                    "I think I might have ADHD",
                    "I have trouble focusing at work and I'm always fidgeting",
                    "This has been going on for about 6 months and it's affecting my job performance"
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"🧪 Testing: {scenario['name']}")
            print('='*60)
            
            # Clear session for each scenario
            chatbot.clear_memory(session_id)
            
            for i, message in enumerate(scenario['messages']):
                print(f"\n👤 User: {message}")
                
                response = chatbot.chat(message, session_id)
                answer = response["answer"]
                assessment = response.get("assessment", "")
                action_taken = response.get("action_taken", "")
                needs_more_info = response.get("needs_more_info", False)
                
                print(f"🤖 Bot: {answer[:200]}...")
                print(f"📊 Assessment: {assessment}")
                print(f"🎯 Action: {action_taken}")
                print(f"❓ Needs more info: {needs_more_info}")
                print(f"📚 Sources found: {len(response.get('sources', []))}")
                
                # Show conversation summary
                summary = chatbot.get_conversation_summary(session_id)
                print(f"💬 Messages: {summary['total_messages']}, Symptoms: {summary['symptom_mentions']}")
        
        print(f"\n🎉 Multi-step agent test completed!")
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multistep_agent()