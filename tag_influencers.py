import os
import json
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "influencers"

if not all([MONGODB_URI, OPENAI_API_KEY, DB_NAME, COLLECTION_NAME]):
    print("Error: Missing environment variables. Please check your .env file.")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize MongoDB client
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

from tagging_utils import generate_influencer_tags as generate_tags

def main():
    print("Starting structured influencer tagging process...")
    print(f"Total docs in collection: {collection.estimated_document_count()}")
    
    # Process all documents with a description
    query = {} # Debugging: fetch all
    
    doc_count = collection.count_documents(query)
    print(f"Found {doc_count} documents to process.")
    
    cursor = collection.find(query).limit(5)
    
    count = 0
    updated_count = 0
    
    for doc in cursor:
        count += 1
        channel_desc = doc.get("description") or doc.get("channel_desc") # Fallback
        
        # Optional: check if already has 'structured_tags' to skip optimization
        # if "structured_tags" in doc:
        #     continue

        print(f"Processing: {doc.get('title', doc.get('channel_name', 'Unknown'))} (ID: {doc.get('_id')})")
        print(f"Keys: {list(doc.keys())}")

        channel_name = doc.get("title") or doc.get("channel_name", "Unknown")
        combined_text = f"Channel Name: {channel_name}\nDescription: {channel_desc}"
        
        tag_data = generate_tags(combined_text)
        
        if tag_data:
            print(f"  > Industry: {tag_data.get('industry')}")
            print(f"  > Match Tags: {tag_data.get('matching_tags')}")
            
            # Update the document with new structured data
            # We keep the old 'tags' for backward compatibility if needed, or overwrite.
            # Here we save to a new field 'structured_tags' and also flatten meaningful tags to 'tags'
            
            # Robust list handling
            industry = tag_data.get('industry', '')
            niche = tag_data.get('niche', [])
            matching = tag_data.get('matching_tags', [])
            
            if isinstance(niche, str): niche = [niche]
            if isinstance(matching, str): matching = [matching]
            
            flat_tags = list(set(
                [industry] + 
                (niche if isinstance(niche, list) else []) + 
                (matching if isinstance(matching, list) else [])
            ))
            # Remove empty strings
            flat_tags = [t for t in flat_tags if t]

            update_data = {
                "structured_tags": tag_data,
                "tags": flat_tags, # Updating the main tags field with a flattened version for easy indexing
                "tagging_version": "v2_structured"
            }

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": update_data}
            )
            updated_count += 1
            print("  [Saved]")
        else:
            print("  No tags generated.")
            
    print(f"\nProcessing complete.")
    print(f"Total documents processed: {count}")
    print(f"Total documents updated: {updated_count}")

if __name__ == "__main__":
    main()
