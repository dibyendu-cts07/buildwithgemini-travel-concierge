import os
from google.cloud import firestore

# Hardcoded project ID as required for Agent Platform compatibility
FIRESTORE_PROJECT = "qwiklabs-gcp-02-bc2b4d729077"

def seed_destinations():
    db = firestore.Client(project=FIRESTORE_PROJECT)
    
    destinations = [
        {
            "id": "tokyo-japan",
            "name": "Tokyo",
            "country": "Japan",
            "category": "Culture & Tech",
            "description": "A vibrant metropolis blending ultramodern skyscrapers with historic temples.",
            "price_level": "$$$",
            "rating": 4.9,
            "best_season": "Spring / Autumn",
            "top_attractions": ["Senso-ji Temple", "Shibuya Crossing", "Shinjuku Gyoen", "Tokyo Skytree"]
        },
        {
            "id": "kyoto-japan",
            "name": "Kyoto",
            "country": "Japan",
            "category": "Heritage & Nature",
            "description": "Japan's cultural heart filled with classical Buddhist temples, gardens, and imperial palaces.",
            "price_level": "$$",
            "rating": 4.8,
            "best_season": "Spring / Autumn",
            "top_attractions": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)"]
        },
        {
            "id": "paris-france",
            "name": "Paris",
            "country": "France",
            "category": "Art & Romance",
            "description": "A global center for art, fashion, gastronomy, and culture famous for its landmark architecture.",
            "price_level": "$$$$",
            "rating": 4.7,
            "best_season": "Late Spring / Early Fall",
            "top_attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Arc de Triomphe"]
        },
        {
            "id": "san-francisco-usa",
            "name": "San Francisco",
            "country": "USA",
            "category": "Coastal & Culture",
            "description": "Famous for its steep hills, iconic Golden Gate Bridge, cable cars, and colorful Victorian houses.",
            "price_level": "$$$$",
            "rating": 4.6,
            "best_season": "September - November",
            "top_attractions": ["Golden Gate Bridge", "Alcatraz Island", "Fisherman's Wharf", "Golden Gate Park"]
        },
        {
            "id": "agra-india",
            "name": "Agra (Taj Mahal)",
            "country": "India",
            "category": "Heritage & Wonders",
            "description": "Home to the magnificent Taj Mahal, one of the Seven Wonders of the World, along with historic Mughal forts.",
            "price_level": "$$",
            "rating": 4.9,
            "best_season": "October - March",
            "top_attractions": ["Taj Mahal", "Agra Fort", "Fatehpur Sikri", "Mehtab Bagh"]
        },
        {
            "id": "jaipur-india",
            "name": "Jaipur (Pink City)",
            "country": "India",
            "category": "Heritage & Palaces",
            "description": "The vibrant capital of Rajasthan known as the Pink City, famous for grand royal palaces and majestic hill forts.",
            "price_level": "$$",
            "rating": 4.8,
            "best_season": "October - March",
            "top_attractions": ["Hawa Mahal", "Amber Fort", "City Palace", "Jantar Mantar"]
        },
        {
            "id": "varanasi-india",
            "name": "Varanasi",
            "country": "India",
            "category": "Spiritual & Culture",
            "description": "One of the world's oldest continually inhabited cities, renowned for sacred ghats along the holy Ganges River.",
            "price_level": "$",
            "rating": 4.7,
            "best_season": "November - February",
            "top_attractions": ["Dashashwamedh Ghat", "Kashi Vishwanath Temple", "Sarnath", "Ganga Aarti"]
        },
        {
            "id": "goa-india",
            "name": "Goa",
            "country": "India",
            "category": "Beaches & Relaxation",
            "description": "Famous for tropical palm-fringed beaches, historic Portuguese architecture, and vibrant coastal culture.",
            "price_level": "$$",
            "rating": 4.7,
            "best_season": "November - February",
            "top_attractions": ["Baga Beach", "Basilica of Bom Jesus", "Dudhsagar Falls", "Fort Aguada"]
        }
    ]

    for item in destinations:
        doc_id = item["id"]
        db.collection("destinations").document(doc_id).set(item)
        print(f"Seeded destination: {item['name']} ({doc_id})")

if __name__ == "__main__":
    seed_destinations()
