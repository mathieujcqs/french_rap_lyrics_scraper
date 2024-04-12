from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import JSONLoader, DirectoryLoader

from src.paths import DATA_DIR
from src.utils.file_utils import get_config
from src.utils.logger import get_console_logger

logger = get_console_logger()

def main():
    """
    Main script to perform the data ingestion into the Qdrant Vector Database.
    
    The script performs the following operations:
    - Loads the embeddings.
    - Creates a document loader
    - Creates a text splittre and apply it on the data
    - Vectorizes and saves the data into the Qdrant DataBase
    
    Configuration for the script, including file paths and processing parameters, 
    is loaded from a 'main.yml' file.
    
    Returns:
        None
    """
    
    CONFIG = get_config("main.yml")
    
    embeddings = SentenceTransformerEmbeddings(model_name=CONFIG["qdrant"]["embeddings_model_name"])
    logger.info('Embeddings loaded')
    
    loader = DirectoryLoader(DATA_DIR, glob=CONFIG["qdrant"]["loader_glob"], show_progress=True, loader_cls=JSONLoader)
    documents = loader.load()
    logger.info('Loader initiated')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CONFIG["qdrant"]["chunk_size"], chunk_overlap=CONFIG["qdrant"]["chunk_overlap"])
    texts = text_splitter(documents)
    logger.info('Text split done')
    
    Qdrant.from_documents(texts, embeddings, url=CONFIG["qdrant"]["url"], prefer_grpc=False, collection_name=CONFIG["qdrant"]["collection_name"])

    logger.info("Vector Database created")
  
if __name__ == "__main__":
    main()