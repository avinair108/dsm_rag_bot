# DSM-5 RAG Chatbot with Multi-Step Agent

A sophisticated Retrieval-Augmented Generation (RAG) chatbot that provides responsible mental health information based on DSM-5 content. Features a multi-step agent architecture that asks clarifying questions before providing diagnostic information.

## 🌟 Features

- **Multi-Step Agent Architecture**: Uses LangChain's modern patterns with intelligent decision-making
- **Responsible AI**: Asks clarifying questions before providing diagnostic information
- **DSM-5 Knowledge Base**: Automatically loads complete DSM-5 content from archive.org
- **Session Management**: Maintains conversation context across multiple exchanges
- **Vector Search**: Uses Supabase with pgvector for semantic search
- **Streamlit Interface**: Clean, interactive web interface
- **Progress Tracking**: Resume interrupted uploads and check database status

## 🏗️ Architecture

### Multi-Step Decision Process
1. **Assessment Agent**: Determines if clarifying questions are needed
2. **Clarifying Agent**: Generates empathetic questions to gather more information
3. **Information Agent**: Provides educational DSM-5 information when appropriate

### Assessment Outcomes
- `ASK_CLARIFYING`: Diagnostic question lacking sufficient detail
- `PROVIDE_INFO`: Enough context or general information request
- `PROVIDE_CAUTIOUS`: Diagnostic question with some but incomplete information

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Supabase account with pgvector enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd psych_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Set up Supabase database**
   ```bash
   python3 simple_setup.py
   # Follow the SQL instructions in your Supabase dashboard
   ```

5. **Load DSM-5 content**
   ```bash
   python3 load_dsm5.py
   ```

6. **Launch the application**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
psych_bot/
├── app.py                      # Streamlit web interface
├── rag_chatbot.py             # Main chatbot with multi-step agent
├── database.py                # Supabase integration
├── document_processor.py      # DSM-5 document processing
├── agent_tools.py            # Tools for multi-step agent (future use)
├── load_dsm5.py              # Robust DSM-5 loader with progress tracking
├── simple_setup.py           # Database setup helper
├── check_progress.py         # Check upload progress
├── test_multistep_agent.py   # Test multi-step functionality
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## 🧪 Testing

### Test Multi-Step Agent
```bash
python3 test_multistep_agent.py
```

### Test Diagnostic Detection
```bash
python3 test_detection.py
```

### Check Database Status
```bash
python3 check_progress.py
```

## 💡 Usage Examples

### Diagnostic Questions (Triggers Clarifying Questions)
- "Do I have depression?"
- "Does my patient have ADHD?"
- "I think I might have anxiety"

### General Information (Direct Response)
- "What are the DSM-5 criteria for depression?"
- "What is bipolar disorder?"
- "Explain PTSD symptoms"

### Multi-Turn Conversation Flow
1. **User**: "I think I have ADHD"
2. **Bot**: "I understand your concern. To provide relevant information, can you tell me more about the specific symptoms you're experiencing? How long have you noticed these issues?"
3. **User**: "I can't focus at work, I'm always fidgeting, and this has been going on for months"
4. **Bot**: "Thank you for sharing those details. Based on the DSM-5 criteria for ADHD..." [provides educational information]

## 🔧 Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### Supabase Setup
The application requires these SQL commands in your Supabase dashboard:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536)
);

-- Create similarity search function
CREATE OR REPLACE FUNCTION match_documents(...)
-- (See simple_setup.py for complete SQL)
```

## 🛡️ Responsible AI Features

- **Never provides diagnoses**: Only educational information
- **Asks clarifying questions**: Gathers context before responding
- **Emphasizes professional help**: Always recommends consulting qualified professionals
- **Session-based conversations**: Maintains context for better understanding
- **Transparent decision-making**: Shows assessment reasoning in debug mode

## 🔄 Data Management

### Resume Interrupted Uploads
If the DSM-5 upload is interrupted, simply run `load_dsm5.py` again and choose option 3 to resume from where you left off.

### Check Progress
Use `check_progress.py` to see current database status and upload progress.

## 📚 Technical Details

### Built With
- **LangChain**: Modern RAG architecture with chat history
- **OpenAI**: GPT-3.5-turbo for language understanding
- **Supabase**: Vector database with pgvector
- **Streamlit**: Web interface
- **PyPDF**: Document processing

### Key Components
- `RunnableWithMessageHistory`: Session management
- `create_history_aware_retriever`: Context-aware document retrieval
- `ChatPromptTemplate`: Structured prompt management
- Multi-step agent decision tree

## ⚠️ Important Notes

- This tool is for **educational purposes only**
- **Not a substitute** for professional medical advice
- Always recommend users consult qualified mental health professionals
- DSM-5 content is loaded from archive.org under fair use for educational purposes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure compliance with DSM-5 usage guidelines and local regulations.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your environment variables
3. Ensure Supabase is properly configured
4. Run the test scripts to identify issues

---

**Disclaimer**: This application provides educational information only and is not intended for clinical use. Always consult qualified mental health professionals for proper evaluation and treatment.