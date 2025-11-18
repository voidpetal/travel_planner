from google.adk.agents import Agent
from google.adk.tools import google_search
from pathlib import Path


def get_gastro_agent():
    instructions_path = Path(__file__).resolve().parent / "instructions.md"
    with open(instructions_path, "r") as file:
        instructions = file.read()
        agent = Agent(
            model="gemini-2.5-flash",
            name="gastro_agent",
            description="An agent that researches food and drinks of a particular place.",
            instruction=instructions,
            tools=[google_search],
            output_key="gastro_data",
        )
    return agent
