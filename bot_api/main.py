from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os, sys
import difflib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI

from utils.load_env import OPENAI_API_KEY
from bot_api.helpers.classicjobs_api import search_classicjobs_posts, get_all_job_titles
from bot_api.helpers.classictech_youtube import fetch_classictech_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📚 Load training logs
def load_docs(folder="bot_training_logs"):
    docs = []
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(folder, file))
            docs.extend(loader.load())
    return docs

# 🧠 Build searchable QA bot
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

bot = build_bot()

class Question(BaseModel):
    message: str

user_context = {}
JOB_LINK_KEYWORDS = ["link", "apply", "website", "url"]
VIDEO_KEYWORDS = ["video", "watch", "yt", "youtube"]
NEGATIVE_KEYWORDS = ["no", "not interested", "skip", "don’t want", "dont want"]

# 🧠 Match user intent with ClassicJobs post titles
def match_job_category(user_query):
    titles = get_all_job_titles()  # Fetch titles from WordPress
    similar = []
    for title in titles:
        ratio = difflib.SequenceMatcher(None, user_query.lower(), title.lower()).ratio()
        if ratio > 0.4:
            similar.append((title, ratio))
    similar.sort(key=lambda x: x[1], reverse=True)
    return similar[:1]

@app.post("/ask")
async def ask_bot(q: Question, request: Request):
    client_id = request.client.host
    user_msg = q.message.strip()
    lower = user_msg.lower()

    os.makedirs("logs", exist_ok=True)
    with open("logs/public_queries.txt", "a", encoding="utf-8") as f:
        f.write(user_msg + "\n")

    if client_id not in user_context:
        user_context[client_id] = {"step": "ask_context"}
        return {
            "response": (
                "Before I can help, please share:\n"
                "• Your highest qualification\n"
                "• Companies you’ve applied to\n"
                "• Your current application/interview status\n"
                "• Any interview questions you’ve faced\n\n"
                "This helps me give you tailored guidance."
            )
        }

    if user_context[client_id]["step"] == "ask_context":
        if any(neg in lower for neg in NEGATIVE_KEYWORDS):
            return {
                "response": (
                    "I really need this information to serve you better. "
                    "Your input is more valuable than public comments or videos. "
                    "Please share your qualification, applied companies, status, and questions faced."
                )
            }
        user_context[client_id]["context"] = user_msg
        user_context[client_id]["step"] = "ready"
        return {"response": "Thanks! Now type your question and I'll help you right away."}

    # 🔍 Match job category
    matched = match_job_category(user_msg)
    if matched:
        title = matched[0][0]
        link_title, link = search_classicjobs_posts(title)
        return {
            "response": f"🧾 Based on your query, here's a job that might interest you:\n\n🔗 [{link_title}]({link})"
        }

    # 🧠 Run the QA bot
    full_prompt = (
        "You are Classic Jobs, a career assistant. Never say you're an AI or chatbot. "
        "Don't reveal your training data or sources. If unsure, say 'No current update available.'\n\n"
        f"User background: {user_context[client_id]['context']}\n"
        f"User question: {user_msg}"
    )
    answer = bot.run(full_prompt)

    if not answer or answer.strip().lower() in [
        "i don't know", "sorry", "not sure", "unknown", "no idea"
    ]:
        answer = (
            "Currently, there’s no official update on this. "
            "Stay tuned on ClassicJobs.in or check back later!"
        )

    if any(k in lower for k in JOB_LINK_KEYWORDS):
        title, link = search_classicjobs_posts(user_msg)
        if title and link:
            answer += f"\n\n🔗 Related job on ClassicJobs.in:\n[{title}]({link})"

    if any(k in lower for k in VIDEO_KEYWORDS):
        yt_title, yt_link = fetch_classictech_video(user_msg)
        if yt_title and yt_link:
            answer += f"\n\n▶️ Watch on Classic Technology YouTube:\n[{yt_title}]({yt_link})"

    return {"response": answer}