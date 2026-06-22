# 1. Add documents to our collection in ChromaDB
# import chromadb

# client = chromadb.PersistentClient(path="./chroma_db")
# collection = client.get_or_create_collection(name="test")

# collection.add(
#     ids=["1"],
#     documents=["The quick brown fox jumps over the lazy dog."]
# )

# results = collection.query(query_texts=["a fast animal leaping"], n_results=1)

# print(results["documents"])

# 2. Wire it with Agno
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.google import GeminiEmbedder

knowledge = Knowledge(
    name="Book Knowledge Base",
    vector_db=ChromaDb(
        collection="book_knowledge",
        path="chroma_db",
        persistent_client=True,
        embedder=GeminiEmbedder()       # Uses GOOGLE_API_KEY from .env
    )
)

print(knowledge)