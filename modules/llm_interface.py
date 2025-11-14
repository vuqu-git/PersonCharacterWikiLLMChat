"""Module for interfacing with IBM watsonx.ai LLMs."""

import logging

from pathlib import Path
from typing import Dict, Any, Optional


# from llama_index.embeddings.ibm import WatsonxEmbeddings
# from llama_index.llms.ibm import WatsonxLLM
# from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

import config
######################################################

import os
from llama_index.llms.perplexity import Perplexity
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

logger = logging.getLogger(__name__)


def create_perplexity_embedding() -> HuggingFaceEmbedding:
    """Creates a HuggingFace embedding model for vector representation.

    Uses the 'BAAI/bge-small-en-v1.5' model which is:
    - Open-source and free
    - High quality (comparable to paid APIs)
    - Lightweight and fast
    - Works locally without external API keys

    Returns:
        HuggingFaceEmbedding model for vector representation.
    """
    # Initialize HuggingFace embedding model
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        cache_folder=".cache/embeddings"
    )

    logger.info("Created HuggingFace Embedding model: BAAI/bge-small-en-v1.5")
    return embed_model


def create_perplexity_llm(
        temperature: float = config.TEMPERATURE,
        max_new_tokens: int = config.MAX_NEW_TOKENS
) -> Perplexity:
    """Creates a Perplexity LLM (Sonar model) for generating responses.

    Args:
        temperature: Temperature for controlling randomness in generation (0.0 to 1.0).
        max_new_tokens: Maximum number of new tokens to generate.

    Returns:
        Perplexity LLM model with web search disabled.
    """
    # Load .env file from the modules directory
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # Retrieve API key
    pplx_api_key = os.getenv("PPLX_API_KEY")

    if not pplx_api_key:
        raise ValueError("PPLX_API_KEY not found in .env file!")

    # Create Perplexity LLM with sonar model and web search disabled
    additional_params = {
        "disable_search": True,
        "top_p": config.TOP_P,
    }

    perplexity_llm = Perplexity(
        api_key=pplx_api_key,
        model="sonar",
        temperature=temperature,
        max_tokens=max_new_tokens,
        # disable_search=True,  # Turn off web search completely => doesn't work
        additional_kwargs=additional_params,
    )

    # # Set disable_search as an attribute to ensure it's passed to API => doesn't work
    # perplexity_llm.disable_search = True

    logger.info("Created Perplexity LLM model: sonar (web search disabled)")
    return perplexity_llm


##################################

# def create_watsonx_embedding() -> WatsonxEmbeddings:
#     """Creates an IBM Watsonx Embedding model for vector representation.
#
#     Returns:
#         WatsonxEmbeddings model.
#     """
#     watsonx_embedding = WatsonxEmbeddings(
#         model_id=config.EMBEDDING_MODEL_ID,
#         url=config.WATSONX_URL,
#         project_id=config.WATSONX_PROJECT_ID,
#         truncate_input_tokens=3,
#     )
#     logger.info(f"Created Watsonx Embedding model: {config.EMBEDDING_MODEL_ID}")
#     return watsonx_embedding
#
# def create_watsonx_llm(
#     temperature: float = config.TEMPERATURE,
#     max_new_tokens: int = config.MAX_NEW_TOKENS,
#     decoding_method: str = "sample"
# ) -> WatsonxLLM:
#     """Creates an IBM Watsonx LLM for generating responses.
#
#     Args:
#         temperature: Temperature for controlling randomness in generation (0.0 to 1.0).
#         max_new_tokens: Maximum number of new tokens to generate.
#         decoding_method: Decoding method to use (sample, greedy).
#
#     Returns:
#         WatsonxLLM model.
#     """
#     additional_params = {
#         "decoding_method": decoding_method,
#         "min_new_tokens": config.MIN_NEW_TOKENS,
#         "top_k": config.TOP_K,
#         "top_p": config.TOP_P,
#     }
#
#     watsonx_llm = WatsonxLLM(
#         model_id=config.LLM_MODEL_ID,
#         url=config.WATSONX_URL,
#         project_id=config.WATSONX_PROJECT_ID,
#         temperature=temperature,
#         max_new_tokens=max_new_tokens,
#         additional_params=additional_params,
#     )
#
#     logger.info(f"Created Watsonx LLM model: {config.LLM_MODEL_ID}")
#     return watsonx_llm

# def change_llm_model(new_model_id: str) -> None:
#     """Change the LLM model to use.
#
#     Args:
#         new_model_id: New LLM model ID to use.
#     """
#     global config
#     config.LLM_MODEL_ID = new_model_id
#     logger.info(f"Changed LLM model to: {new_model_id}")