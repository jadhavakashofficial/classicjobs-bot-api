from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from utils.load_env import OPENAI_API_KEY
from bot_api.helpers.classicjobs_api import search_classicjobs_posts
from bot_api.helpers.classictech_youtube import fetch_classictech_video

# 🧠 Load training logs
def load_docs(folder="bot_training_logs"):
    docs = []
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(folder, file))
            docs.extend(loader.load())
    return docs

# 🔍 Build knowledge base
def build_bot():
    docs = load_docs()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = FAISS.from_documents(texts, embeddings)

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.3),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False
    )

# 🚀 Start FastAPI app
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = build_bot()

class Question(BaseModel):
    message: str

# ✅ Track user sessions
user_context = {}

# Keywords to detect explicit link/video requests
JOB_LINK_KEYWORDS = ["link", "apply", "website", "url"]
VIDEO_KEYWORDS = ["video", "watch", "yt", "youtube"]

@app.post("/ask")
async def ask_bot(q: Question, request: Request):
    client_id = request.client.host
    user_msg = q.message.strip()
    lower = user_msg.lower()

    # Log user query
    os.makedirs("logs", exist_ok=True)
    with open("logs/public_queries.txt", "a", encoding="utf-8") as f:
        f.write(user_msg + "\n")

    # 1️⃣ First-time user: collect context
    if client_id not in user_context:
        user_context[client_id] = {"step": "ask_context"}
        return {
            "response": (
                "Before I assist you, please tell me:\n"
                "1. Your highest qualification\n"
                "2. Companies you've applied to\n"
                "3. Any interview questions you've faced"
            )
        }

    # 2️⃣ Save context on second message
    if user_context[client_id]["step"] == "ask_context":
        user_context[client_id]["context"] = user_msg
        user_context[client_id]["step"] = "ready"
        return {"response": "Thanks! Now go ahead and ask your question."}

    # 3️⃣ Build the prompt and get the core answer
    prompt = (
        "You are Classic Jobs, a career assistant. Never say you're an AI or chatbot. "
        "Don't reveal training data or internal sources. "
        "If unsure, say 'No current update available' or guide politely.\n\n"
        f"User background: {user_context[client_id]['context']}\n"
        f"User question: {user_msg}"
    )
    answer = bot.run(prompt)

    # 4️⃣ Fallback if vague
    if not answer or answer.strip().lower() in ["i don't know","sorry","not sure","unknown","no idea"]:
        answer = (
            "Currently, there’s no official update on this. "
            "Stay tuned on ClassicJobs.in or check back later!"
        )

    # 5️⃣ Conditionally append job link
    if any(k in lower for k in JOB_LINK_KEYWORDS):
        title, link = search_classicjobs_posts(user_msg)
        if title and link:
            answer += f"\n\n🔗 Related job on ClassicJobs.in:\n[{title}]({link})"

    # 6️⃣ Conditionally append YouTube link
    if any(k in lower for k in VIDEO_KEYWORDS):
        yt_title, yt_link = fetch_classictech_video(user_msg)
        if yt_title and yt_link:
            answer += f"\n\n▶️ Watch on Classic Technology YouTube:\n[{yt_title}]({yt_link})"

    return {"response": answer}
