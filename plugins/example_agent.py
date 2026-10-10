"""Example agent plugin."""

def example_agent(context: dict) -> dict:
    return {"bias": 0.1, "view": "Example plugin agent sees mild bullish structure"}

def register_agent():
    return "example", example_agent
