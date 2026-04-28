import os
import requests
import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

load_dotenv()

st.set_page_config(page_title="City Intelligence AI", page_icon="🏙️", layout="centered")

st.markdown("""
<style>
.block-container {
    max-width: 850px;
    padding-top: 1.2rem;
}
[data-testid="stChatInput"] {
    border-radius: 16px;
}
.hero {
    text-align: center;
    padding: 0.5rem 0 1rem 0;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-subtitle {
    text-align: center;
    font-size: 1rem;
    color: #8a8a8a;
    margin-top: 0.3rem;
    margin-bottom: 1rem;
}
</style>

<div class="hero">
    <h1 class="hero-title">City Intelligence</h1>
    <div class="hero-subtitle">Ask about weather, news, and city insights</div>
</div>
""", unsafe_allow_html=True)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def get_weather(city: str) -> str:
    """Get current weather of a city"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY is missing."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
    except Exception as e:
        return f"Error fetching weather: {e}"

    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message', 'Could not fetch weather')}"

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"Weather in {city}: {desc}, {temp}°C"

from datetime import datetime

@tool
def get_news(place: str) -> str:
    """Get latest relevant news for a specific city"""
    try:
        results = tavily_client.search(
            query=f'"{place}" news OR events OR update',  # quoted for exact match
            search_depth="advanced",
            max_results=7,
            # Remove topic="news" — it biases toward global trending news
            # Remove time_range="day" — too restrictive, forces trending results
        )
    except Exception as e:
        return f"Error fetching news: {e}"

    if not results or "results" not in results or len(results["results"]) == 0:
        return f"No recent news found for {place}"

    # Filter results to only include articles that mention the place
    place_keywords = [kw.lower() for kw in place.replace(",", "").split()]
    
    filtered = []
    for article in results["results"]:
        title = article.get("title", "")
        content = article.get("content", "") or article.get("snippet", "")
        combined = (title + " " + content).lower()
        
        # Keep article only if at least one keyword from place name appears
        if any(kw in combined for kw in place_keywords):
            filtered.append(article)

    if not filtered:
        return f"No locally relevant news found for {place}. Try a larger nearby city."

    news_list = []
    for i, article in enumerate(filtered[:5], 1):
        title = article.get("title", "No Title")
        summary = article.get("content") or article.get("snippet") or "No summary available"
        url = article.get("url", "")
        news_list.append(
            f"### {i}. {title}\n"
            f"{summary[:200]}...\n"
            f"[Read more]({url})"
        )

    return f"## 📰 Latest News in {place}\n\n" + "\n\n".join(news_list)
tools = {
    "get_weather": get_weather,
    "get_news": get_news
}

def make_llm(model_name):
    llm = ChatMistralAI(model=model_name)
    return llm.bind_tools([get_weather, get_news])

def run_agent(chat_messages, llm_with_tools):
    lc_messages = []
    for m in chat_messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            lc_messages.append(AIMessage(content=m["content"]))

    while True:
        ai_msg = llm_with_tools.invoke(lc_messages)

        # No tool calls → we're done, return the final answer
        if not getattr(ai_msg, "tool_calls", None):
            return ai_msg.content

        # Append the AI message directly (with tool calls)
        lc_messages.append(ai_msg)

        # Execute each tool and append its result
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            tool_result = tools[tool_name].invoke(tool_args)
            lc_messages.append(
                ToolMessage(content=tool_result, tool_call_id=tool_call["id"])
            )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I’m City Intelligence. Ask me about any city."}
    ]

with st.sidebar:
    st.subheader("Controls")
    selected_model = st.selectbox(
        "Choose model",
        ["mistral-small-latest", "mistral-small-3.1"],
        index=0
    )
    st.caption("Recommended: mistral-small-latest")
    if st.button("Clear chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I’m City Intelligence. Ask me about any city."}
        ]
        st.rerun()

llm_with_tools = make_llm(selected_model)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about any city..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(st.session_state.messages, llm_with_tools)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
