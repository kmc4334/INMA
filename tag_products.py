import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from tagging_utils import generate_product_tags

load_dotenv(override=True)

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "products"

if not all([MONGODB_URI, DB_NAME]):
    print("Error: Missing environment variables.")
    exit(1)

# Initialize Clients
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

def main():
    print(f"Starting product tagging process for '{COLLECTION_NAME}'...")
    
    # Process all products. Can add filter like {"structured_tags": {"$exists": False}}
    cursor = collection.find({})
    
    count = 0
    updated_count = 0
    
    for doc in cursor:
        count += 1
        name = doc.get("name", "Unknown")
        print(f"Processing: {name} (ID: {doc.get('_id')})")
        
        tag_data = generate_product_tags(doc)
        
        if tag_data:
            print(f"  > Category: {tag_data.get('category')}")
            print(f"  > Match Tags: {tag_data.get('matching_tags')}")
            
            # Prepare flattened tags
            cat = tag_data.get('category', '')
            feats = tag_data.get('features', [])
            usage = tag_data.get('usage_scenario', [])
            matching = tag_data.get('matching_tags', [])
            
            if isinstance(feats, str): feats = [feats]
            if isinstance(usage, str): usage = [usage]
            if isinstance(matching, str): matching = [matching]

            flat_tags = list(set(
                [cat] + feats + usage + matching
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
            
            # Rate limiting
            time.sleep(0.5)
        else:
            print("  No tags generated.")
            
    print(f"\nProcessing complete.")
    print(f"Total documents processed: {count}")
    print(f"Total documents updated: {updated_count}")

if __name__ == "__main__":
    main()
