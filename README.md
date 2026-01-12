# Vector Search 

This project demonstrates a **simple and production-ready vector search implementation** using **MongoDB Atlas Vector Search** and **Sentence Transformers**, implemented entirely in **one Python file**.

The script:

* Generates embeddings
* Stores them in MongoDB
* Performs semantic similarity search using `$vectorSearch`
* Reads all configuration from environment variables

---

## Architecture Overview

```
┌──────────────────────────┐
│  Input Text              │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ SentenceTransformer      │
│ (Text → Embedding)       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ MongoDB Collection       │
│ { text, embedding }      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ MongoDB Atlas             │
│ Vector Search Index       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ $vectorSearch Pipeline   │
│ (Cosine similarity)      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Ranked Search Results    │
└──────────────────────────┘
```

---

## File Structure

There is **only one file**:

```
mongo_vector_search.py
```

No additional configuration files or modules are required.

---

## Requirements

* Python **3.9+**
* MongoDB Atlas cluster (free tier works)
* MongoDB Atlas **Vector Search index**
* Internet access to download embedding model

---

## Dependencies

Install dependencies before running:

```bash
pip install pymongo sentence-transformers
```

---

## Environment Variables

All configuration is read from environment variables.

### Required

```bash
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net"
```

### Optional (with defaults)

```bash
export MONGODB_DB="vector_db"
export MONGODB_COLLECTION="documents"
export MONGODB_VECTOR_INDEX="vector_index"
```

---

## MongoDB Vector Index Setup

Create a **Vector Search index** in MongoDB Atlas for the collection.

### Index Configuration Example

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

* **Index name** must match `MONGODB_VECTOR_INDEX`
* **Dimensions (384)** must match the embedding model

---

## How It Works

### 1. Embedding Generation

The script uses:

```
sentence-transformers/all-MiniLM-L6-v2
```

* Output dimension: **384**
* Converts text into dense vectors

---

### 2. Data Storage

Each document stored in MongoDB looks like:

```json
{
  "text": "MongoDB is a NoSQL database",
  "embedding": [0.0123, -0.9812, ...]
}
```

---

### 3. Vector Search

The script uses MongoDB’s `$vectorSearch` aggregation stage:

```python
{
  "$vectorSearch": {
    "index": "vector_index",
    "queryVector": query_embedding,
    "path": "embedding",
    "numCandidates": 100,
    "limit": 3
  }
}
```

Results are ranked by **cosine similarity**.

---

## How to Run

1. Set environment variables
2. Run the script:

```bash
python mongo_vector_search.py
```

3. The script will:

   * Insert sample documents if the collection is empty
   * Enter an interactive query loop

---

## Example Usage

### Input

```
Query (type 'exit' to quit): database for vector search
```

### Output

```
Results:

1. Score: 0.9123
   Text: MongoDB is a NoSQL database

2. Score: 0.6431
   Text: Vector search enables semantic similarity
```

---

## Troubleshooting

### `MONGODB_URI environment variable not set`

Ensure the environment variable is defined before running the script.

---

### No results returned

* Verify the vector index exists
* Ensure `numDimensions` matches the embedding size (384)
* Confirm documents contain the `embedding` field

---

### Slow search performance

* Increase `numCandidates`
* Ensure Atlas cluster is not paused
* Use a higher tier cluster if needed

---

### Duplicate documents

The script inserts sample data **only if the collection is empty**.
Clear the collection if you want to reinsert samples.

---

## Limitations

* Requires MongoDB Atlas (not local MongoDB)
* Single-vector field per document
* No chunking for large documents
* No hybrid text + vector search

---

## Possible Extensions

* FastAPI wrapper
* RAG pipeline
* Hybrid search (text + vector)
* Document chunking
* Async MongoDB client
* Replace embedding model

---

## Summary

This project provides a **minimal, clean, and correct reference implementation** of:

* Vector embeddings
* MongoDB Atlas Vector Search
* Environment-based configuration
* Single-file Python architecture

It is suitable for **learning, prototyping, and backend services**, and can be easily extended into production systems.

