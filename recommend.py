import sys
from matching_engine import MatchingEngine

sys.stdout.reconfigure(encoding='utf-8')

def match_product(query_name):
    engine = MatchingEngine()
    
    # 1. Find the product
    print(f"🔎 상품 검색 중: '{query_name}'...")
    product = engine.products.find_one({"name": {"$regex": query_name, "$options": "i"}})
    
    if not product:
        # Fallback to verify if it's in 'title' or similar
        product = engine.products.find_one({"title": {"$regex": query_name, "$options": "i"}})
        
    if not product:
        print(f"❌ 상품을 찾을 수 없습니다.")
        return

    print(f"✅ 상품 발견: {product.get('title') or product.get('name')}")
    
    # Check for embedding and wait if missing
    if not product.get("embedding"):
        import time
        print("⏳ 태깅/임베딩 생성 대기 중 (최대 30초)...")
        for _ in range(10):  # 10 * 3s = 30s
            time.sleep(3)
            # Reload product
            product = engine.products.find_one({"_id": product["_id"]})
            if product.get("embedding"):
                print("✅ 임베딩 생성 완료.")
                break
        else:
            print("⚠️ 경고: 임베딩 생성 시간 초과. 결과가 부정확할 수 있습니다.")

    print(f"   카테고리: {product.get('structured_tags', {}).get('category')}")
    print("-" * 50)
    
    # 2. Run Matching
    recommendations = engine.find_influencers_for_product(product, limit=5)
    
    if not recommendations:
        print("❌ 적합한 인플루언서를 찾지 못했습니다.")
        return

    # 3. Display Results
    print(f"🏆 추천 인플루언서 TOP 5:")
    print("=" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        inf = rec["influencer"]
        score = rec["score"]
        details = rec["details"]
        
        name = inf.get("title") or inf.get("channel_name")
        industry = inf.get("structured_tags", {}).get("industry", "N/A")
        subscribers = inf.get("stats", {}).get("subscribers", 0)
        email = inf.get("email", "N/A")
        
        print(f"{i}. {name} (매칭 점수: {score:.2f})")
        print(f"   카테고리: {industry} | 구독자: {subscribers:,}")
        print(f"   📧 이메일: {email}")
        print(f"   🔍 유사도: {details['similarity']} | 키워드 일치: {details['keyword_overlap']}")
        print(f"   📈 참여율 점수: {details['er_score']}")
        print("-" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recommend.py <product_name>")
        print("Example: python recommend.py 네모팬티")
    else:
        product_name = " ".join(sys.argv[1:])
        match_product(product_name)
