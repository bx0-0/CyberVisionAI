from celery import shared_task
from concurrent.futures import ThreadPoolExecutor
import os
from tqdm import tqdm
from RAGManger.RAGHelperFunc import process_page,process_and_store_embeddings
import fitz
import redis
from .models import UserNotification

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@shared_task
def process_pdf(file_name,file_path, user_id, chunk_size=50):
    """
    This function processes a PDF file into smaller chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        print(f"Processing file: {file_path} for user: {user_id}")
        doc = fitz.open(file_path)
        num_pages = doc.page_count
        all_chunks = []

        # Process each page in parallel
        for start_page in range(0, num_pages, chunk_size):
            end_page = min(start_page + chunk_size, num_pages)
            print(f"Processing pages {start_page+1} to {end_page}")

            # Use ThreadPoolExecutor to process the pages in parallel
            with ThreadPoolExecutor() as executor:
                results = list(tqdm(
                    executor.map(process_page, [(file_path, page_num) for page_num in range(start_page, end_page)]),
                    total=end_page - start_page
                ))

            for result in results:
                all_chunks.extend(result)

        # Add the file name to each chunk
        embedding_input= {f"Chunk {i+1}": f"[{file_name}] {chunk}" for i, chunk in enumerate(all_chunks)}
        process_and_store_embeddings(user_id=user_id,embedding_input=embedding_input)
        message = f"Great Job! X Training Completed for {file_name}."
        UserNotification.objects.create(user_id=user_id, message=message)
        redis_client.publish(f"user_{user_id}", message)


    except Exception as e:
        print(f"Error processing PDF: {e}")
        message = f"Bad Job! X Training Failed for {file_name} Try Again."
        UserNotification.objects.create(user_id=user_id, message=message)
        redis_client.publish(f"user_{user_id}", message)
    
         

        