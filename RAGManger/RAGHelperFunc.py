import fitz  
import pdfplumber
import re
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
import lancedb
import numpy as np
import ollama
from RAGManger.lancedb_utils import create_table_if_not_exists

def is_index_section(text):
    """
    This function checks if the given text is a section of an index.
    """
    return bool(re.search(r'(\.\s*){5,}', text))

def load_page_text(file_path, page_num):
    """
    This function loads the text of a specific page from a PDF file.
    """
    doc = fitz.open(file_path)
    page = doc.load_page(page_num)  
    text = page.get_text()
    doc.close()
    return text

def extract_tables_from_page(file_path, page_num):
    """
    This function extracts all tables from a specific page of a PDF file if it exists.
    """
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[page_num]  
        tables = page.extract_tables() 
        return tables

def remove_table_text_from_page_text(page_text, tables):
    """
    This function removes the text of all tables from a specific page of a PDF file to get clean text."""
    for table in tables:
        for row in table:
            for cell in row:
                if cell:  
                    cell_pattern = re.escape(cell.strip())
                    page_text = re.sub(cell_pattern, '', page_text, flags=re.IGNORECASE)
    return page_text

def clean_text(text):
    """
    This function cleans the text by removing extra spaces and dots.
    """
    
    text = re.sub(r'\.{3,}', ' ', text)  
    text = re.sub(r'\s+', ' ', text).strip() 
    return text

def table_to_text(table):
    """
    This function converts a table to a string of text.
    """
    table_text = ""
    for row in table:
        row_text = " | ".join([cell.strip() if cell else "" for cell in row])
        table_text += row_text + "\n"
    return table_text.strip()

def smart_chunk_text(text, max_chunk_size=500):
    """
    This function splits the text into smaller chunks based on sentence length.
    """


    text = clean_text(text) if not is_index_section(text) else ""
    
    sentences = sent_tokenize(text)
    
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if current_length + sentence_length > max_chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk)) 
                current_chunk = []  
                current_length = 0
        
        current_chunk.append(sentence)
        current_length += sentence_length

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def process_page(args):
    """
    This function processes a specific page of a PDF file.
    """
    file_path, page_num = args
    page_text = load_page_text(file_path, page_num)
    tables = extract_tables_from_page(file_path, page_num)
    page_text_without_tables = remove_table_text_from_page_text(page_text, tables)
    text_chunks = smart_chunk_text(page_text_without_tables)

    if tables:
        for table in tables:
            table_text = table_to_text(table)
            text_chunks.append(table_text)

    return text_chunks



def process_and_store_embeddings(user_id,embedding_input):
    """
    This function process the user content and convert to  embeddding and sore it in  lancedb
    """
    def count_tokens_manual(text):
        return len(text.split()) // 5

    batch_size = 50  
    num_batches = len(embedding_input) // batch_size + (1 if len(embedding_input) % batch_size != 0 else 0)

    db = lancedb.connect("./lancedb")
    table_name = "Users_contents"
    create_table_if_not_exists(db,table_name)
    table = db.open_table(table_name)
    embedding_model = 'granite-embedding'

    for batch_idx in tqdm(range(num_batches), desc="🔄 processing the Text.."):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(embedding_input))

        batch_data = dict(list(embedding_input.items())[start:end])

        filtered_data = {k: v for k, v in batch_data.items() if count_tokens_manual(v) <= 900}
        if not filtered_data:
            continue 

        filtered_texts = list(filtered_data.values())  
        filtered_ids = list(filtered_data.keys()) 

        embeddings_data = []
        for i, text in enumerate(filtered_texts):
            try:
                response = ollama.embed(model=embedding_model, input=text)
                embedding = response['embeddings'][0]
                embeddings_data.append(
                    {
                        "user_id":user_id,
                        "text": text,
                        "vector": np.array(embedding),
                        "id": filtered_ids[i],
                    }
                )
            except Exception as e:
                print(text)


        table.add(embeddings_data)

    print(f"embedding insert into  db  for user{user_id}")