import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from utils.load_env import OPENAI_API_KEY

def load_public_logs(folder="bot_training_logs"):
    documents = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(folder, filename))
            documents.extend(loader.load())
    return documents

def log_public_query(question, logfile="logs/public_queries.txt"):
    os.makedirs("logs", exist_ok=True)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(question.strip() + "\n")

def build_public_bot(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = FAISS.from_documents(texts, embeddings)

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.3),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False
    )
    return qa_chain

if __name__ == "__main__":
    print("🌐 Loading public training logs...")
    docs = load_public_logs()
    print(f"📄 Loaded {len(docs)} documents.")

    print("🤖 Public bot ready. Ask your questions (type 'exit' to quit):")
    bot = build_public_bot(docs)

    while True:
        query = input("User: ")
        if query.lower() in ["exit", "quit"]:
            break
        log_public_query(query)
        response = bot.run(query)
        print("Bot:", response)
