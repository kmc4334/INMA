import os
import json
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables with override to ensure correct API key
load_dotenv(override=True)

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "brands" # Explicitly targeting brands

if not all([MONGODB_URI, OPENAI_API_KEY, DB_NAME]):
    print("Error: Missing environment variables. Please check your .env file.")
    exit(1)

# Initialize Clients
client = OpenAI(api_key=OPENAI_API_KEY)
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

from tagging_utils import generate_brand_tags

# removed local generate_brand_tags definition


def main():
    print(f"Starting structured tagging process for '{COLLECTION_NAME}'...")
    
    # Process all brands - we can filter if needed, e.g., {"structured_tags": {"$exists": False}}
    cursor = collection.find({})
    
    count = 0
    updated_count = 0
    
    for doc in cursor:
        count += 1
        name = doc.get("name", "Unknown")
        print(f"Processing: {name} (ID: {doc.get('_id')})")
        
        # Skip if very little info is available
        if not doc.get("industry") and not doc.get("product_category"):
            print("  Skipping: Insufficient data.")
            continue

        tag_data = generate_brand_tags(doc)
        
        if tag_data:
            print(f"  > Industry: {tag_data.get('industry')}")
            print(f"  > Match Tags: {tag_data.get('matching_tags')}")
            
            # Prepare flattened tags
            flat_tags = list(set(
                [tag_data.get('industry', '')] + 
                [tag_data.get('product_category', '')] +
                tag_data.get('brand_values', []) +
                tag_data.get('matching_tags', [])
            ))
            flat_tags = [t for t in flat_tags if t]

            update_data = {
                "structured_tags": tag_data,
                "tags": flat_tags,
                "tagging_version": "v1_structured"
            }

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": update_data}
            )
            updated_count += 1
            print("  [Saved]")
            
            # Rate limiting to be safe
            time.sleep(0.5)
        else:
            print("  No tags generated.")
            
    print(f"\nProcessing complete.")
    print(f"Total documents processed: {count}")
    print(f"Total documents updated: {updated_count}")

if __name__ == "__main__":
    main()
