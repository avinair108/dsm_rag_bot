"""
Robust DSM-5 loader with better error handling and progress tracking
"""
import os
import requests
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

def download_dsm5_with_progress():
    """Download DSM-5 with progress tracking"""
    url = "https://dn790004.ca.archive.org/0/items/APA-DSM-5/DSM5.pdf"
    
    print("📥 Downloading DSM-5 PDF...")
    
    # Use longer timeout and stream download
    response = requests.get(url, stream=True, timeout=300)  # 5 minute timeout
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r📥 Downloaded: {percent:.1f}%", end="", flush=True)
        
        print(f"\n✅ Download complete! File size: {downloaded / (1024*1024):.1f} MB")
        return temp_file.name

def process_dsm5_pdf(pdf_path):
    """Process PDF into chunks"""
    print("📄 Loading PDF...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    print(f"📚 Loaded {len(documents)} pages")
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    print("✂️ Splitting into chunks...")
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "source": "DSM-5",
            "source_url": "https://dn790004.ca.archive.org/0/items/APA-DSM-5/DSM5.pdf",
            "chunk_id": i,
            "document_type": "diagnostic_manual"
        })
    
    print(f"📦 Created {len(chunks)} chunks")
    return chunks

def upload_to_supabase(chunks, batch_size=10):
    """Upload chunks to Supabase in batches"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    client = create_client(supabase_url, supabase_key)
    embeddings = OpenAIEmbeddings()
    
    vector_store = SupabaseVectorStore(
        client=client,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents"
    )
    
    print(f"🚀 Uploading {len(chunks)} chunks to Supabase...")
    
    # Upload in batches to avoid timeouts
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            vector_store.add_documents(batch)
            print(f"✅ Uploaded batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
            time.sleep(1)  # Small delay between batches
        except Exception as e:
            print(f"❌ Error uploading batch {i//batch_size + 1}: {e}")
            continue
    
    print("🎉 Upload complete!")

def main():
    try:
        # Check environment variables
        if not all([os.getenv("OPENAI_API_KEY"), os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")]):
            print("❌ Missing environment variables. Check your .env file.")
            return
        
        # Download DSM-5
        pdf_path = download_dsm5_with_progress()
        
        try:
            # Process PDF
            chunks = process_dsm5_pdf(pdf_path)
            
            # Upload to Supabase
            upload_to_supabase(chunks)
            
        finally:
            # Clean up
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
                print("🧹 Cleaned up temporary files")
        
        print("\n🎯 DSM-5 RAG chatbot is ready!")
        print("🚀 Run: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()