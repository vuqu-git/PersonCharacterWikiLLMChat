import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "modules"))

from llm_interface import create_perplexity_llm

# Create LLM
llm = create_perplexity_llm(temperature=0.0, max_new_tokens=100)

# Test it
# q = "What is Star Trek?"
# q = "What is the current bitcoin price?"
# q = "What happened in the news today?"
q = "Who won the 2025 Super Bowl?"
response = llm.complete(q)

print("Response:", response)
