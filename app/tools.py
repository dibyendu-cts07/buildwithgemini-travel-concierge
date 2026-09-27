import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from google.adk.tools import ToolContext
from google.cloud import firestore, storage
from google.genai import types

load_dotenv()




# Configurable project ID and media bucket name
FIRESTORE_PROJECT = os.getenv("FIRESTORE_PROJECT", "qwiklabs-gcp-02-bc2b4d729077")
BUCKET_NAME = os.getenv("MEDIA_BUCKET_NAME", "travel-concierge-media-qwiklabs-gcp-02-bc2b4d729077")


def get_firestore_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT)


def search_destinations(country: str = "", category: str = "") -> str:
    """Searches for travel destinations stored in Firestore database.

    Args:
        country: Optional country name filter (e.g. 'Japan', 'France', 'USA').
        category: Optional category filter (e.g. 'Culture & Tech', 'Art & Romance').

    Returns:
        A list of matching travel destination summaries from Firestore.
    """
    db = get_firestore_client()
    docs = db.collection("destinations").stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        if country and country.lower() not in data.get("country", "").lower():
            continue
        if category and category.lower() not in data.get("category", "").lower():
            continue

        results.append(data)

    if not results:
        return f"No destinations found matching country='{country}', category='{category}'."

    return str(results)


