"""Module for querying indexed LinkedIn profile data."""

import logging
from typing import Any, Dict, Optional

from llama_index.core import VectorStoreIndex, PromptTemplate

from modules.llm_interface import create_perplexity_llm
import config

logger = logging.getLogger(__name__)


# What is a Query Engine?
# In the context of our RAG (Retrieval-Augmented Generation) system, a query engine is responsible for:
#     Retrieving relevant information from our vector index based on a query
#     Formatting the retrieved information into a prompt for the LLM
#     Generating coherent and accurate responses based on the retrieved context
#     => query engine that combines the index with the LLM and prompt, and then execute a query to generate


def generate_initial_facts(index: VectorStoreIndex) -> str:
    """Generates interesting facts about the person's career or education.

    Args:
        index: VectorStoreIndex containing the LinkedIn profile data.

    Returns:
        String containing interesting facts about the person.
    """
    try:
        # Create Perplexity LLM for generating facts
        perplexity_llm = create_perplexity_llm(
            temperature=0.0,
            max_new_tokens=500
        )

        # Create prompt template
        facts_prompt = PromptTemplate(template=config.INITIAL_FACTS_TEMPLATE)

        # Create query engine
        query_engine = index.as_query_engine(
            streaming=False,  # Wait for the full response rather than streaming it
            similarity_top_k=config.SIMILARITY_TOP_K,  # Retrieve the most relevant chunks from the profile
            llm=perplexity_llm,
            text_qa_template=facts_prompt
        )

        # Execute the query
        query = "Provide three interesting facts about this person's career or education."
        response = query_engine.query(query)

        # Return the facts
        return response.response
    except Exception as e:
        logger.error(f"Error in generate_initial_facts: {e}")
        return "Failed to generate initial facts."

# def generate_initial_facts(index: VectorStoreIndex) -> str:
#     """Generates interesting facts about the person\'s career or education.
#
#     Args:
#         index: VectorStoreIndex containing the LinkedIn profile data.
#
#     Returns:
#         String containing interesting facts about the person.
#     """
#     try:
#
#         pplx_api_key = os.getenv("PPLX_API_KEY")
#
#         # Create LLM for generating facts
#         watsonx_llm = create_watsonx_llm(
#             temperature=0.0,
#             max_new_tokens=500,
#             decoding_method="sample"
#         )
#
#         # Create prompt template
#         facts_prompt = PromptTemplate(template=config.INITIAL_FACTS_TEMPLATE)
#
#         # Create query engine
#         query_engine = index.as_query_engine(
#             streaming=False, # Wait for the full response rather than streaming it
#             similarity_top_k=config.SIMILARITY_TOP_K, #Retrieve the most relevant chunks from the profile
#             llm=watsonx_llm,
#             text_qa_template=facts_prompt
#         )
#
#         # Execute the query
#         query = "Provide three interesting facts about this person\'s career or education."
#         response = query_engine.query(query)
#
#         # Return the facts
#         return response.response
#     except Exception as e:
#         logger.error(f"Error in generate_initial_facts: {e}")
#         return "Failed to generate initial facts."


def answer_user_query(index: VectorStoreIndex, user_query: str) -> Any:
    """Answers the user's question using the vector database and the LLM.

    Args:
        index: VectorStoreIndex containing the LinkedIn profile data.
        user_query: The user's question.

    Returns:
        Response object containing the answer to the user's question.
    """
    try:
        # Create Perplexity LLM for answering questions
        perplexity_llm = create_perplexity_llm(
            temperature=0.0,
            max_new_tokens=250  # Keeps answers concise
        )

        # Create prompt template
        question_prompt = PromptTemplate(template=config.USER_QUESTION_TEMPLATE)

        # Retrieve relevant nodes
        base_retriever = index.as_retriever(similarity_top_k=config.SIMILARITY_TOP_K)
        source_nodes = base_retriever.retrieve(user_query)

        # Build context string
        context_str = "\n\n".join([node.node.get_text() for node in source_nodes])

        # Create query engine
        query_engine = index.as_query_engine(
            streaming=False,
            similarity_top_k=config.SIMILARITY_TOP_K,
            llm=perplexity_llm,
            text_qa_template=question_prompt
        )

        # Execute the query
        answer = query_engine.query(user_query)
        return answer
    except Exception as e:
        logger.error(f"Error in answer_user_query: {e}")
        return "Failed to get an answer."


# def answer_user_query(index: VectorStoreIndex, user_query: str) -> Any:
#     """Answers the user's question using the vector database and the LLM.
#
#     Args:
#         index: VectorStoreIndex containing the LinkedIn profile data.
#         user_query: The user's question.
#
#     Returns:
#         Response object containing the answer to the user's question.
#     """
#     try:
#         # Create LLM for answering questions
#         watsonx_llm = create_watsonx_llm(
#             temperature=0.0,
#             max_new_tokens=250, # Keeps answers concise
#             decoding_method="greedy" # Always selects the most likely next token for maximum accuracy
#         )
#
#         # Create prompt template
#         question_prompt = PromptTemplate(template=config.USER_QUESTION_TEMPLATE)
#
#         # Retrieve relevant nodes
#         base_retriever = index.as_retriever(similarity_top_k=config.SIMILARITY_TOP_K)
#         source_nodes = base_retriever.retrieve(user_query)
#
#         # Build context string
#         context_str = "\n\n".join([node.node.get_text() for node in source_nodes])
#
#         # Create query engine
#         query_engine = index.as_query_engine(
#             streaming=False,
#             similarity_top_k=config.SIMILARITY_TOP_K,
#             llm=watsonx_llm,
#             text_qa_template=question_prompt
#         )
#
#         # Execute the query
#         answer = query_engine.query(user_query)
#         return answer
#     except Exception as e:
#         logger.error(f"Error in answer_user_query: {e}")
#         return "Failed to get an answer."