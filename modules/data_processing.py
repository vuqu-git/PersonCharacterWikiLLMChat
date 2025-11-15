"""Module for processing LinkedIn profile data."""

import json
import logging
from typing import Dict, List, Any, Optional

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from modules.llm_interface import create_perplexity_embedding
import config

logger = logging.getLogger(__name__)

def split_profile_data(profile_data: Dict[str, Any]) -> List:
    # result of extract_linkedin_profile call is of type: Dict[str, Any]
    """Splits the LinkedIn profile JSON data into nodes.

    Args:
        profile_data: LinkedIn profile data dictionary.

    Returns:
        List of document nodes.
    """
    try:
        # Converts a Python dictionary into a JSON-formatted string
        # The string format makes it easier to split, chunk, or embed the profile data into document nodes for further processing.
        profile_json = json.dumps(profile_data)     # JSON-formatted string (str type) representation of that dictionary
        # profile_json = '{"name": "John Doe", "age": 30, "skills": ["Python", "Java"], "is_active": true}'
        # Create a Document object from the JSON string
        document = Document(text=profile_json)
        # Split the document into nodes using SentenceSplitter
        splitter = SentenceSplitter(chunk_size=config.CHUNK_SIZE)
        # in LlamaIndex chunks are called nodes
        nodes = splitter.get_nodes_from_documents([document])

        logger.info(f"Created {len(nodes)} nodes from profile data")
        return nodes
    except Exception as e:
        logger.error(f"Error in split_profile_data: {e}")
        return []


def split_got_profile_data(profile_data: Dict[str, Any]) -> List:
    """Splits the wiki data into nodes with section metadata.

    Args:
        profile_data: Wiki profile data dictionary with 'sections' and optional 'infobox'.

    Returns:
        List of document nodes with metadata.
    """
    try:
        nodes = []

        # Create metadata for the character
        base_metadata = {
            "character_name": profile_data.get("name", "Unknown"),
            "source_url": profile_data.get("url", ""),
            "source_type": "game_of_thrones_wiki"
        }

        # Add infobox information as a separate node if available
        if "infobox" in profile_data:
            infobox_text = json.dumps(profile_data["infobox"], indent=2)
            infobox_doc = Document(
                text=f"Character Information:\n{infobox_text}",
                metadata={**base_metadata, "section": "Infobox"}
            )
            nodes.append(infobox_doc)

        # Process each section separately to maintain semantic boundaries
        if "sections" in profile_data:
            for section_name, section_content in profile_data["sections"].items():
                # Skip empty sections
                if not section_content or len(section_content) < 50:
                    continue

                # Create document with section-specific metadata
                section_metadata = {
                    **base_metadata,
                    "section": section_name
                }

                section_doc = Document(
                    text=f"Section: {section_name}\n\n{section_content}",
                    metadata=section_metadata
                )
                nodes.append(section_doc)

        # Now split each document into smaller chunks if needed
        splitter = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=50)
        final_nodes = splitter.get_nodes_from_documents(nodes)

        logger.info(f"Created {len(final_nodes)} nodes from {len(nodes)} sections")
        return final_nodes

    except Exception as e:
        logger.error(f"Error in split_got_profile_data: {e}")
        return []


def create_vector_database(nodes: List) -> Optional[VectorStoreIndex]:
    """Stores the document chunks (nodes) in a vector database.

    Args:
        nodes: List of document nodes to be indexed.

    Returns:
        VectorStoreIndex or None if indexing fails.
    """
    try:
        # Get the embedding model
        embedding_model = create_perplexity_embedding()
        # Create a VectorStoreIndex from the nodes
        index = VectorStoreIndex(
            nodes=nodes,
            embed_model=embedding_model,
            show_progress=True
        )

        logger.info("Vector database created successfully")
        return index
    except Exception as e:
        logger.error(f"Error in create_vector_database: {e}")
        return None

def verify_embeddings(index: VectorStoreIndex) -> bool:
    """Verify that all nodes have been properly embedded.

    Args:
        index: VectorStoreIndex to verify.

    Returns:
        True if all embeddings are valid, False otherwise.
    """
    try:
        vector_store = index._storage_context.vector_store
        node_ids = list(index.index_struct.nodes_dict.keys())
        missing_embeddings = False
        for node_id in node_ids:
            embedding = vector_store.get(node_id)
            if embedding is None:
                logger.warning(f"Node ID {node_id} has a None embedding.")
                missing_embeddings = True
            else:
                logger.debug(f"Node ID {node_id} has a valid embedding.")

        if missing_embeddings:
            logger.warning("Some node embeddings are missing")
            return False
        else:
            logger.info("All node embeddings are valid")
            return True
    except Exception as e:
        logger.error(f"Error in verify_embeddings: {e}")
        return False

