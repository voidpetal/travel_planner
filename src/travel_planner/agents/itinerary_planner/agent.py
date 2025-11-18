from google.adk.agents import Agent
from pathlib import Path


def get_itinerary_agent():
    instructions_path = Path(__file__).resolve().parent / "instructions.md"
    with open(instructions_path, "r") as file:
        instructions = file.read()
        agent = Agent(
            model="gemini-2.5-flash",
            name="itinerary_planner_agent",
            description="An agent that plans the final itinerary for the trip.",
            instruction=instructions,
            output_key="itinerary_data",
        )
    return agent
