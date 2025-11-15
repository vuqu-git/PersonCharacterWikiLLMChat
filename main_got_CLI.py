"""Main script for running the Game of Thrones Wiki Bot."""

import sys
import time
import logging
import argparse

from modules.data_extraction import extract_got_profile
from modules.data_processing import split_got_profile_data, create_vector_database, verify_embeddings
from modules.query_engine import generate_initial_facts, answer_user_query


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def process_got_wiki(wiki_url, mock=True):
    """
    Processes a Game of Thrones wiki URL, extracts character data, and interacts with the user.

    Args:
        wiki_url: The Fandom wiki URL to scrape or load mock data from.
        mock: If True, loads mock data from a saved HTML file instead of web scraping.
    """
    try:
        # Extract the wiki page data
        profile_data = extract_got_profile(wiki_url, mock=mock)

        if not profile_data:
            logger.error("Failed to retrieve wiki data.")
            return

        # Split the data into nodes using wiki-specific splitter
        nodes = split_got_profile_data(profile_data)

        if not nodes:
            logger.error("Failed to process wiki data into nodes.")
            return

        # Store in vector database
        vectordb_index = create_vector_database(nodes)

        if not vectordb_index:
            logger.error("Failed to create vector database.")
            return

        # Verify embeddings
        if not verify_embeddings(vectordb_index):
            logger.warning("Some embeddings may be missing or invalid.")

        # Generate and display the initial facts
        initial_facts = generate_initial_facts(vectordb_index)

        print("\nHere are 3 interesting facts about this character:")
        print(initial_facts)

        # Start the chatbot interface
        chatbot_interface(vectordb_index)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")


def chatbot_interface(index):
    """
    Provides a simple chatbot interface for user interaction.

    Args:
        index: VectorStoreIndex containing the Game of Thrones character data.
    """
    print("\nYou can now ask more questions about this character. Type 'exit', 'quit', or 'bye' to quit.")

    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Bot: Goodbye!")
            break

        print("Bot is typing...", end='')
        sys.stdout.flush()
        time.sleep(1)  # Simulate typing delay
        print('\r', end='')

        response = answer_user_query(index, user_query)
        print(f"Bot: {response.response.strip()}\n")


def main():
    """Main function to run the Game of Thrones Wiki Bot."""
    parser = argparse.ArgumentParser(description='Game of Thrones Wiki Bot - Character Analyzer')
    parser.add_argument(
        '--url',
        type=str,
        help='Fandom wiki URL (e.g., https://gameofthrones.fandom.com/wiki/Rhaenyra_Targaryen)'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock data from saved HTML file instead of web scraping'
    )

    args = parser.parse_args()

    # Use command line arguments or prompt user for input
    wiki_url = args.url or input("Enter Game of Thrones wiki URL (or press Enter to use mock data): ")
    use_mock = args.mock or not wiki_url

    # Use a default URL for mock data if none provided
    if use_mock and not wiki_url:
        wiki_url = "https://gameofthrones.fandom.com/wiki/Rhaenyra_Targaryen"

    process_got_wiki(wiki_url, mock=use_mock)


if __name__ == "__main__":
    main()


## To test our CLI application, we can run it with various combinations of arguments:
# 1. With a Game of Thrones wiki URL:
# python main_got_CLI.py --url https://gameofthrones.fandom.com/wiki/Jon_Snow

# 2. With mock data:
# python main_got_CLI.py --mock

# 3. Interactive mode (will prompt for URL):
# python main_got_CLI.py
