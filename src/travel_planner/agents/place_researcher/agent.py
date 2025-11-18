from google.adk.agents import Agent
from google.adk.tools import google_search
from pathlib import Path


def get_place_researcher_agent():
    instructions_path = Path(__file__).resolve().parent / "instructions.md"
    with open(instructions_path, "r") as file:
        instructions = file.read()
        place_researcher_agent = Agent(
            model="gemini-2.5-flash",
            name="place_researcher_agent",
            description="An agent that researches places for travel planning.",
            instruction=instructions,
            tools=[google_search],
            output_key="place_research_data",
        )
    return place_researcher_agent
