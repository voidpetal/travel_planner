from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
from pydantic import BaseModel, Field


APP_NAME = "travel_planner_app"
USER_ID = "main_user"
SESSION_ID = "12345"


async def setup_session_and_runner(agent):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


async def call_agent_async(query, agent):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    _, runner = await setup_session_and_runner(agent)
    events = runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    )

    async for event in events:
        response = event.content.parts[0].text
        if response:
            with open(f"{event.author}_log.md", "w", encoding="utf-8") as f:
                f.write(response)
        if event.is_final_response():
            final_response = response

    return final_response


def run_agent(agent, user_input):
    return asyncio.run(call_agent_async(user_input, agent))


USER_INPUT_TEMPLATE = """Source: {source}
    Destination: {destination}
    Travel time and duration: {travel_duration}
    Month of travel: {month}
    Dates of travel: {dates}
    Traveler persona: {personas}
    Extra context: {extra_context}"""


class TravelRequest(BaseModel):
    destination: str = Field(..., description="The travel destination.")
    source: str = Field(..., description="The starting point of travel.")
    travel_duration: str = Field(..., description="The travel time and duration.")
    month: str = Field(..., description="The month of travel.")
    dates: str = Field("Any", description="The specific days of travel.")
    persona: list[str] = Field(..., description="The traveler persona.")
    extra_context: str = Field(
        "N/A", description="Additional context for the travel plan."
    )

    def to_string(self) -> str:
        return USER_INPUT_TEMPLATE.format(
            source=self.source,
            destination=self.destination,
            travel_duration=self.travel_duration,
            month=self.month,
            dates=self.dates,
            personas=", ".join(self.persona),
            extra_context=self.extra_context,
        )
