"""Configuration settings for the Icebreaker Bot."""
import os

from dotenv import load_dotenv

# general remark in environ var. for deployment
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# set all configuration values that are loaded with os.getenv or from .env file (e.g. in the Render dashboard)
# for your current config.py, it is: PPLX_API_KEY


# Centralize environment loading
# !!! entire config.py is called/imported from parent folder (by app_wiki.py) !!!
ENV_PATH = os.path.join(os.path.dirname(__file__), 'modules', '.env')
load_dotenv(dotenv_path=ENV_PATH) # local dev: looks for your local .env file and loads those values into environment variables

# Perplexity API key loading
PPLX_API_KEY = os.getenv("PPLX_API_KEY") # every time os.getenv("PPLX_API_KEY") is called, it fetches the value from the OS environment—set by either .env (locally), or by e.g. Render (in deployment)

# Optional: Add validation
if not PPLX_API_KEY:
    raise ValueError("PPLX_API_KEY must be set in .env file")

# Mock data URL
MOCK_DATA_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/ZRe59Y_NJyn3hZgnF1iFYA/linkedin-profile-data.json"

# MOCK_DATA_URL = "./linkedin-profile-data.json" # !!! Important Caveat: the actual location depends on where the script is run from, not necessarily where config.py is located
# Instead of using relative paths, use paths relative to the config.py file location
# CONFIG_DIR = os.path.dirname(os.path.abspath(__file__)) # Get the directory where config.py is located
# MOCK_DATA_URL = os.path.join(CONFIG_DIR, "linkedin-profile-data.json") # Now point to files relative to config.py location

# Query settings
SIMILARITY_TOP_K = 5    # Determines how many similar chunks to retrieve when answering queries. Increasing this could give more comprehensive but potentially noisier responses.

TEMPERATURE = 0.0
MAX_NEW_TOKENS = 500
TOP_P = 1
#MIN_NEW_TOKENS = 1
#TOP_K = 50

# Node settings
CHUNK_SIZE = 500    # Controls how large each text chunk is when splitting the LinkedIn data. If you want more granular retrieval, you could reduce this (e.g., to 300).

# LLM prompt templates
INITIAL_FACTS_TEMPLATE = """
You are an AI assistant that provides detailed answers based on the provided context.

Context information is below:
{context_str}

Based on the context provided, list 3 interesting facts about this person's life.

Answer in detail, using only the information provided in the context.
"""

USER_QUESTION_TEMPLATE = """
You are an AI assistant that provides detailed answers to questions based on the provided context.

Context information is below:
{context_str}

Question: {query_str}

Answer in full details, using only the information provided in the context. If the answer is not available in the context, say "I don't know. The information is not available on the provided material."
"""