import os
import requests

# url = "https://gameofthrones.fandom.com/wiki/Rhaenyra_Targaryen"
url = "https://gameofthrones.fandom.com/wiki/Tyrion_Lannister"

headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)

with open("../mock_got_wiki.html", "w", encoding="utf-8") as f:
    f.write(response.text)


#############
## better ##
#
# # Define the file path to save the HTML in the parent directory
# file_path = os.path.join("..", "mock_got_wiki.html")
#
# # Write the fetched HTML content to the specified file path
# with open(file_path, "w", encoding="utf-8") as f:
#     f.write(response.text)