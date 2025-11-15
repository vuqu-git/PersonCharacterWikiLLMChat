"""Module for extracting LinkedIn profile data."""

import time
import requests
import logging
from typing import Dict, Optional, Any

from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)

def extract_linkedin_profile(
        linkedin_profile_url: str,
        api_key: Optional[str] = None,
        mock: bool = True
) -> Dict[str, Any]:
    """Extract LinkedIn profile data using ProxyCurl API or loads a premade JSON file.

    Args:
        linkedin_profile_url: The LinkedIn profile URL to extract data from.
        api_key: ProxyCurl API key. Required if mock is False.
        mock: If True, loads mock data from a premade JSON file instead of using the API.

    Returns:
        Dictionary containing the LinkedIn profile data.
    """
    start_time = time.time()

    try:
        if mock:
            logger.info("Using mock data from a premade JSON file...")
            mock_url = config.MOCK_DATA_URL
            response = requests.get(mock_url, timeout=30)
        else:
            # Ensure API key is provided when mock is False
            if not api_key:
                raise ValueError("ProxyCurl API key is required when mock is set to False.")

            logger.info("Starting to extract the LinkedIn profile...")
            # Set up the API endpoint and headers
            api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            # Prepare parameters for the request
            params = {
                "url": linkedin_profile_url,
                "fallback_to_cache": "on-error",
                "use_cache": "if-present",
                "skills": "include",
                "inferred_salary": "include",
                "personal_email": "include",
                "personal_contact_number": "include"
            }
            logger.info(f"Sending API request to ProxyCurl at {time.time() - start_time:.2f} seconds...")
            # Send API request
            response = requests.get(api_endpoint, headers=headers, params=params, timeout=10)

        logger.info(f"Received response at {time.time() - start_time:.2f} seconds...")
        # Check if response is successful
        if response.status_code == 200:
            try:
                # Parse the JSON response
                data = response.json()

                # Clean the data, remove empty values and unwanted fields
                data = {
                    k: v
                    for k, v in data.items()
                    if v not in ([], "", None) and k not in ["people_also_viewed", "certifications"]
                }
                # Remove profile picture URLs from groups to clean the data
                if data.get("groups"):
                    for group_dict in data.get("groups"):
                        group_dict.pop("profile_pic_url", None)
                return data
            except ValueError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Response content: {response.text[:200]}...")  # Print first 200 chars
                return {}
        else:
            logger.error(f"Failed to retrieve data. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {}

    except Exception as e:
        logger.error(f"Error in extract_linkedin_profile: {e}")
        return {}

##################################

def extract_wiki_profile(
        wiki_url: str = None,
        mock: bool = False,
        html_content: str = None  # NEW: Accept HTML content directly
) -> Dict[str, Any]:
    """Extract wiki page content using web scraping.

    Args:
        wiki_url: The wiki URL to scrape.
        mock: If True, loads mock data from a saved HTML file instead of scraping.

    Returns:
        Dictionary containing the scraped wiki page data with structured sections.
    """
    start_time = time.time()

    try:
        # Priority: 1. Direct HTML content (uploaded file)
        #           2. Mock file
        #           3. Web scraping
        if html_content:
            logger.info("Using uploaded HTML content...")
            logger.info(f"HTML content length: {len(html_content)} characters")
            # ✅ DON'T parse yet - just store it
        elif mock:
            logger.info("Using mock data from a saved HTML file...")
            mock_file_path = "mock_wiki.html"
            try:
                with open(mock_file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                logger.info(f"Loaded mock HTML from {mock_file_path}")
            except FileNotFoundError:
                logger.error(f"Mock file not found: {mock_file_path}")
                logger.info("Please save a wiki page HTML to 'mock_wiki.html' or disable mock mode")
                return {}
        else:
            # Only web scrape if no html_content and not mock
            if not wiki_url:
                logger.error("No wiki URL provided for web scraping")
                return {}

            logger.info(f"Starting to scrape wiki page: {wiki_url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }

            logger.info(f"Sending request to Wiki at {time.time() - start_time:.2f} seconds...")
            response = requests.get(wiki_url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to retrieve wiki page. Status code: {response.status_code}")
                return {}

            html_content = response.text
            logger.info(f"Received response with {len(html_content)} characters")

        # ✅ NOW parse the HTML (after getting it from one of the three sources)
        logger.info(f"Parsing HTML at {time.time() - start_time:.2f} seconds...")

        # **************************************************************
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract character name from title
        title_element = soup.find('h1', class_='page-header__title')
        character_name = title_element.get_text(strip=True) if title_element else "Unknown"
        logger.info(f"Character name: {character_name}")

        # Extract main content from the article
        content_div = soup.find('div', class_='mw-parser-output')

        if not content_div:
            logger.error("Could not find main content div")
            return {}

        # Initialize data structure
        data = {
            "name": character_name,
            "url": wiki_url if wiki_url else "Uploaded HTML",
            "sections": {}
        }

        # Extract text sections, filtering out unwanted elements
        blacklist = ['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside']

        # Find all section headers and content
        current_section = "Overview"
        section_content = []

        for element in content_div.find_all(['h2', 'h3', 'p', 'ul']):
            # Skip blacklisted elements
            if element.name in blacklist or element.parent.name in blacklist:
                continue

            # Check if it's a section header
            if element.name in ['h2', 'h3']:
                # Save previous section if it has content
                if section_content:
                    data["sections"][current_section] = ' '.join(section_content)
                    section_content = []

                # Start new section
                current_section = element.get_text(strip=True)
                # Remove edit links and other unwanted text
                current_section = current_section.replace('[edit]', '').strip()

            # Extract paragraph or list text
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text and len(text) > 20:  # Filter out very short paragraphs
                    section_content.append(text)

            elif element.name == 'ul':
                # Extract list items
                list_items = [li.get_text(strip=True) for li in element.find_all('li')]
                if list_items:
                    section_content.extend(list_items)

        # Save the last section
        if section_content:
            data["sections"][current_section] = ' '.join(section_content)

        # Extract infobox data if available
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            infobox_data = {}
            for row in infobox.find_all('div', class_='pi-item'):
                label_elem = row.find('h3', class_='pi-data-label')
                value_elem = row.find('div', class_='pi-data-value')

                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    infobox_data[label] = value

            if infobox_data:
                data["infobox"] = infobox_data
                logger.info(f"Extracted infobox with {len(infobox_data)} fields")

        # Clean empty sections
        data["sections"] = {k: v for k, v in data["sections"].items() if v}
        # **************************************************************

        logger.info(f"Successfully extracted {len(data['sections'])} sections from wiki page")
        logger.info(f"Total processing time: {time.time() - start_time:.2f} seconds")
        return data

    except FileNotFoundError:
        logger.error("Mock HTML file not found. Please save a mock file as 'mock_wiki.html'")
        return {}
    except Exception as e:
        logger.error(f"Error in extract_wiki_profile: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}