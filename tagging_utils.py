import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Ensure env vars are loaded with override
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_influencer_tags(channel_data_text):
    """
    Generates structured tags for an influencer based on channel data (Name + Description).
    """
    if not channel_data_text:
        return None

    prompt = f"""
    Act as a Senior AI Data Expert specializing in Influencer Marketing in Korea.
    Analyze the following YouTube channel information and extract a structured "Unified Tag Profile".
    
    CRITICAL INSTRUCTION:
    - If the Channel Name or Description contains explicit keywords, you MUST prioritize them for the 'industry' field.
    - Examples:
      - '육아', '맘', '키즈', 'Baby', 'Parenting' -> industry: '육아'
      - '게임', 'Game', 'Gaming', 'TV' (if context is game) -> industry: '게임'
      - '차', 'Car', 'Auto', '모터스' -> industry: '자동차'
      - '뷰티', 'Beauty' -> industry: '뷰티'
      - '푸드', 'Food', '요리', '레시피' -> industry: '푸드'
    - Do NOT default to 'Lifestyle' if a specific keyword exists in the title.
    
    Channel Data:
    "{channel_data_text}"
    
    Construct a JSON object with the following fields (ALL VALUES MUST BE IN KOREAN):
    1. industry: The broader industry (e.g., 뷰티, 패션, 테크, 게임, 푸드, 여행, 라이프스타일, 육아, 키즈, 운동, 자동차 etc).
    2. niche: valid sub-categories (e.g., '저가 코스프레', '가성비 여행', '데스크 셋업').
    3. content_style: The format/vibe (e.g., '브이로그', '상세 리뷰', '튜토리얼', '쇼츠').
    4. audience_demographic: Inferred target audience (e.g., '20대 대학생', '30대 직장인').
    5. matching_tags: 5-10 core keywords for matching.
    6. brand_affinity: What kind of brands would be a perfect match?
    7. confidence_score: Confidence (0.0 - 1.0).

    Output STRICT JSON only.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert data analyst. Output only valid JSON. Ensure all text values are in Korean."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error generating influencer tags: {e}")
        return None

def generate_brand_tags(brand_doc):
    """
    Generates structured tags for a brand based on its profile.
    """
    context = f"""
    Brand Name: {brand_doc.get("name", "Unknown")}
    Industry: {brand_doc.get("industry", "")}
    Product Category: {brand_doc.get("product_category", "")}
    Target Audience: {brand_doc.get("target_audience", "")}
    Positioning: {brand_doc.get("positioning", "")}
    """

    prompt = f"""
    Act as a Senior Brand Strategist in Korea.
    Analyze the following brand profile and extract a structured "Unified Tag Profile".
    
    Brand Profile:
    "{context}"
    
    Construct a JSON object with the following fields (ALL VALUES MUST BE IN KOREAN):
    1. industry: Broader industry category.
    2. product_category: Specific product niche.
    3. brand_values: 3-5 keywords describing ethos.
    4. target_demographic: Standardized detailed demographic.
    5. marketing_goals: Inferred marketing goals.
    6. influencer_affinity: Types of influencers that match.
    7. matching_tags: 5-10 core keywords for matching.
    8. confidence_score: Confidence (0.0 - 1.0).

    Output STRICT JSON only.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert brand analyst. Output only valid JSON. Ensure all text values are in Korean."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error generating brand tags: {e}")
        return None

def generate_product_tags(product_doc):
    """
    Generates structured tags for a product based on its description.
    """
    context = f"""
    Product Name: {product_doc.get("title") or product_doc.get("name", "Unknown Product")}
    Category (Raw): {product_doc.get("category") or ""}
    Price: {product_doc.get("price") or ""}
    Description: {(product_doc.get("description") or "")[:1000]} 
    """

    prompt = f"""
    Act as an e-commerce AI Specialist in Korea.
    Analyze the following product information and extract a structured "Unified Tag Profile".
    
    Product Info:
    "{context}"
    
    Construct a JSON object with the following fields (ALL VALUES MUST BE IN KOREAN):
    1. category: Refined classification (e.g., '스마트워치', '러닝화'). For ANY vehicle (EV, Hybrid, Car), output '자동차'. If 'Slim9'/'슬림나인'/'편해브라'/'네모팬티', output '패션'. If 'Logitech'/'로지텍', output 'IT'.
    2. features: List of 3-5 key features. If Slim9, include '편안함', '신축성'. If Logitech, include '반응속도', '내구성'.
    3. target_audience: Who is this for?
    4. usage_scenario: When/Where to use? If Slim9, MUST include '운동', '육아', '데일리'. If Logitech, MUST include '게임', '업무'.
    2. features: List of 3-5 key features (e.g., '방수', '노이즈 캔슬링', '초경량').
    3. target_audience: Who is this for? (e.g., '2030 직장인', '학생', '게이머').
    4. usage_scenario: When/Where to use? (e.g., '출퇴근', '운동', '여행').
    5. matching_tags: 5-10 core keywords for search optimization.
    6. confidence_score: Confidence (0.0 - 1.0).

    Output STRICT JSON only.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert product analyst. Output only valid JSON. Ensure all text values are in Korean."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error generating product tags: {e}")
        return None

def get_embedding(text):
    """
    Generates a vector embedding for the given text using OpenAI 'text-embedding-3-small'.
    """
    if not text:
        return None

    try:
        # Simplify text to reduce token usage and noise
        text = text.replace("\n", " ")[:8000] 
        
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
