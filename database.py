import os
from supabase import create_client, Client
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class SupabaseDB:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.embeddings = OpenAIEmbeddings()
        
    def get_vector_store(self, table_name="documents"):
        return SupabaseVectorStore(
            client=self.client,
            embedding=self.embeddings,
            table_name=table_name,
            query_name="match_documents"
        )
    
    def create_tables(self):
        """Create necessary tables for storing DSM-5 documents and embeddings"""
        # This assumes you have the pgvector extension enabled in Supabase
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS dsm5_documents (
            id BIGSERIAL PRIMARY KEY,
            content TEXT,
            metadata JSONB,
            embedding VECTOR(1536)
        );
        
        CREATE OR REPLACE FUNCTION match_documents(
            query_embedding VECTOR(1536),
            match_threshold FLOAT DEFAULT 0.78,
            match_count INT DEFAULT 10
        )
        RETURNS TABLE(
            id BIGINT,
            content TEXT,
            metadata JSONB,
            similarity FLOAT
        )
        LANGUAGE SQL STABLE
        AS $$$
            SELECT
                dsm5_documents.id,
                dsm5_documents.content,
                dsm5_documents.metadata,
                1 - (dsm5_documents.embedding <=> query_embedding) AS similarity
            FROM dsm5_documents
            WHERE 1 - (dsm5_documents.embedding <=> query_embedding) > match_threshold
            ORDER BY dsm5_documents.embedding <=> query_embedding
            LIMIT match_count;
        $$;
        """
        
        try:
            # Note: Supabase client doesn't directly execute SQL
            # You'll need to run this in your Supabase SQL editor
            print("Please run the following SQL in your Supabase SQL editor:")
            print(create_table_sql)
        except Exception as e:
            print(f"Error creating tables: {e}")