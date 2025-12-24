
import gradio as gr
import os
from pathlib import Path
import traceback
from datetime import date, datetime
from travel_planner.utils import TravelRequest
from travel_planner.__main__ import run_travel_planner


LOG_FILES = {
    "Travel Report": Path("travel_report.md"),
    "Gastro": Path("gastro_agent_log.md"),
    "Navigation": Path("navigation_agent_log.md"),
    "Place Researcher": Path("place_researcher_agent_log.md"),
    "Itinerary": Path("itinerary_planner_agent_log.md"),
    "Weather": Path("weather_agent_log.md"),
}


def _read_file(path: Path) -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"*No file found: {path}*"
    except Exception as e:
        return f"Error reading {path}: {e}"


def _collect_logs() -> list[str]:
    return [_read_file(p) for p in LOG_FILES.values()]


def _parse_date(val: object | None) -> date | None:
    if not val:
        return None
    # If Gradio DatePicker passed a date object already
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    s = str(val).strip()
    # Try ISO first
    try:
        return date.fromisoformat(s)
    except Exception:
        pass
    # Try common formats
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


def run_and_collect(
    destination: str,
    source: str,
    duration: str,
    start_date: object | None,
    end_date: object | None,
    personas: str,
    extra_context: str,
) -> tuple[str, str, str, str, str, str]:
    """Run the planner and return contents for each tab.

    Returns a tuple with contents in the same order as `LOG_FILES`.
    """
    try:
        persona_list = [p.strip() for p in personas.split(",") if p.strip()]

        # Parse dates; handle Date objects or strings from fallback Textbox
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        # Build month and dates strings expected by TravelRequest
        if start and end:
            if start.month == end.month and start.year == end.year:
                month_str = start.strftime("%B %Y")
            else:
                month_str = f"{start.strftime('%B %Y')} — {end.strftime('%B %Y')}"
            dates_str = f"{start.isoformat()} to {end.isoformat()}"
        elif start and not end:
            month_str = start.strftime("%B %Y")
            dates_str = start.isoformat()
        else:
            month_str = date.today().strftime("%B %Y")
            dates_str = "Any"

        travel_request = TravelRequest(
            destination=destination,
            source=source,
            travel_duration=duration or "",
            month=month_str,
            dates=dates_str,
            persona=persona_list,
            extra_context=extra_context or "",
        )

        response = run_travel_planner(travel_request)

        # write travel report so it shows up in load-existing
        try:
            Path("travel_report.md").write_text(response, encoding="utf-8")
        except Exception:
            pass

        return tuple(_collect_logs())
    except Exception:
        tb = traceback.format_exc()
        # write full traceback to travel_report.md so user can inspect
        try:
            Path("travel_report.md").write_text(tb, encoding="utf-8")
        except Exception:
            pass
        # return traceback in the first tab and existing logs in others
        logs = _collect_logs()
        logs[0] = f"### Error running planner\n\n```\n{tb}\n```"
        return tuple(logs)


def load_existing() -> tuple[str, str, str, str, str, str]:
    return tuple(_collect_logs())


def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# Travel Planner — Agent Recommendation")

        with gr.Row():
            with gr.Column(scale=3):
                destination = gr.Textbox(label="Destination", placeholder="e.g. Prague, Czechia")
            with gr.Column(scale=2):
                source = gr.Textbox(label="Source", value="Prague, Czechia")

        with gr.Row():
            with gr.Column(scale=1):
                duration = gr.Textbox(label="Duration", value="Weekend trip, 3 days")
            with gr.Column(scale=2):
                personas = gr.Textbox(label="Personas (comma separated)", value="Foodie, Traveler")

        with gr.Row():
            # Some Gradio versions don't provide DatePicker. Fall back to Textbox.
            if hasattr(gr, "DatePicker"):
                start_date = gr.DatePicker(label="Start date (optional)")
                end_date = gr.DatePicker(label="End date (optional)")
            else:
                start_date = gr.Textbox(label="Start date (optional)", placeholder="YYYY-MM-DD or DD-MM-YYYY")
                end_date = gr.Textbox(label="End date (optional)", placeholder="YYYY-MM-DD or DD-MM-YYYY")
            extra_context = gr.Textbox(label="Extra context", value="romantic getaway")

        with gr.Row():
            btn = gr.Button("Generate Recommendation")
            load_btn = gr.Button("Load existing")

        tabs = gr.Tabs()
        tab_markdowns = []
        for title in LOG_FILES.keys():
            with tabs:
                with gr.TabItem(title):
                    md = gr.Markdown("", elem_id=title.replace(" ", "_"))
                    tab_markdowns.append(md)

        # Wire button actions: each returns content for each tab's Markdown
        btn.click(
            run_and_collect,
            inputs=[
                destination,
                source,
                duration,
                start_date,
                end_date,
                personas,
                extra_context,
            ],
            outputs=tab_markdowns,
        )

        load_btn.click(load_existing, inputs=[], outputs=tab_markdowns)

    return demo


def main():
    app = build_ui()
    app.launch()


if __name__ == "__main__":
    main()
