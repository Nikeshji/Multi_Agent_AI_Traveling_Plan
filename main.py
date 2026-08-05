import os
import re
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import requests

load_dotenv()

# ── LOCAL add_messages (no import needed) ───────────────────────────────────
def add_messages(left, right):
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return left + right

# ── LLM ──────────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)

# ── FLIGHT TOOL (embedded) ───────────────────────────────────────────────────
AVIATION_API_KEY = os.getenv("AVIATION_API_KEY")

def _mock_flights(origin: str, destination: str):
    return [
        {"airline": "Air India", "departure": f"{origin} at 06:30", "arrival": f"{destination} at 09:15", "status": "Scheduled"},
        {"airline": "IndiGo", "departure": f"{origin} at 14:00", "arrival": f"{destination} at 16:45", "status": "On Time"},
        {"airline": "Vistara", "departure": f"{origin} at 19:20", "arrival": f"{destination} at 22:10", "status": "Scheduled"},
    ]

def search_flights(origin: str, destination: str, date: str):
    if not AVIATION_API_KEY or AVIATION_API_KEY == "your_aviationstack_api_key":
        return _mock_flights(origin, destination)

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVIATION_API_KEY,
        "dep_iata": origin.upper() if len(origin) == 3 else origin,
        "arr_iata": destination.upper() if len(destination) == 3 else destination,
        "limit": 5,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return _mock_flights(origin, destination)

    flights = []
    if data.get("data"):
        for flight_info in data["data"][:5]:
            airline = flight_info.get("airline", {}).get("name", "N/A")
            dep = flight_info.get("departure", {})
            arr = flight_info.get("arrival", {})
            flights.append({
                "airline": airline,
                "departure": f"{dep.get('iataCode', 'N/A')} at {dep.get('scheduled', 'N/A')}",
                "arrival": f"{arr.get('iataCode', 'N/A')} at {arr.get('scheduled', 'N/A')}",
                "status": flight_info.get("flight_status", "N/A"),
            })

    return flights if flights else _mock_flights(origin, destination)


# ── TAVILY TOOL (embedded) ───────────────────────────────────────────────────
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def _mock_hotels(destination: str, days: int):
    return [
        {"title": f"Luxury Stay {destination}", "url": "https://example.com/hotel1", "content": f"5-star hotel in central {destination}. Pool, spa, free WiFi. ~₹8,000/night."},
        {"title": f"Budget Inn {destination}", "url": "https://example.com/hotel2", "content": f"Clean rooms, great location. ~₹2,500/night."},
        {"title": f"Boutique Hotel {destination}", "url": "https://example.com/hotel3", "content": f"Mid-range with rooftop restaurant. ~₹4,500/night."},
    ]

def _mock_attractions(destination: str):
    return [
        {"title": f"Top sights in {destination}", "url": "https://example.com/attr1", "content": f"Must-visit landmarks and cultural spots in {destination}."},
        {"title": f"{destination} City Guide", "url": "https://example.com/attr2", "content": f"Best museums, parks, and local markets."},
    ]

def search_hotels(destination: str, days: int = 5):
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY and TAVILY_API_KEY != "your_tavily_api_key" else None
    except ImportError:
        client = None

    if client is None:
        return _mock_hotels(destination, days)

    query = f"best hotels in {destination} for tourists budget luxury mid-range"
    try:
        response = client.search(query=query, search_depth="basic", max_results=5)
        results = response.get("results", [])
        return results if results else _mock_hotels(destination, days)
    except Exception:
        return _mock_hotels(destination, days)


def search_attractions(destination: str):
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY and TAVILY_API_KEY != "your_tavily_api_key" else None
    except ImportError:
        client = None

    if client is None:
        return _mock_attractions(destination)

    query = f"top tourist attractions sightseeing places to visit in {destination}"
    try:
        response = client.search(query=query, search_depth="basic", max_results=5)
        results = response.get("results", [])
        return results if results else _mock_attractions(destination)
    except Exception:
        return _mock_attractions(destination)


# ── STATE ────────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    final_response: str
    llm_calls: int


# ── HELPERS ──────────────────────────────────────────────────────────────────
def _extract_city_date(query: str):
    origin, destination, date = "DEL", "BOM", "2026-08-15"
    cities = re.findall(r"\b(?:to|for|in)\s+([A-Za-z\s]+?)(?:\s+trip|\s+from|\s+under|\s+\d|$)", query, re.IGNORECASE)
    if cities:
        destination = cities[-1].strip().split()[0]
    from_match = re.search(r"from\s+([A-Za-z]+)", query, re.IGNORECASE)
    if from_match:
        origin = from_match.group(1).strip()
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", query)
    if date_match:
        date = date_match.group(1)
    return origin, destination, date


def _format_hotel_results(results: list):
    text = ""
    for i, r in enumerate(results[:3], 1):
        text += f"**{i}. {r.get('title', 'Hotel')}**\n"
        text += f"- {r.get('content', 'No details')}\n"
        text += f"- [Link]({r.get('url', '#')})\n\n"
    return text


def _format_attractions(results: list):
    text = ""
    for i, r in enumerate(results[:3], 1):
        text += f"**{i}. {r.get('title', 'Attraction')}**\n"
        text += f"- {r.get('content', 'No details')}\n\n"
    return text


