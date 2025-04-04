from pydantic_ai import Agent, RunContext
from httpx import AsyncClient
from dataclasses import dataclass
import os
import json

import nest_asyncio
nest_asyncio.apply()

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
import os

os.system('clear')

model = GroqModel('llama-3.3-70b-versatile')
agent = Agent(model)

Question="When was the first computer bug found?"
result = agent.run_sync(Question)  
print(f"{Question}:\n{'='*len(Question)}\n{result.data}")
#######################################################################################################
from pydantic_ai import Agent, RunContext
from httpx import AsyncClient
from dataclasses import dataclass
import os
import json

@dataclass
class FlightDeps:
    client: AsyncClient
    flight_api_key: str | None

# Define the model and flight agent
flight_agent = Agent(
    model=GroqModel('llama-3.3-70b-versatile'),
    system_prompt="""
        You are a helpful flight assistant. If flight information is 
        available, provide it in the following form:

        Flight IATA: {flight.iata}
        Flight Date: {flight_date}
        Departure Airport: {departure.airport} ({departure.iata})
        Departure Time: {departure.scheduled_time}
        Arrival Airport: {arrival.airport} ({arrival.iata})
        Arrival Time: {arrival.scheduled_time}

        If no information is available, respond with: "No information found 
        for this flight."
    """,
    deps_type=FlightDeps,
)


@flight_agent.tool
async def get_flight_info(ctx: RunContext[FlightDeps], flight_iata: str) -> dict:
    """
    Retrieve flight information using the AviationStack API.
    """
    if ctx.deps.flight_api_key is None:
        return {'error': 'No API key provided'}

    url = "https://api.aviationstack.com/v1/flights"
    params = {
        "access_key": ctx.deps.flight_api_key,
        "flight_iata": flight_iata,
    }

    try:
        response = await ctx.deps.client.get(url, params=params)
        response.raise_for_status()

        if not response.text.strip():  # Check for empty response
            return {"error": "API returned an empty response"}

        data = response.json()  # Parse JSON
        if data.get("data"):
            flight_data = data["data"][0]  # Use the first flight record
            return {
                "flight_date": flight_data.get("flight_date"),
                "flight_status": flight_data.get("flight_status"),
                "departure": {
                    "airport": flight_data["departure"].get("airport"),
                    "iata": flight_data["departure"].get("iata"),
                    "scheduled_time": flight_data["departure"].get("scheduled"),
                },
                "arrival": {
                    "airport": flight_data["arrival"].get("airport"),
                    "iata": flight_data["arrival"].get("iata"),
                    "scheduled_time": flight_data["arrival"].get("scheduled"),
                },
                "airline": {
                    "name": flight_data["airline"].get("name"),
                    "iata": flight_data["airline"].get("iata"),
                },
                "flight": {
                    "number": flight_data["flight"].get("number"),
                    "iata": flight_data["flight"].get("iata"),
                },
            }
        else:
            return {"error": "No data found for the given flight number"}
    except Exception as e:
        return {"error": f"API error: {str(e)}"}


# Main function to execute the flight agent
async def main():
    """
    Main function to run the flight agent.
    """
    async with AsyncClient() as client:
        # Replace 'your_api_key_here' with your AviationStack API key
        deps = FlightDeps(client, os.getenv("AVIATIONSTACK_API_KEY"))
        flight_iata = "BA1455"  # Example flight number
        result = await flight_agent.run(f"Check flight status for {flight_iata}.", deps=deps)

        # Debug raw result data
        print(result.data)

        # Handle and display flight information
        try:
            flight_info = result.data  # Treat result.data as plain text

            # Check if an error occurred
            if "No information found" in flight_info or "error" in flight_info:
                print("Error:", flight_info)

        except Exception as e:
            print("An unexpected error occurred:", e)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())