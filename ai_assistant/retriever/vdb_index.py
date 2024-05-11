from typing import Dict

import chromadb
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from loguru import logger
from tqdm import tqdm

from ai_assistant.utils.db_utils import collection_cache


def index_webpage(parsed: Dict, url: str, collection_name: str, db_dir: str) -> None:
    logger.info(f"Indexing wiki url to collection_name {collection_name}")
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection = chroma_client.get_or_create_collection(name=collection_name)
    text_splitter = SentenceTransformersTokenTextSplitter()
    for header, paragraphs in tqdm(parsed.items()):
        for id, text in paragraphs.items():
            # split the text into chunks and insert into chromadb
            ids = []
            documents = []
            metadatas = []
            chunks = text_splitter.create_documents([text])  # takes array of documents
            for chunk_no, chunk in enumerate(chunks):
                ids.append(f"pid_{id}#{chunk_no}")
                documents.append(chunk.page_content)
                metadatas.append({"title": header, "source": url})
            if ids:
                collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    logger.info(f"Cache collection path for {url} to redis..")
    cache = collection_cache()
    cache.set(url, collection_name)
