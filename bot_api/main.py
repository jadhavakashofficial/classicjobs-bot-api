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

# 🔍 Build searchable knowledge base
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

# 🚀 Start FastAPI server
app = FastAPI()

# Allow public frontend access (like classicjobs.in)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = build_bot()

class Question(BaseModel):
    message: str

# 🔄 Endpoint for public questions
@app.post("/ask")
async def ask_bot(q: Question):
    os.makedirs("logs", exist_ok=True)
    with open("logs/public_queries.txt", "a", encoding="utf-8") as f:
        f.write(q.message.strip() + "\n")
    answer = bot.run(q.message)
    return {"response": answer}
