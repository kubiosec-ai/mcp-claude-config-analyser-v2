import json
from typing import List, Optional
from pydantic import BaseModel
from agents import Agent, Runner


# === Load tools.json ===
with open("reporter_tools.json", "r") as f:
    tools = json.load(f).get("tools", [])


# === Define output structure ===
class PredictedPrecedence(BaseModel):
    tools: List[str]
    likely_selection: str
    reason: str
    conflicting_tools: List[str]

class OverlappingFunctionality(BaseModel):
    description: str
    predicted_precedence: List[PredictedPrecedence]

class IssueCategory(BaseModel):
    description: str
    affected_tools: List[str]

class Recommendations(BaseModel):
    suggestions: List[str]

class StructuredAnalysis(BaseModel):
    overlapping_functionality: OverlappingFunctionality
    influencing_or_persuasive_language: IssueCategory
    crafted_or_informal_tone: IssueCategory
    attention_seeking_wording: IssueCategory
    inconsistency_in_tone_or_structure: IssueCategory
    recommendations: Recommendations


# === Prompt ===
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

# === Construct prompt input ===
user_prompt = "Analyse this tool declarations:\n\n" + json.dumps(tools, indent=2)

# === Setup Agent ===
agent = Agent(
    name="Structured Analysis Agent",
    instructions=system_prompt,
    output_type=StructuredAnalysis
)

# === Run the Agent ===
result = Runner.run_sync(agent, user_prompt)

# === Print structured result as JSON ===
print(json.dumps(result.final_output.model_dump(), indent=2, ensure_ascii=False))