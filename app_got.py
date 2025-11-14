"""Gradio web interface for the Game of Thrones Wiki Bot."""

import os
import sys
import logging
import uuid
import gradio as gr

from modules.data_extraction import extract_got_profile
from modules.data_processing import split_got_profile_data, create_vector_database, verify_embeddings
from modules.query_engine import generate_initial_facts, answer_user_query
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# A dictionary to store active conversations across sessions
active_indices = {}


def process_got_profile(wiki_url: str, use_mock: bool = False):
    """Process a Game of Thrones wiki profile and generate initial facts.

    Args:
        wiki_url: Fandom wiki URL to process.
        use_mock: Whether to use mock data from a saved HTML file.

    Returns:
        Initial facts about the character and a session ID for this conversation.
    """
    try:
        # Use a default URL for mock data if none provided
        if use_mock and not wiki_url:
            wiki_url = "https://gameofthrones.fandom.com/wiki/Rhaenyra_Targaryen"

        # Extract profile data from wiki
        profile_data = extract_got_profile(wiki_url, mock=use_mock)

        if not profile_data:
            return "Failed to retrieve wiki data. Please check the URL.", None

        # Split data into nodes using wiki-specific splitter
        nodes = split_got_profile_data(profile_data)

        if not nodes:
            return "Failed to process wiki data into nodes.", None

        # Create vector database
        index = create_vector_database(nodes)

        if not index:
            return "Failed to create vector database.", None

        # Verify embeddings
        if not verify_embeddings(index):
            logger.warning("Some embeddings may be missing or invalid")

        # Generate initial facts
        facts = generate_initial_facts(index)

        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Store the index for this session
        active_indices[session_id] = index

        # Return the facts and session ID
        return f"Wiki page processed successfully!\n\nHere are 3 interesting facts about this character:\n\n{facts}", session_id

    except Exception as e:
        logger.error(f"Error in process_got_profile: {e}")
        return f"Error: {str(e)}", None


def chat_with_character(session_id, user_query, chat_history):
    """Chat about a processed Game of Thrones character.

    Args:
        session_id: Session ID for this conversation.
        user_query: User's question.
        chat_history: Chat history.

    Returns:
        Updated chat history.
    """
    if not session_id:
        return chat_history + [[user_query, "No character loaded. Please process a wiki page first."]]

    if session_id not in active_indices:
        return chat_history + [[user_query, "Session expired. Please process the wiki page again."]]

    if not user_query.strip():
        return chat_history

    try:
        # Get the index for this session
        index = active_indices[session_id]

        # Answer the user's query
        response = answer_user_query(index, user_query)

        # Update chat history
        return chat_history + [[user_query, response.response]]

    except Exception as e:
        logger.error(f"Error in chat_with_character: {e}")
        return chat_history + [[user_query, f"Error: {str(e)}"]]


def create_gradio_interface():
    """Create the Gradio interface for the Game of Thrones Wiki Bot."""

    with gr.Blocks(title="Game of Thrones Wiki Bot") as demo:
        gr.Markdown("# Game of Thrones Wiki Bot")
        gr.Markdown("Learn about Game of Thrones characters and chat about their stories")

        gr.Markdown("""
        ### How to use:
        1. Go to the **Process Wiki Page** tab
        2. Enter a Game of Thrones Fandom wiki URL or use mock data
        3. Click **Process Wiki Page** to analyze the character
        4. Go to the **Chat** tab to ask questions about the character
        ---
        """)

        with gr.Tab("Process Wiki Page"):
            with gr.Row():
                with gr.Column(scale=4):  # Give more space to the URL column
                    wiki_url = gr.Textbox(
                        label="Fandom Wiki URL",
                        placeholder="https://gameofthrones.fandom.com/wiki/Character_Name",
                        info="Enter a Game of Thrones Fandom wiki URL",
                        lines=1,
                        max_lines=1
                    )
                    use_mock = gr.Checkbox(
                        label="Use Mock Data",
                        value=True,
                        info="Load from the saved default HTML file (no web scraping)"
                    )

                    gr.Markdown("### Example URLs:")
                    gr.Markdown("""
                    - https://gameofthrones.fandom.com/wiki/Jon_Snow
                    - https://gameofthrones.fandom.com/wiki/Daenerys_Targaryen
                    """)

                    process_btn = gr.Button("Process Wiki Page", variant="primary")

                with gr.Column(scale=3):  # Results column takes less space
                    result_text = gr.Textbox(label="Initial Facts", lines=12)
                    session_id = gr.Textbox(label="Session ID", visible=False)

            process_btn.click(
                fn=process_got_profile,
                inputs=[wiki_url, use_mock],
                outputs=[result_text, session_id]
            )

        with gr.Tab("Chat"):
            gr.Markdown("Ask questions about the Game of Thrones character")

            chatbot = gr.Chatbot(
                height=500,
                placeholder="Process a wiki page first, then ask questions here!"
            )
            chat_input = gr.Textbox(
                label="Ask a question about the character",
                placeholder="What is this character's house allegiance?"
            )

            chat_btn = gr.Button("Send")

            chat_btn.click(
                fn=chat_with_character,
                inputs=[session_id, chat_input, chatbot],
                outputs=[chatbot]
            )

            chat_input.submit(
                fn=chat_with_character,
                inputs=[session_id, chat_input, chatbot],
                outputs=[chatbot]
            )

            # Clear chat button
            clear_btn = gr.Button("Clear Chat")
            clear_btn.click(lambda: [], outputs=[chatbot])

    return demo


if __name__ == "__main__":
    demo = create_gradio_interface()
    # Launch the Gradio interface
    demo.launch(
        server_name="127.0.0.1",
        server_port=5001,  # Different port from the LinkedIn app
        share=False  # Set to True to create a public link
    )
