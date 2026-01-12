import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# =========================
# LOAD CONFIG FROM ENVS
# =========================
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "vector_db")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "documents")
VECTOR_INDEX_NAME = os.getenv("MONGODB_VECTOR_INDEX", "vector_index")

if not MONGO_URI:
    raise ValueError("MONGODB_URI environment variable not set")

# =========================
# CONNECT TO MONGODB
# =========================
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# =========================
# LOAD EMBEDDING MODEL
# =========================
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

VECTOR_DIMENSION = model.get_sentence_embedding_dimension()

# =========================
# EMBEDDING UTILS
# =========================
def embed_text(text: str) -> list:
    return model.encode(text).tolist()

# =========================
# DATA INSERTION
# =========================
def insert_documents(texts: list[str]):
    documents = []
    for text in texts:
        documents.append({
            "text": text,
            "embedding": embed_text(text)
        })

    if documents:
        collection.insert_many(documents)
        print(f"Inserted {len(documents)} documents")

# =========================
# VECTOR SEARCH
# =========================
def vector_search(query: str, top_k: int = 3):
    query_vector = embed_text(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "queryVector": query_vector,
                "path": "embedding",
                "numCandidates": 100,
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    return list(collection.aggregate(pipeline))

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("Connected to MongoDB")
    print(f"Database: {DB_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Vector Index: {VECTOR_INDEX_NAME}")
    print(f"Embedding Dimension: {VECTOR_DIMENSION}\n")

    # Insert sample documents if collection is empty
    if collection.count_documents({}) == 0:
        sample_texts = [
            "Python is a popular programming language",
            "MongoDB is a NoSQL database",
            "Vector search enables semantic similarity",
            "Embeddings convert text into vectors",
            "FastAPI is used to build APIs"
        ]
        insert_documents(sample_texts)

    # Interactive query loop
    while True:
        query = input("Query (type 'exit' to quit): ").strip()

        if query.lower() in {"exit", "quit"}:
            break

        results = vector_search(query)

        if not results:
            print("No results found\n")
            continue

        print("\nResults:\n")
        for i, res in enumerate(results, 1):
            print(f"{i}. Score: {res['score']:.4f}")
            print(f"   Text: {res['text']}\n")
