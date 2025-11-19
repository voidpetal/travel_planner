from dotenv import load_dotenv
from google.adk.agents import SequentialAgent, ParallelAgent
from travel_planner.agents import (
    get_gastro_agent,
    get_itinerary_agent,
    get_navigation_agent,
    get_place_researcher_agent,
    get_weather_agent,
)
from travel_planner.utils import run_agent, TravelRequest
from argparse import ArgumentParser
from datetime import date
load_dotenv()


if __name__ == "__main__":
    
    default_personas = [
        "Budget but Comfort",
        "Slow Traveler",
        "Cultural Explorer",
        "Foodie",
        "Outdoor Enjoyer",
        "Couple",
    ]
    default_duration = "Weekend trip, 3 days"
    default_month = date.today().strftime("%B").lower() + " " + str(date.today().year)
    default_extra_context = "romantic getaway"

    parser = ArgumentParser(description="Travel Planner")
    parser.add_argument(
        "--destination", type=str, required=True, help="Travel destination"
    )
    parser.add_argument(
        "--source", type=str, required=False, help="Travel source location", default="Prague, Czechia"
    )
    parser.add_argument(
        "--duration", type=str, required=False, help="Duration of the travel", default=default_duration
    )
    parser.add_argument("--month", type=str, required=False, help="Month of travel", default=default_month)
    parser.add_argument("--dates", type=str, required=False, help="Specific dates", default="Any")
    parser.add_argument(
        "--extra-context", type=str, help="Extra context for the travel", default=default_extra_context
    )
    parser.add_argument(
        "--personas",
        type=str,
        nargs="+",
        default=default_personas,
        help="Traveler personas",
    )
    args = parser.parse_args()

    travel_request = TravelRequest(
        destination=args.destination,
        source=args.source,
        travel_duration=args.duration,
        month=args.month,
        dates=args.dates,
        persona=args.personas,
        extra_context=args.extra_context,
    )

    parallel = ParallelAgent(
        name="ResearchPhase",
        sub_agents=[
            get_weather_agent(),
            get_gastro_agent(),
            get_navigation_agent(),
        ],
    )
    pipeline = SequentialAgent(
        name="TravelPlanning",
        sub_agents=[parallel, get_place_researcher_agent(), get_itinerary_agent()],
    )

    response = run_agent(pipeline, travel_request.to_string())

    with open("travel_report.md", "w", encoding="utf-8") as f:
        f.write(response)