# ── AGENT NODES ──────────────────────────────────────────────────────────────
def flight_agent(state: AgentState):
    calls = state.get("llm_calls", 0) + 1
    query = state["user_query"]

    prompt = f"""You are a flight search assistant.
Extract the departure city, destination city, and travel date from this request:
"{query}"

Respond ONLY in this exact format (no extra text):
ORIGIN: <city or IATA code>
DESTINATION: <city or IATA code>
DATE: <YYYY-MM-DD>
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content
    origin, dest, date = _extract_city_date(query)

    for line in content.split("\n"):
        if line.upper().startswith("ORIGIN:"):
            origin = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DESTINATION:"):
            dest = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DATE:"):
            date = line.split(":", 1)[1].strip()

    flights = search_flights(origin, dest, date)

    flight_text = f"### ✈️ Flights: {origin} → {dest} ({date})\n\n"
    for i, f in enumerate(flights[:3], 1):
        flight_text += f"**{i}. {f.get('airline', 'Airline')}**\n"
        flight_text += f"- Departure: {f.get('departure', 'N/A')}\n"
        flight_text += f"- Arrival: {f.get('arrival', 'N/A')}\n"
        flight_text += f"- Status: {f.get('status', 'N/A')}\n\n"

    return {
        "flight_results": flight_text,
        "llm_calls": calls,
        "messages": [AIMessage(content=f"[Flight Agent] Completed search {origin}→{dest}.")],
    }


def hotel_agent(state: AgentState):
    calls = state.get("llm_calls", 0) + 1
    query = state["user_query"]

    prompt = f"""Extract only the destination city from this travel request:
"{query}"
Respond with just the city name, nothing else."""
    response = llm.invoke([HumanMessage(content=prompt)])
    destination = response.content.strip().split("\n")[0]

    hotels = search_hotels(destination)
    attractions = search_attractions(destination)

    hotel_text = f"### 🏨 Hotels in {destination}\n\n" + _format_hotel_results(hotels)
    hotel_text += f"\n### 🎯 Top Attractions in {destination}\n\n" + _format_attractions(attractions)

    return {
        "hotel_results": hotel_text,
        "llm_calls": calls,
        "messages": [AIMessage(content=f"[Hotel Agent] Found stays in {destination}.")],
    }


def itinerary_agent(state: AgentState):
    calls = state.get("llm_calls", 0) + 1
    query = state["user_query"]

    days_match = re.search(r"(\d+)\s*(?:day|days)", query, re.IGNORECASE)
    days = int(days_match.group(1)) if days_match else 5

    prompt = f"""Extract only the destination city from this request:
"{query}"
Respond with just the city name."""
    dest_response = llm.invoke([HumanMessage(content=prompt)])
    destination = dest_response.content.strip().split("\n")[0]

    prompt = f"""You are an expert travel planner. Create a detailed {days}-day itinerary for {destination}.

Use the following flight and hotel information to make it realistic:

{state['flight_results']}

{state['hotel_results']}

Format as:
### Day 1: ...
- Morning: ...
- Afternoon: ...
- Evening: ...

Continue for all {days} days. Add a brief budget tip at the end.
"""
    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "itinerary": response.content,
        "llm_calls": calls,
        "messages": [AIMessage(content=f"[Itinerary Agent] Planned {days} days in {destination}.")],
    }


def final_agent(state: AgentState):
    calls = state.get("llm_calls", 0) + 1

    prompt = f"""You are the Final Travel Concierge. Combine all research into one beautiful, cohesive travel plan.

## User Request
{state['user_query']}

## Flight Information
{state['flight_results']}

## Hotel & Attractions
{state['hotel_results']}

## Day-by-Day Itinerary
{state['itinerary']}

## Instructions
Write a final travel plan in markdown with:
1. **Executive Summary** (2-3 sentences)
2. **Flight Recommendations** (best pick + why)
3. **Hotel Recommendations** (best pick + why)
4. **Itinerary Highlights** (top 3 must-do experiences)
5. **Estimated Budget Breakdown** (table format)

Make it feel personal and exciting. Use emojis.
"""
    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "final_response": response.content,
        "llm_calls": calls,
        "messages": [AIMessage(content=response.content)],
    }


# ── BUILD GRAPH ──────────────────────────────────────────────────────────────
builder = StateGraph(AgentState)

builder.add_node("flight_agent", flight_agent)
builder.add_node("hotel_agent", hotel_agent)
builder.add_node("itinerary_agent", itinerary_agent)
builder.add_node("final_agent", final_agent)

builder.set_entry_point("flight_agent")
builder.add_edge("flight_agent", "hotel_agent")
builder.add_edge("hotel_agent", "itinerary_agent")
builder.add_edge("itinerary_agent", "final_agent")
builder.add_edge("final_agent", END)

checkpointer = MemorySaver()
print("✅ Using in-memory checkpointer (no database required).")

app = builder.compile(checkpointer=checkpointer)


# ── TERMINAL TEST ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_query = "Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2 lakhs"
    config = {"configurable": {"thread_id": "test_user_001"}}

    print(f"\n🚀 Testing with query: {test_query}\n")
    for chunk in app.stream(
        {
            "messages": [HumanMessage(content=test_query)],
            "user_query": test_query,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "final_response": "",
            "llm_calls": 0,
        },
        config=config,
        stream_mode="updates",
    ):
        for node_name, state_update in chunk.items():
            print(f"--- {node_name} ---")
            if node_name == "final_agent":
                msgs = state_update.get("messages", [])
                if msgs:
                    print(msgs[-1].content[:500] + "...")
            print()