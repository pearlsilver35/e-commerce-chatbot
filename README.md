# E-commerce Customer Support Chatbot

A modern, agent-based customer support chatbot built with Python, Streamlit, and LLM technology.

## Features

- **Agent-Based Architecture**: Specialized agents handle different types of customer queries
- **Multiple LLM Support**: Seamlessly switch between OpenAI and Google Gemini models
- **Conversation History**: Persistent chat history with ChromaDB vector storage
- **Modern UI**: Clean, responsive interface built with Streamlit

## Quick Setup

### Prerequisites

- Python 3.8+ (for local development)
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- Google API key (optional, for Gemini model)


### Docker Deployment

1. **Build the application**:
   ```bash
   docker-compose up --build -d
   ```
2. **Run tests**:
   ```bash
   docker-compose run test
   ```

3. **After the first build**, if you want to start the application without rebuilding, you can simply run:
   ```bash
   docker-compose up app
   ```

4. **To stop the application**, use:
   ```bash
   docker-compose down
   ```

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/pearlsilver35/e-commerce-chatbot.git
cd e-commerce-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.0-flash
DEFAULT_MODEL=openai
TEMPERATURE=0.7
```

5. Start the application:
```bash
streamlit run src/app.py
```

2. Access the application at http://localhost:8501

## Documentation

For detailed documentation about the architecture, development, and contribution guidelines, please see [DOCUMENTATION.md](DOCUMENTATION.md).

## Contact

For questions or support, contact ayodeleabigailofficial@gmail.com