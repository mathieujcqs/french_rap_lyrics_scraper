import time
import streamlit as st

from src.utils.file_utils import get_config
from src.utils.logger import get_console_logger
from utils.app_utils import get_prompt_template, get_llm, create_retriever, response_generator

logger = get_console_logger()


def main():
    """
    Main script to launch the app.
    
    The script performs the following operations:
    - Loads the LLM, retriever and prompt template.
    - Creates the streamlit app with a chat
    - Creates a text splittre and apply it on the data
    - Vectorizes and saves the data into the Qdrant DataBase
    
    Configuration for the script, including file paths and processing parameters, 
    is loaded from a 'main.yml' file.
    
    Returns:
        No
    """
    CONFIG = get_config("main.yml")
    
    llm = get_llm(CONFIG)
    logger.info("LLM set")
    
    retriever = create_retriever(CONFIG)
    logger.info("Retriever set")
    
    prompt_template = get_prompt_template(CONFIG)
    logger.info("Prompt Template set")
    
    st.title("Ghost Writer Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(prompt, llm, retriever, prompt_template))
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
if __name__ == "__main__":
    main()