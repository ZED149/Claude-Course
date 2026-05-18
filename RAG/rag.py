

from anthropic import Anthropic
import voyageai
from dotenv import load_dotenv
import os
import re

load_dotenv("C:/Users/salma/OneDrive/Desktop/Claude Course/.env")

#KEYS
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

voyage_client = voyageai.client(VOYAGE_API_KEY)
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)

# chunk by section
def chunk_by_section(document_text):
    pattern = r"\n##"
    return re.split(pattern, document_text)

# embedding generation
def embeding_generation(text, model="voyage-3-large", input_type="query"):
    result = voyage_client.embed([text], model=model, input_type=input_type)
    return result.embeddings[0]

# MAIN

# reading the file
with open("./report.md", "r") as file:
    text = file.read()

# breaking document text into chunks
chunks = chunk_by_section(text)
# converting chunks to embeddings
embeding_generation(chunks[0])

