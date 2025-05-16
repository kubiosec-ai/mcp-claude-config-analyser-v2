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
    affected_tools: Optional[List[str]] = None

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

Your task is to analyze the tool descriptions and identify issues that could cause biased or incorrect tool selection by the LLM.

You MUST return a valid JSON object

Do not include any explanation, comments, or text outside the JSON. Output only the JSON object.
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