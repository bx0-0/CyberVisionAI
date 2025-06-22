from django.test import TestCase

# Create your tests here.
import lancedb
import numpy as np
import ollama

#  embedding  model
def search_in_RAG_db(user_id,query):
    embedding_model = 'granite-embedding'

    db = lancedb.connect("./lancedb")
    table = db.open_table("Users_contents")

    # query_embedding = np.array(ollama.embed(model=embedding_model, input=query)['embeddings'][0])

    # results = table.search(query_embedding).where(f"user_id='{user_id}'") \
    #           .limit(10) \
    #           .to_pandas()
              

    # for i, row in results.iterrows():
    #     print(f" {i+1}: {row['text']}\n🔹 Similarity score: {row['_distance']:.4f}\n")
    #     print("-"*50)
    stored_data = table.count_rows()
    print(f"📦 عدد العناصر المخزنة في ChromaDB: {stored_data}")


search_in_RAG_db(1,'who  is CEO?')