import lancedb
import pyarrow as pa
import lancedb
import numpy as np
import ollama

def connect_to_lancedb(db_path="./lancedb"):
    return lancedb.connect(db_path)

# Create a table with schema
def create_table_if_not_exists(db, table_name, embedding_dim=384):
    if table_name not in db.table_names():
        schema = pa.schema([
            pa.field("user_id", pa.string()), 
            pa.field("text", pa.string()),  #  documents
            pa.field("vector", pa.list_(pa.float32(), embedding_dim)),  #  embeddings
            pa.field("id", pa.string()),  #  IDs
        
        ])
        db.create_table(table_name, schema=schema)
        print(f"✅Table {table_name} created")
    else:
        print(f"table already exist {table_name}")


def search_in_RAG_db(user_id, query, number_data_retrieval):
    embedding_model = 'granite-embedding'
    db = connect_to_lancedb("./lancedb")
    table = db.open_table("Users_contents")
    
    query_embedding = np.array(ollama.embed(model=embedding_model, input=query)['embeddings'][0])
    
    results = table.search(query_embedding).where(f"user_id='{user_id}'").limit(number_data_retrieval).to_pandas()
    
    if results.empty:
        return {"status": "no_content", "message": "No content found for this user."}
    
    result = ''
    for i, row in results.iterrows():
        result += f"{i+1}: {row['text']}\n🔹 Similarity score: {row['_distance']:.4f}\n\n"
    
    return {"status": "success", "result": result}