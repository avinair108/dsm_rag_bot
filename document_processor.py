from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.schema import Document
from typing import List
import os
import requests
import tempfile

class DSM5Processor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.dsm5_url = "https://dn790004.ca.archive.org/0/items/APA-DSM-5/DSM5.pdf"
    
    def load_dsm5_from_url(self) -> List[Document]:
        """Load DSM-5 PDF directly from the archive.org URL"""
        print("Downloading DSM-5 PDF from archive.org...")
        
        # Download the PDF
        response = requests.get(self.dsm5_url, stream=True)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        try:
            # Load and process the PDF
            print("Processing DSM-5 PDF...")
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
            
            # Add page numbers and source info to metadata
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "source": "DSM-5",
                    "source_url": self.dsm5_url,
                    "page": i + 1,
                    "document_type": "diagnostic_manual"
                })
            
            return self.split_documents(documents)
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def load_dsm5_documents(self, file_path: str) -> List[Document]:
        """Load DSM-5 documents from file"""
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        return self.split_documents(documents)
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
    
    def add_metadata(self, documents: List[Document], source_type="dsm5") -> List[Document]:
        """Add metadata to documents"""
        for doc in documents:
            doc.metadata.update({
                "source_type": source_type,
                "document_type": "diagnostic_manual"
            })
        return documents