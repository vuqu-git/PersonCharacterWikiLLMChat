"""Gradio web interface for the Person and Character Wiki Bot."""

import sys
import logging
import uuid
import gradio as gr

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

# A dictionary to store active conversations across sessions
active_indices = {}


def process_got_profile(wiki_url: str, use_mock: bool = False):
    """Process a wiki profile and generate initial facts.

    Args:
        wiki_url: wiki URL to process.
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


def process_got_profile_from_file(html_file, wiki_url: str = ""):
    """Process a wiki profile from uploaded HTML file.

    Args:
        html_file: Uploaded HTML file object from Gradio.
        wiki_url: Optional URL for reference.

    Returns:
        Initial facts about the character and a session ID for this conversation.
    """
    try:
        if html_file is None:
            return "Please upload an HTML file.", None

        # Read the uploaded HTML file
        logger.info(f"Reading uploaded file: {html_file.name}")
        with open(html_file.name, "r", encoding="utf-8") as f:
            html_content = f.read()

        logger.info(f"HTML file loaded, size: {len(html_content)} characters")

        # Extract profile data from the HTML content
        profile_data = extract_got_profile(html_content=html_content)

        # Use the wiki_url (as metadata) if provided, otherwise leave blank
        if wiki_url:
            profile_data["url"] = wiki_url

        if not profile_data:
            return "Failed to parse HTML file. Please ensure it's a valid wiki page.", None

        # Split data into nodes
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

        return f"HTML file processed successfully!\n\nHere are 3 interesting facts about this character:\n\n{facts}", session_id

    except Exception as e:
        logger.error(f"Error in process_got_profile_from_file: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}", None


def chat_with_character(session_id, user_query, chat_history):
    """Chat about a (processed) person or character.

    Args:
        session_id: Session ID for this conversation.
        user_query: User's question.
        chat_history: Chat history.

    Returns:
        Updated chat history.
    """
    if not session_id:
        return chat_history + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": "No character loaded. Please process a wiki page first."}
        ]# ,                 ""
#      ↑                     ↑
#      First return value   Second return value
#      (updated chat)       (empty string)

    if session_id not in active_indices:
        return chat_history + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": "Session expired. Please process the wiki page again."}
        ]#, ""

    if not user_query.strip():
        return chat_history

    try:
        # Get the index for this session
        index = active_indices[session_id]

        # Answer the user's query
        response = answer_user_query(index, user_query)

        # Update chat history
        return chat_history + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": response.response}
        ]  # ✅ Only return chat_history (removed ", """)

    except Exception as e:
        logger.error(f"Error in chat_with_character: {e}")
        return chat_history + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": f"Error: {str(e)}"}
        ]  # ✅ Only return chat_history (removed ", """)



def create_gradio_interface():
    """Create the Gradio interface for the Person and Character Wiki Bot."""

    with gr.Blocks(title="Person and Character Wiki Bot") as demo:
        gr.Markdown("# Person and Character Wiki Bot")
        gr.Markdown("Learn about persons and character and chat about their stories")

        gr.Markdown("""
        ### How to use:
        1. Go to the **Process Wiki Page** tab
        2. Option 1: Upload a HTML file or Option 2: enter a person and character wiki URL (maybe 403 - bot/scraper protection) or use mock data
        3. Click **Process ...** to analyze the persin or character
        4. Go to the **Chat** tab to ask questions about the person or character
        ---
        """)

        with gr.Tab("Process Wiki Page"):
            # ✅ One row containing both options side-by-side
            with gr.Row():
                # Option 1: Left column
                with gr.Column(scale=1):
                    gr.Markdown("### Option 1: Upload HTML File")
                    gr.Markdown("Download a wiki page as HTML (Right-click → Save As → Webpage, Complete) and upload the HTML file here.")

                    html_file = gr.File(
                        label="Upload HTML File",
                        file_types=[".html", ".htm"],
                        file_count="single"
                    )
                    wiki_url_optional = gr.Textbox(
                        label="Wiki URL (Optional)",
                        placeholder="https://en.wikipedia.org/wiki/Spock",
                        info="Optional: Add the source URL for reference",
                        lines=1,
                        max_lines=1
                    )
                    process_file_btn = gr.Button("Process Uploaded HTML", variant="primary")

                # Option 2: Right column
                with gr.Column(scale=1):
                    gr.Markdown("### Option 2: Web Scraping or Use Mock Data")

                    gr.Markdown("**Example URLs:**")
                    gr.Markdown("""
                    - https://en.wikipedia.org/wiki/Daenerys_Targaryen
                    - https://en.wikipedia.org/wiki/Heinrich_Harrer
                    """)

                    wiki_url = gr.Textbox(
                        label="Wiki URL",
                        placeholder="https://en.wikipedia.org/wiki/Aloy",
                        info="Enter a wiki URL about a person or character",
                        lines=1,
                        max_lines=1
                    )
                    use_mock = gr.Checkbox(
                        label="Use Mock Data",
                        value=True,
                        info="Load from the saved default HTML file (no web scraping)"
                    )

                    process_btn = gr.Button("Process Wiki Page", variant="primary")

            # ✅ New row for output - full width
            gr.Markdown("---")
            with gr.Row():
                result_text = gr.Textbox(label="Initial Facts", lines=12, interactive=False)

            session_id = gr.Textbox(label="Session ID", visible=False)

            # Connect both buttons to the same output components
            process_file_btn.click(
                fn=process_got_profile_from_file,
                inputs=[html_file, wiki_url_optional],
                outputs=[result_text, session_id]
            )

            process_btn.click(
                fn=process_got_profile,
                inputs=[wiki_url, use_mock],
                outputs=[result_text, session_id]
            )

        with gr.Tab("Chat"):
            gr.Markdown("Ask questions about the person or character")

            chatbot = gr.Chatbot(
                height=500,
                type='messages',
                placeholder="Process a wiki page first, then ask questions here!"
            )

            chat_input = gr.Textbox(
                label="Ask a question about the character",
                placeholder="What is this person's/character's passion?",
                lines=1,
                max_lines=1
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
#                 # outputs=[chatbot, chat_input]
#                 #        ↑        ↑
#                 #        |        └── Gets the second return value ("")
#                 #        └── Gets the first return value (chat history)

#                 # Gradio maps return values to output components in order:
#                 #     First return value → First output component (chatbot): Updates the chat display with new messages
#                 #     Second return value → Second output component (chat_input): Sets the textbox value to "" (clearing it)
#                 #     The number of return values from the fn chat_with_character must match the number of components in the outputs list
#
            )

            gr.ClearButton([chatbot])

    return demo


if __name__ == "__main__":
    demo = create_gradio_interface()
    # Launch the Gradio interface
    demo.launch(
        server_name="127.0.0.1",
        server_port=5001,
        share=False  # Set to True to create a public link
    )
