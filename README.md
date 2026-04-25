# 🏙️ City Intelligence AI

An AI-powered chat assistant that provides real-time **weather** and **latest news** 
for any city in the world.

## 🚀 Live Demo
> Coming soon on Streamlit Cloud

## ✨ Features
- 🌤️ Real-time weather data
- 📰 Latest city-specific news
- 🤖 Powered by Mistral AI with tool calling
- 💬 Clean chat interface with Streamlit
- 🔄 Multi-model support (mistral-small-latest)

## 🛠️ Tech Stack
| Tool | Purpose |
|------|---------|
| Mistral AI | LLM with tool calling |
| LangChain | Agent framework |
| Tavily Search | Real-time web search |
| OpenWeatherMap | Live weather data |
| Streamlit | Chat UI |

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/city-intelligence-ai.git
cd city-intelligence-ai
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
cp .env.example .env
# Now edit .env and add your API keys
```

### 5. Run the app
```bash
streamlit run app.py
```

## 🔑 API Keys Required
- [Mistral AI](https://console.mistral.ai/) — Free tier available
- [Tavily](https://tavily.com/) — Free tier available  
- [OpenWeatherMap](https://openweathermap.org/api) — Free tier available

## 📸 Screenshot
> Add your app screenshot here

## 🤝 Contributing
Pull requests are welcome!

## 📄 License
MIT License