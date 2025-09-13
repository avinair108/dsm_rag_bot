"""
Simple setup script that creates a basic table structure for Supabase
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_supabase():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return
    
    print("🔧 Setting up Supabase for DSM-5 RAG chatbot...")
    
    print("\n📋 Please run the following SQL commands in your Supabase SQL Editor:")
    print("=" * 60)
    
    sql_commands = """
-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536)
);

-- 3. Create RLS policies (optional, for security)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 4. Create a policy to allow all operations (adjust as needed)
CREATE POLICY "Allow all operations on documents" ON documents
FOR ALL USING (true);

-- 5. Create index for faster similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 6. Create function for similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 10
)
RETURNS TABLE(
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE documents.embedding IS NOT NULL
    AND 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;
"""
    
    print(sql_commands)
    print("=" * 60)
    print("\n✅ After running the SQL commands above, your database will be ready!")
    print("🚀 Then run: python3 populate_database.py")

if __name__ == "__main__":
    setup_supabase()