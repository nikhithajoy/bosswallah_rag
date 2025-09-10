# Boss Wallah RAG Chatbot

A sophisticated RAG (Retrieval-Augmented Generation) based AI chatbot that acts as a support agent for Boss Wallah courses. The chatbot uses semantic search to find relevant courses and Google Gemini 2.5 Flash to generate contextual responses.

## 🚀 Features

- **Complete RAG Pipeline**: Implements all RAG components - data ingestion, embedding, retrieval, and generation
- **Semantic Search**: Uses sentence transformers and FAISS for accurate course retrieval
- **Multilingual Support**: Responds in Hindi, Tamil, Telugu, Kannada, Malayalam, and English
- **Google Gemini Integration**: Uses Gemini 2.5 Flash for high-quality response generation
- **Interactive UI**: Streamlit-based web interface for easy interaction
- **Comprehensive Testing**: Handles all required test cases including bonus tasks

## 📁 Project Structure

```
bosswallah_rag/
│
├── app.py
├── config.py
├── .env
├── data/
│   ├── bw_courses - Sheet1.csv
│   └── chroma_db/
│
├── core/
│   └── pipeline.py
│
├── src/
│   ├── rag/
│   │   ├── llm_setup.py
│   │   └── query_processor.py
│   ├── utils/
│   │   └── constants.py
│   ├── search/
│   │   └── google_search_service.py
│   ├── data_processing/
│   │   ├── data_loader.py
│   │   └── vectordb_creator.py
│   └── translation/
│       ├── language_detector.py
│       └── translator.py
│
├── ui/
│   ├── components/
│   │   ├── chat_interface.py
│   │   └── sidebar.py
│
└── test_search.py
```

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/boss-wallah-rag-chatbot.git
cd boss-wallah-rag-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 5. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 6. Download Dataset

Download the Boss Wallah courses dataset CSV file and place it in the `data/` directory as `courses.csv`.

## 🚀 Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Chatbot

1. **Upload Dataset**: Upload the Boss Wallah courses CSV file
2. **Enter API Key**: Provide your Google Gemini API key
3. **Start Chatting**: Use the test questions or ask your own questions

## 🧪 Test Cases

The chatbot handles all required test cases:

### Standard Questions
1. **"Tell me about honey bee farming course"**
2. **"I want to learn how to start a poultry farm"**
3. **"Do you have any courses in Tamil?"**
4. **"I am a recent high school graduate, are there any opportunities for me?"**

### Bonus Questions
1. **"How many cows do I need to start a dairy farm?" (in Hindi/Tamil/Telugu/Kannada/Malayalam)**
2. **"Are there any stores near Whitefield, Bangalore where I can buy seeds for papaya farming?"**

## 🏗️ RAG Architecture

### 1. Data Ingestion (`data_loader.py`)
- Loads and preprocesses the course dataset
- Handles language code mapping (6→Hindi, 20→Tamil, etc.)
- Creates searchable text combining all course fields

### 2. Embedding & Indexing (`vector_store.py`)
- Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings
- Implements FAISS for efficient vector similarity search
- Supports different index types (flat, IVF, HNSW)

### 3. Retrieval System
- Semantic search using cosine similarity
- Configurable similarity threshold and top-k results
- Returns relevant courses with similarity scores

### 4. Generation (`llm_handler.py`)
- Integrates Google Gemini 2.5 Flash model
- Context-aware prompt engineering
- Multilingual response generation
- Safety settings and error handling

## 💡 Key Components

### VectorStore Class
```python
# Create embeddings and build FAISS index
vector_store = VectorStore()
embeddings = vector_store.create_embeddings(texts)
vector_store.build_index(index_type='flat')

# Semantic search
results = vector_store.search(query, top_k=5)
```

### RAG Pipeline
```python
# 1. Retrieve relevant courses
relevant_courses = rag_system.retrieve_relevant_courses(query)

# 2. Generate contextual response
response = rag_system.generate_response(query, relevant_courses)
```

### Multilingual Support
```python
# Handle multilingual queries
response = rag_system.handle_multilingual_query(query, target_language='Hindi')
```

## 🌐 Multilingual Capabilities

The chatbot supports:
- **Hindi (हिंदी)**: Code 6
- **Kannada (ಕನ್ನಡ)**: Code 7
- **Malayalam (മലയാളം)**: Code 11
- **Tamil (தமிழ்)**: Code 20
- **Telugu (తెలుగు)**: Code 21
- **English**: Code 24

## 📊 Performance Optimizations

- **FAISS Indexing**: Fast similarity search with normalized embeddings
- **Batch Processing**: Efficient embedding creation
- **Caching**: Session state management in Streamlit
- **Memory Management**: Optimized data structures

## 🔧 Configuration Options

### Embedding Model
```python
# Change embedding model
vector_store = VectorStore(model_name='sentence-transformers/paraphrase-MiniLM-L6-v2')
```

### Search Parameters
```python
# Adjust retrieval parameters
results = vector_store.search(
    query=query,
    top_k=10,
    score_threshold=0.4
)
```

### LLM Configuration
```python
# Customize Gemini settings
generation_config = {
    'temperature': 0.7,
    'top_p': 0.8,
    'max_output_tokens': 1024
}
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: GEMINI_API_KEY is required
   ```
   Solution: Set your Google Gemini API key in environment variables

2. **Module Import Error**
   ```
   ModuleNotFoundError: No module named 'sentence_transformers'
   ```
   Solution: Install requirements: `pip install -r requirements.txt`

3. **FAISS Installation Issues**
   ```
   pip install faiss-cpu  # For CPU version
   pip install faiss-gpu  # For GPU version (if CUDA available)
   ```

4. **Dataset Loading Error**
   ```
   FileNotFoundError: courses.csv
   ```
   Solution: Ensure the CSV file is in the correct location

## 📈 Future Enhancements

- [ ] Add more advanced retrieval techniques (hybrid search)
- [ ] Implement conversation memory
- [ ] Add more Indian languages
- [