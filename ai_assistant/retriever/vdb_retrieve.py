from chromadb.utils import embedding_functions
from dspy.retrieve.chromadb_rm import ChromadbRM


def Retrieval(collection, db_dir):
    """
    Retreives paragraphs from wiki page.
    This is just a retriever and does not have any language model.
    """
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    return ChromadbRM(collection, db_dir, default_ef, k=3)
