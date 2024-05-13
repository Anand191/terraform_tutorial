import re

import dspy
import typer
from loguru import logger
from typing_extensions import Annotated

from ai_assistant.crawler.web_crawler import parse_wiki
from ai_assistant.generator import init_gemini_pro
from ai_assistant.generator.optimized_qa import load_dataset, optimize_generator
from ai_assistant.generator.qa import wiki_assistant
from ai_assistant.retriever.vdb_index import index_webpage
from ai_assistant.utils.db_utils import collection_cache

app = typer.Typer()


def store_webpage(
    url: str,
    collection: str,
    db_location: str,
) -> None:
    parsed_url = parse_wiki(url)
    index_webpage(parsed_url, url, collection, db_location)


def initialize_generator(
    collection: str, db_location: str, temp: float = 0.2, optimize: bool = False
) -> dspy.Module:
    # Init LM in DSPy
    init_gemini_pro(temperature=temp)
    cot_assistant = wiki_assistant(
        retriver_collection=collection, database_loc=db_location
    )
    if optimize:
        logger.info("Using optimized CoT agent")
        # Get trainset and optimize base module
        trainset, _ = load_dataset()
        cot_assistant = optimize_generator(cot_assistant, trainset)
    return cot_assistant


@app.command()
def chat(
    url: Annotated[
        str,
        typer.Argument(
            help="URL of wikipedia page for the Q/A Assistant",
            rich_help_panel="Arguments",
        ),
    ] = "https://en.wikipedia.org/wiki/Go_(game)",
    update: Annotated[
        bool,
        typer.Option(
            help="Whether to update the index for this url", rich_help_panel="Options"
        ),
    ] = False,
    optimize: Annotated[
        bool,
        typer.Option(
            help="Whether to use optimized CoT agent or not", rich_help_panel="Options"
        ),
    ] = False,
):
    URL_LOCAL = url.split("/")[-1]
    URL_LOCAL = re.sub(r"\W+", "", URL_LOCAL)
    CHROMA_COLLECTION_NAME = f"wiki_{URL_LOCAL}"
    CHROMADB_DIR = "../db/"
    conn = collection_cache()

    # Check if data from this wiki page already indexed or if update is enabled
    # If not following steps:
    # 1) Crawl data from wiki page
    # 2) Index to vector db collection
    # 3) Cache indexing infor to redis
    logger.info("Check if data from this wiki page already indexed")
    if not conn.check(url) or update:
        logger.info(f"(re)indexing data from {url}")
        store_webpage(url, CHROMA_COLLECTION_NAME, CHROMADB_DIR)

    # Init Generator
    assistant = initialize_generator(
        CHROMA_COLLECTION_NAME, CHROMADB_DIR, optimize=optimize
    )
    logger.info(
        f"""
        Begin asking questions based on the wiki page about {URL_LOCAL}.
        Hit enter to send question. Type 'exit' to end chat session.
        """
    )
    while True:
        # Accept user input
        message = typer.prompt("Question ")

        # Get assistant response
        if message.lower() == "exit":
            logger.info("Ending the chat session")
            break

        response = assistant(message)
        print(f"Assistant: {response}")
        print()


if __name__ == "__main__":
    app()
