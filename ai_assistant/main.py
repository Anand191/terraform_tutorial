import re

from loguru import logger

from ai_assistant.generator import init_gemini_pro
from ai_assistant.generator.qa import wiki_assistant

URL = "https://en.wikipedia.org/wiki/Go_(game)"
URL_LOCAL = URL.split("/")[-1]
URL_LOCAL = re.sub(r"\W+", "", URL_LOCAL)
CHROMA_COLLECTION_NAME = f"wiki_{URL_LOCAL}"
CHROMADB_DIR = "../db/"

logger.info("Type a question")
QUESTION = input()
logger.info(f"Question: {QUESTION}")

if __name__ == "__main__":
    init_gemini_pro(temperature=0.2)
    cot_assistant = wiki_assistant()
    response = cot_assistant(QUESTION, CHROMA_COLLECTION_NAME, CHROMADB_DIR)
    logger.info(f"The answer of the RAG agent is: \n {response.answer}")
