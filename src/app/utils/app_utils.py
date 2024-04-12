import torch
from langchain import PromptTemplate
from qdrant_client import QdrantClient
from langchain.chains import RetrievalQA
from langchain import HuggingFacePipeline
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import SentenceTransformerEmbeddings
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, GenerationConfig, pipeline

def get_llm(CONFIG):
    MODEL_NAME = CONFIG["model"]["model_name"]

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=CONFIG["model"]["quantization_config"]["load_in_4bit"],
        bnb_4bit_compute_dtype=torch.float64,
        bnb_4bit_quant_type=CONFIG["model"]["quantization_config"]["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=CONFIG["model"]["quantization_config"]["bnb_4bit_use_double_quant"],
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, 
        torch_dtype=torch.float16,
        trust_remote_code=CONFIG["model"]["config"]["trust_remote_code"],
        device_map=CONFIG["model"]["config"]["device_map"],
        quantization_config=quantization_config
    )

    generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    generation_config.max_new_tokens = CONFIG["model"]["max_new_tokens"]
    generation_config.temperature = CONFIG["model"]["temperature"]
    generation_config.top_p = CONFIG["model"]["top_p"]
    generation_config.do_sample = CONFIG["model"]["do_sample"]
    generation_config.repetition_penalty = CONFIG["model"]["repetition_penalty"]

    pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=True,
        generation_config=generation_config,
    )

    return HuggingFacePipeline(pipeline=pipeline)


def get_prompt_template(CONFIG):
    return PromptTemplate(template=CONFIG["prompt"]["prompt_template"], input_variables=CONFIG["prompt"]["input_variable"])

def create_retriever(CONFIG):
    client = QdrantClient(url=CONFIG["qdrant"]["url"], prefer_grpc=False)
    embeddings = SentenceTransformerEmbeddings(model_name=CONFIG["qdrant"]["embeddings_model_name"])
    db = Qdrant(client=client, embeddings=embeddings,collection_name=CONFIG["qdrant"]["collection_name"])
    return db.as_retriever(search_kwargs=CONFIG["qdrant"]["search_kwargs"])

def response_generator(prompt: str, llm, retriever, prompt_template):
    chain_type_kwargs = {"prompt": prompt_template}
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True, chain_type_kwargs=chain_type_kwargs, verbose=True)
    response = qa(prompt)
    answer = response['result']
    logger.info(response['source_documents'][0].page_content)
    logger.info(response['source_documents'][0].metadata['source'])

    for word in answer.split():
        yield word + " "
        time.sleep(0.05)