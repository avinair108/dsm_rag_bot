"""
Run this script to set up your Supabase database for the DSM-5 RAG chatbot.
Make sure you have the pgvector extension enabled in your Supabase project.
"""

from database import SupabaseDB

def main():
    print("Setting up Supabase database for DSM-5 RAG chatbot...")
    
    db = SupabaseDB()
    db.create_tables()
    
    print("\nSetup instructions:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Enable pgvector extension by running: CREATE EXTENSION IF NOT EXISTS vector;")
    print("4. Run the SQL commands printed above to create tables and functions")
    print("5. Your database will be ready for the RAG chatbot!")

if __name__ == "__main__":
    main()