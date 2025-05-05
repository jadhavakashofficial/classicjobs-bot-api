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

# ✅ User session data
user_context = {}

@app.post("/ask")
async def ask_bot(q: Question, request: Request):
    client_id = request.client.host

    # Save query log
    os.makedirs("logs", exist_ok=True)
    with open("logs/public_queries.txt", "a", encoding="utf-8") as f:
        f.write(q.message.strip() + "\n")

    # First-time user: ask for background
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

    # Second message: save background
    if user_context[client_id]["step"] == "ask_context":
        user_context[client_id]["context"] = q.message.strip()
        user_context[client_id]["step"] = "ready"
        return {"response": "Thanks! Now go ahead and ask your question."}

    # User already gave context: now answer
    full_prompt = f"User background: {user_context[client_id]['context']}\nQuestion: {q.message}"
    answer = bot.run(full_prompt)

    return {"response": answer}
