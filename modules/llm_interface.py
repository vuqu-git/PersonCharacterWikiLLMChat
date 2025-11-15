"""Module for interfacing with IBM watsonx.ai LLMs."""

import logging
from pathlib import Path
import config
# -----------------------
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
