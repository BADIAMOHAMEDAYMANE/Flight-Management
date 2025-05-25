# utils/constants.py

# AI System Prompt
SYSTEM_PROMPT = """You are TravelMate, a friendly travel assistant. Respond to greetings naturally.

For travel requests, format your response as follows:

## Recommended Destinations

{destination_card}**Paris, France**{/destination_card}
* **Highlights:** Iconic Eiffel Tower, world-class museums, charming cafés
* **Perfect for:** Romantic getaways, art lovers, foodies
* **Best time to visit:** Spring (April-June) or Fall (September-October)

{destination_card}**Tokyo, Japan**{/destination_card}
* **Highlights:** Blend of tradition and futuristic technology, incredible food scene
* **Perfect for:** Food enthusiasts, technology fans, culture seekers
* **Best time to visit:** Spring (March-May) or Fall (October-November)

{destination_card}**Costa Rica**{/destination_card}
* **Highlights:** Lush rainforests, beautiful beaches, abundant wildlife
* **Perfect for:** Nature lovers, adventure seekers, eco-tourists  
* **Best time to visit:** Dry season (December-April)

For specific destination queries, use this format:

## {destination_card}{Destination Name}{/destination_card}

**Top Attractions:**
* {Attraction 1}
* {Attraction 2}
* {Attraction 3}

**Local Cuisine:** {Brief description of local food}

**Best Time to Visit:** {Season information}

**Travel Tips:**
* {Tip 1}
* {Tip 2}
* {Tip 3}

{suggest_buttons}["I choose {destination name}", "Budget for {destination name}", "Flights to {destination name}"]{/suggest_buttons}

For budget-related questions, respond with a breakdown like this:

## Budget Estimate for {Destination}

**Accommodation:**
* Budget: ${X}-${Y} per night
* Mid-range: ${X}-${Y} per night
* Luxury: ${X}+ per night

**Food:**
* Budget meals: ${X}-${Y} per day
* Mid-range dining: ${X}-${Y} per day
* Fine dining: ${X}+ per meal

**Transportation:**
* Public transit: ${X} per day
* Car rental: ${X}-${Y} per day
* Taxis/rideshares: Average ${X} per ride

**Activities:**
* Free attractions: {Examples}
* Paid attractions: ${X}-${Y} per activity
* Tours: ${X}-${Y} per tour

**Estimated daily budget:** ${X}-${Y} depending on travel style

{suggest_buttons}["I choose {destination name}", "Weather in {destination name}", "Things to do in {destination name}"]{/suggest_buttons}

Always inform users they can get detailed information by typing "I choose {destination name}".
"""

# Destination mapping for Travel Advisor API
DESTINATION_CONTENT_IDS = {
    "paris": "187147",
    "london": "186338",
    "new york": "60763",
    "tokyo": "298184",
    "rome": "187791",
    "barcelona": "187497",
    "dubai": "295424",
    "sydney": "255060",
    "amsterdam": "188590",
    "bangkok": "293916",
    "los angeles": "32655",
    "las vegas": "45963",
    "chicago": "35805",
    "miami": "34439",
    "berlin": "187323",
    "madrid": "187514",
    "singapore": "294265",
    "san francisco": "60713",
    "hong kong": "294217",
}

# Base costs for different budget levels (per person, per day in USD)
BASE_COSTS = {
    "budget": {
        "accommodation": {"min": 50, "max": 100},
        "food": {"min": 20, "max": 40},
        "activities": {"min": 10, "max": 30},
        "transport": {"min": 5, "max": 15}
    },
    "mid-range": {
        "accommodation": {"min": 100, "max": 250},
        "food": {"min": 40, "max": 80},
        "activities": {"min": 30, "max": 60},
        "transport": {"min": 15, "max": 40}
    },
    "luxury": {
        "accommodation": {"min": 250, "max": 1000},
        "food": {"min": 80, "max": 200},
        "activities": {"min": 60, "max": 200},
        "transport": {"min": 40, "max": 150}
    }
}

# Cost multipliers for different destinations
COST_MULTIPLIERS = {
    "paris": 1.3,
    "london": 1.4,
    "new york": 1.5,
    "tokyo": 1.4,
    "dubai": 1.3,
    "sydney": 1.2,
    "hong kong": 1.3,
    "singapore": 1.2,
    "las vegas": 1.1,
    "bangkok": 0.6,
    "barcelona": 1.0,
    "rome": 1.1,
    "berlin": 1.0,
    "madrid": 1.0,
    "amsterdam": 1.2,
    "chicago": 1.1,
    "los angeles": 1.3,
    "san francisco": 1.4,
    "miami": 1.2
}

# Attractions data for major destinations
ATTRACTIONS_DATA = {
    "paris": [
        {"name": "Eiffel Tower", "cost": 25},
        {"name": "Louvre Museum", "cost": 17},
        {"name": "Seine River Cruise", "cost": 15}
    ],
    "london": [
        {"name": "Tower of London", "cost": 30},
        {"name": "London Eye", "cost": 35},
        {"name": "Westminster Abbey", "cost": 25}
    ],
    "new york": [
        {"name": "Empire State Building", "cost": 42},
        {"name": "Metropolitan Museum of Art", "cost": 25},
        {"name": "Statue of Liberty Ferry", "cost": 24}
    ],
    "tokyo": [
        {"name": "Tokyo Skytree", "cost": 23},
        {"name": "Robot Restaurant Show", "cost": 80},
        {"name": "Senso-ji Temple", "cost": 0}
    ],
    "rome": [
        {"name": "Colosseum", "cost": 16},
        {"name": "Vatican Museums", "cost": 17},
        {"name": "Roman Forum", "cost": 16}
    ]
}

# Flight cost estimates
FLIGHT_COSTS = {
    "budget": {"min": 300, "max": 600},
    "mid-range": {"min": 600, "max": 1200},
    "luxury": {"min": 1200, "max": 3000}
}

# CORS Headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST",
    "Access-Control-Allow-Headers": "Content-Type"
}