def get_destination_details(destination_id: str) -> str:
    """Retrieves full details for a specific travel destination from Firestore.

    Args:
        destination_id: The document ID of the destination (e.g. 'tokyo-japan', 'paris-france').

    Returns:
        Detailed dictionary string of destination attributes, attractions, and rating.
    """
    db = get_firestore_client()
    doc_ref = db.collection("destinations").document(destination_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Destination ID '{destination_id}' not found in Firestore."

    return str(doc.to_dict())


def save_travel_itinerary(city: str, days: int, notes: str) -> str:
    """Saves a travel itinerary created for the user into Firestore database.

    Args:
        city: City or destination name for the itinerary.
        days: Duration of the trip in days.
        notes: Highlights or itinerary notes for the trip.

    Returns:
        Confirmation message with the generated itinerary document ID.
    """
    db = get_firestore_client()
    doc_id = f"{city.lower().replace(' ', '-')}-{days}days"
    itinerary_data = {
        "city": city,
        "days": days,
        "notes": notes,
        "status": "saved",
    }
    db.collection("itineraries").document(doc_id).set(itinerary_data)
    return f"Successfully saved itinerary '{doc_id}' in Firestore database!"


def generate_destination_postcard(
    destination: str, style_description: str = ""
) -> str:
    """Generates a scenic AI travel postcard visual for a destination and uploads it to Cloud Storage.

    Args:
        destination: Name of the city or destination (e.g. 'Tokyo', 'Paris', 'Kyoto').
        style_description: Optional custom artistic style or scenery details (e.g. 'sunset view with cherry blossoms').

    Returns:
        The public HTTP URL of the generated postcard image.
    """
    try:
        genai_client = genai.Client(
            vertexai=True, project=FIRESTORE_PROJECT, location="us-central1"
        )
        prompt = f"A beautiful artistic travel postcard of {destination}."
        if style_description:
            prompt += f" Style details: {style_description}."

        response = genai_client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return f"Failed to generate postcard image for {destination}."

        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(BUCKET_NAME)

        filename = f"postcards/{destination.lower().replace(' ', '-')}-{int(time.time())}.png"
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = (
            f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        )
        return f"Successfully generated postcard for {destination}! View image at: {public_url}"

    except Exception as e:
        return f"Error generating postcard for {destination}: {str(e)}"


def get_live_currency_exchange(
    amount: float, from_currency: str = "USD", to_currency: str = "EUR"
) -> str:
    """Fetches real live foreign currency exchange rates and converts travel amounts using the Frankfurter public API.

    Args:
        amount: The monetary amount to convert (e.g. 100.0).
        from_currency: The source 3-letter currency code (e.g. 'USD', 'EUR', 'GBP').
        to_currency: The target 3-letter currency code (e.g. 'JPY', 'EUR', 'USD', 'GBP').

    Returns:
        String detailing converted value and exchange rate.
    """
    try:
        from_curr = from_currency.upper().strip()
        to_curr = to_currency.upper().strip()
        url = f"https://api.frankfurter.dev/v1/latest?amount={amount}&from={from_curr}&to={to_curr}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        converted_val = data.get("rates", {}).get(to_curr)
        if converted_val is not None:
            rate = converted_val / amount if amount > 0 else 0
            return f"{amount} {from_curr} = {converted_val:.2f} {to_curr} (Exchange rate: 1 {from_curr} = {rate:.4f} {to_curr}, Date: {data.get('date')})"
        return f"Could not find exchange rate from {from_curr} to {to_curr}."
    except Exception as e:
        return f"Error fetching currency exchange rate: {str(e)}"


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographic coordinates (latitude, longitude) using Google Maps Geocoding API.

    Args:
        address: The address, landmark, or city name to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Tokyo Tower').

    Returns:
        Formatted address and latitude/longitude coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY is not set in environment."

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            return f"Geocoding failed for '{address}': {data.get('status')}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address")
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return f"Address: {formatted_address} | Location: (latitude={lat}, longitude={lng})"

    except Exception as e:
        return f"Error geocoding address '{address}': {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> str:
    """Finds nearby places of a given type around coordinates using Google Maps Places API (New).

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        place_type: Type of place to search for (e.g. 'restaurant', 'tourist_attraction', 'cafe', 'hotel').
        radius_meters: Search radius in meters (default: 1000).

    Returns:
        List of nearby places with name, formatted address, and location coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY is not set in environment."

    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }
        body = {
            "includedTypes": [place_type],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": float(radius_meters),
                }
            },
        }

        response = requests.post(url, headers=headers, json=body, timeout=5)
        response.raise_for_status()
        data = response.json()

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        results = []
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown")
            addr = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            results.append(
                {
                    "name": name,
                    "address": addr,
                    "location": loc,
                }
            )

        return str(results)

    except Exception as e:
        return f"Error finding nearby places: {str(e)}"


async def generate_travel_image(
    prompt_description: str, tool_context: ToolContext = None
) -> str:
    """Generates an image for a travel destination, landmark, or culinary item using gemini-3.1-flash-lite-image in the global region.
    Saves the generated image as a session artifact and uploads it to public Cloud Storage.

    Args:
        prompt_description: Description of the travel item or destination to visualize (e.g. 'Eiffel Tower illuminated at night', 'Fresh sushi platter in Tokyo').
        tool_context: Optional ADK ToolContext automatically injected by framework.

    Returns:
        The public HTTPS URL of the uploaded image on Cloud Storage.
    """
    try:
        genai_client = genai.Client(
            vertexai=True, project=FIRESTORE_PROJECT, location="global"
        )
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt_description,
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return f"Failed to generate image for '{prompt_description}'."

        filename = f"domain_images/{int(time.time())}.png"

        # (1) Save image with tool_context.save_artifact for Playground's Artifacts panel
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(
                    data=image_bytes, mime_type="image/png"
                )
                await tool_context.save_artifact(
                    filename=filename, artifact=artifact_part
                )
            except Exception as e:
                print(f"Failed to save artifact in tool_context: {e}")

        # (2) Upload image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url

    except Exception as e:
        return f"Error generating travel image: {str(e)}"


async def generate_destination_video(
    prompt_description: str, tool_context: ToolContext = None
) -> str:
    """Generates a short video for a travel destination, landmark, or attraction using Google's Omni model (gemini-omni-flash-preview) in the global region.
    Saves the generated video as a session artifact for the Playground and uploads it to public Cloud Storage.

    Args:
        prompt_description: Detailed description of the travel scene or item to visualize as a video (e.g. 'A scenic 5-second video preview of Kyoto, Japan with cherry blossoms gently swaying').
        tool_context: Optional ADK ToolContext automatically injected by framework.

    Returns:
        The public HTTPS URL of the uploaded video on Cloud Storage.
    """
    try:
        genai_client = genai.Client(
            vertexai=True, project=FIRESTORE_PROJECT, location="global"
        )
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt_description,
        )

        video_bytes = None
        if hasattr(interaction, "output_video") and interaction.output_video and getattr(interaction.output_video, "data", None):
            import base64
            video_bytes = base64.b64decode(interaction.output_video.data)
        elif hasattr(interaction, "steps"):
            import base64
            for step in getattr(interaction, "steps", []):
                for part in getattr(step, "content", []):
                    if getattr(part, "type", None) == "video" and getattr(part, "data", None):
                        video_bytes = base64.b64decode(part.data)
                        break

        if not video_bytes:
            return f"Failed to generate video for '{prompt_description}'."

        import uuid
        filename = f"destination_videos/video_{uuid.uuid4().hex[:8]}.mp4"

        # (1) Save video with tool_context.save_artifact so it shows up in Playground's Artifacts panel
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(
                    data=video_bytes, mime_type="video/mp4"
                )
                await tool_context.save_artifact(
                    filename=filename, artifact=artifact_part
                )
            except Exception as e:
                print(f"Failed to save artifact in tool_context: {e}")

        # (2) Upload video bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url

    except Exception as e:
        return f"Error generating travel video: {str(e)}"




