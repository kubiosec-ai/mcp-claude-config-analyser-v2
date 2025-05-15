# Copyright (c) 2025 kubiosec-ai
#
# This file is part of MCP Server Tool Analyzer.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import sys
from pathlib import Path
from openai import OpenAI

# Initialize the OpenAI client (it will use the OPENAI_API_KEY environment variable by default)
client = OpenAI()

# Get the filename from command-line arguments
json_file = sys.argv[1]


# Load the tools.json file
try:
    with open(json_file, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: File '{json_file}' not found")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: File '{json_file}' is not valid JSON")
    sys.exit(1)


# Handle different JSON formats
if isinstance(data, list):
    # If data is a list, use it directly as the tools list
    tools = data
    # Convert to expected format with name and description
    if len(tools) > 0 and "tool_name" in tools[0]:
        tools = [{"name": tool.get("tool_name", ""), "description": tool.get("description", "")} for tool in tools]
elif isinstance(data, dict) and "tools" in data:
    # If data is a dict with a "tools" key, use that
    tools = data.get("tools", [])
else:
    # Otherwise, use an empty list
    tools = []
    print("Warning: No tools found in the JSON file. Expected a list or a dict with a 'tools' key.")

# System prompt that sets up the security audit agent
system_prompt = """
You are given a JSON blob where each object contains a tool name and its description.

These tools are available to an AI agent that selects one or more tools to solve user queries.

Your task is to analyze the tool descriptions and identify any of the following issues that could cause biased or incorrect tool selection by the LLM:

1. Overlapping functionality — tools that perform similar actions and may confuse the model
2. Influencing or persuasive language — descriptions that subtly suggest preference or priority
3. Crafted or informal tone — non-neutral wording such as second-person instructions or emotional framing
4. Attention-seeking wording — descriptions using exaggeration or marketing-style language (e.g. "better", "use this if...")
5. Predicted precedence — for each overlapping tool group, predict which tool the LLM would likely select and explain why (e.g. due to tone, specificity, keyword match)
6. Inconsistency in tone or structure — descriptions that don’t follow a consistent, formal, objective style

The goal is to prevent the LLM from taking unintended or suboptimal actions due to description bias.
Provide a structured and reasoned analysis, grouped by issue type. Include recommendations where appropriate.
Pay attention to Predicted precedence, as it is crucial for understanding how the LLM might prioritize tools.
Identitfy which tools are most likely to be selected based on the descriptions provided if they are similar in nature
The analysis should be clear and concise, with a focus on the potential impact of each issue on the LLM's decision-making process.
"""

# Prepare the user message with tool data as a list
user_prompt = "Here is a list of tool declarations:\n\n" + json.dumps(tools, indent=2)

# Run OpenAI API call
response = client.chat.completions.create(
    model="gpt-4o",  # or gpt-4o if you have access
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0
)

# Display result
print("\n📋 Tool Security Audit Report:\n")
print(response.choices[0].message.content)