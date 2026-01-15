import os
import time
import threading
import traceback
from pymongo import MongoClient
from dotenv import load_dotenv
from tagging_utils import generate_influencer_tags, generate_brand_tags, generate_product_tags, get_embedding

load_dotenv(override=True)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

if not all([MONGODB_URI, DB_NAME]):
    print("Error: Missing env vars.")
    exit(1)

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def process_influencers():
    collection = db["influencers"]
    # Check for untagged OR missing embedding
    query = {"$or": [{"structured_tags": {"$exists": False}}, {"embedding": {"$exists": False}}]}
    cursor = collection.find(query).limit(5)  # Batch size 5
    
    count = 0
    for doc in cursor:
        try:
            name = doc.get("channel_name", "Unknown")
            desc = doc.get("channel_desc", "")
            print(f"[Influencer] Updating: {name}")

            # 1. Generate Tags if missing
            tag_data = doc.get("structured_tags")
            flat_tags = doc.get("tags", [])
            embedding = doc.get("embedding")
            
            if not tag_data:
                combined_text = f"Channel Name: {name}\nDescription: {desc}"
                tag_data = generate_influencer_tags(combined_text)
                
                if tag_data:
                    niche = tag_data.get('niche', [])
                    if isinstance(niche, str): niche = [niche]
                    
                    matching = tag_data.get('matching_tags', [])
                    if isinstance(matching, str): matching = [matching]

                    flat_tags = list(set(
                        [tag_data.get('industry', '')] + 
                        niche + 
                        matching
                    ))
                    flat_tags = [t for t in flat_tags if t]

            # 2. Generate Embedding if missing
            if (tag_data and not embedding) or (tag_data and not doc.get("embedding")):
                tags_list = tag_data.get('matching_tags', [])
                if isinstance(tags_list, str): tags_list = [tags_list]
                text_for_embed = f"{name} {desc} {' '.join(tags_list)}"
                embedding = get_embedding(text_for_embed)

            if tag_data and embedding:
                update_data = {
                    "structured_tags": tag_data,
                    "tags": flat_tags,
                    "embedding": embedding,
                    "tagging_version": "v_poll_1.0",
                    "last_updated": time.time()
                }

                collection.update_one({"_id": doc["_id"]}, {"$set": update_data})
                print(f"  ✅ [Influencer] Done: {name}")
                count += 1
                time.sleep(1)
                
        except Exception as e:
            print(f"  ❌ [Influencer] Error on {doc.get('_id')}: {e}")

    return count

def process_brands():
    collection = db["brands"]
    # Check for untagged OR missing embedding
    query = {"$or": [{"structured_tags": {"$exists": False}}, {"embedding": {"$exists": False}}]}
    cursor = collection.find(query).limit(5)  # Batch size 5
    
    count = 0
    for doc in cursor:
        try:
            name = doc.get("name", "Unknown")
            print(f"[Brand] Updating: {name}")
            
            # 1. Generate Tags if missing
            tag_data = doc.get("structured_tags")
            flat_tags = doc.get("tags", [])
            embedding = doc.get("embedding")
            
            if not tag_data:
                tag_data = generate_brand_tags(doc)
                
                if tag_data:
                    b_vals = tag_data.get('brand_values', [])
                    if isinstance(b_vals, str): b_vals = [b_vals]
                    
                    matching = tag_data.get('matching_tags', [])
                    if isinstance(matching, str): matching = [matching]

                    flat_tags = list(set(
                        [tag_data.get('industry', '')] + 
                        [tag_data.get('product_category', '')] +
                        b_vals +
                        matching
                    ))
                    flat_tags = [t for t in flat_tags if t]
            
            # 2. Generate Embedding if missing
            if (tag_data and not embedding) or (tag_data and not doc.get("embedding")):
                industry = tag_data.get('industry', '')
                prod_cat = tag_data.get('product_category', '')
                tags_str = " ".join(flat_tags)
                text_for_embed = f"{name} {industry} {prod_cat} {tags_str}"
                embedding = get_embedding(text_for_embed)

            if tag_data and embedding:
                update_data = {
                    "structured_tags": tag_data,
                    "tags": flat_tags,
                    "embedding": embedding,
                    "tagging_version": "v_poll_1.0",
                    "last_updated": time.time()
                }
                
                collection.update_one({"_id": doc["_id"]}, {"$set": update_data})
                print(f"  ✅ [Brand] Done: {name}")
                count += 1
                time.sleep(1)
        except Exception as e:
            print(f"  ❌ [Brand] Error on {doc.get('_id')}: {e}")
            
    return count

def process_products():
    collection = db["products"]
    # Check for untagged OR missing embedding
    query = {"$or": [{"structured_tags": {"$exists": False}}, {"embedding": {"$exists": False}}]}
    cursor = collection.find(query).limit(5)  # Batch size 5
    
    count = 0
    for doc in cursor:
        try:
            name = doc.get("title") or doc.get("name", "Unknown")
            print(f"[Product] Updating: {name}")
            
            # 1. Generate Tags if missing
            tag_data = doc.get("structured_tags")
            flat_tags = doc.get("tags", [])
            
            if not tag_data:
                tag_data = generate_product_tags(doc)
                if tag_data:
                    cat = tag_data.get('category', '')
                    feats = tag_data.get('features', [])
                    usage = tag_data.get('usage_scenario', [])
                    matching = tag_data.get('matching_tags', [])
                    
                    if isinstance(feats, str): feats = [feats]
                    if isinstance(usage, str): usage = [usage]
                    if isinstance(matching, str): matching = [matching]

                    flat_tags = list(set([cat] + feats + usage + matching))
                    flat_tags = [t for t in flat_tags if t]

            # 2. Generate Embedding (Always run if we are here)
            # Use data from tag_data if available, else doc
            cat_text = tag_data.get('category', '') if tag_data else doc.get('category', '')
            desc = doc.get("description", "")
            tags_str = " ".join(flat_tags)
            
            text_embed = f"{name} {cat_text} {desc} {tags_str}"
            embedding = get_embedding(text_embed)
            
            if tag_data and embedding:
                update_data = {
                    "structured_tags": tag_data,
                    "tags": flat_tags,
                    "embedding": embedding,
                    "tagging_version": "v_poll_1.0",
                    "last_updated": time.time()
                }
                
                collection.update_one({"_id": doc["_id"]}, {"$set": update_data})
                print(f"  ✅ [Product] Done: {name}")
                count += 1
                time.sleep(1)
        except Exception as e:
            print(f"  ❌ [Product] Error on {doc.get('_id')}: {e}")
            traceback.print_exc()

    return count

def run_polling_loop():
    print("🚀 Auto-Tagging Service Started (Interval: 3 sec)")
    print("   Targets: Influencers, Brands, Products")
    
    while True:
        print("\n⏰ Starting Polling Cycle...")
        
        try:
            c_inf = process_influencers()
            c_brd = process_brands()
            c_prd = process_products()
            
            total = c_inf + c_brd + c_prd
            if total > 0:
                print(f"✅ Cycle Complete. Updated {total} docs (I:{c_inf}, B:{c_brd}, P:{c_prd}).")
            else:
                print("💤 No new data found. Sleeping...")
                
        except Exception as e:
            print(f"❌ Critical Error in Polling Loop: {e}")
        
        # Sleep 3 seconds
        time.sleep(3)

if __name__ == "__main__":
    run_polling_loop()
