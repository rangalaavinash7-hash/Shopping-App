"""
ShopFinder Algorithms: Recommendations & Priority Queue Module (ADS)
Implements:
1. Min-Heap (Priority Queue) to retrieve top lowest-priced offers in O(K log N)
2. Best-Value Recommendation Engine using Multi-Criteria Weighted Scoring

Telugu Guide (తెలుగు వివరణ):
- Min-Heap / Priority Queue: అతి తక్కువ ధర కలిగిన ఆఫర్లను కనుగొనడానికి మొత్తం లిస్ట్ సార్ట్ చేయకుండా O(K log N) సమయంలో వేగంగా వెలికితీస్తుంది.
- Best-Value Recommendation: కేవలం ధర మాత్రమే కాకుండా రేటింగ్, డిస్కౌంట్, డెలివరీ ఛార్జీలను కూడా లెక్కించి వినియోగదారునికి ఉత్తమ డీల్ ని సిఫార్సు చేస్తుంది.
"""

import heapq
from typing import List, Dict, Any


def get_lowest_price_offers_heap(offers: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
    """
    Extracts the top K lowest total-cost offers using a Min-Heap / Priority Queue.

    Time Complexity: O(N + K log N) using heapq.nsmallest
    Space Complexity: O(N) or O(K)

    Telugu:
    హీప్ (Heap) నిర్మాణం ద్వారా కనీస ధర ఉన్న K ఆఫర్లను సమర్థవంతంగా వేరుచేస్తుంది.
    """
    if not offers:
        return []

    # Use total_cost (current_price + delivery_charge) as the primary heap sorting key
    return heapq.nsmallest(
        k,
        offers,
        key=lambda offer: offer.get("total_cost", offer.get("current_price", 0.0) + offer.get("delivery_charge", 0.0))
    )


def calculate_product_recommendation_score(product: Dict[str, Any], target_budget: float = 0.0) -> float:
    """
    Computes a composite 'Value for Money' score from 0 to 100 based on:
    - Rating (35% weight)
    - Verified Discount % (25% weight)
    - Delivery Charge penalty (15% weight)
    - Budget Fit (25% weight)

    Telugu:
    ప్రతి ప్రొడక్ట్ కు రేటింగ్, డిస్కౌంట్, బడ్జెట్ అనుకూలత ఆధారంగా సమగ్ర విలువ స్కోర్ (0-100) లెక్కిస్తుంది.
    """
    score = 0.0

    # 1. Rating contribution (0 to 5 mapped to 35 points)
    rating = float(product.get("best_rating", product.get("rating", 4.0)) or 4.0)
    score += (rating / 5.0) * 35.0

    # 2. Discount contribution (0% to 70% mapped to 25 points)
    discount = float(product.get("best_discount", product.get("discount_percentage", 0)) or 0)
    discount_clamped = min(discount, 70.0)
    score += (discount_clamped / 70.0) * 25.0

    # 3. Delivery charge bonus / penalty
    offers = product.get("offers", [])
    if offers:
        best_del = min(o.get("delivery_charge", 0.0) for o in offers)
    else:
        best_del = float(product.get("delivery_charge", 0.0) or 0.0)

    if best_del == 0.0:
        score += 15.0  # Free delivery bonus!
    elif best_del <= 50.0:
        score += 8.0
    else:
        score += 2.0

    # 4. Budget proximity contribution (25 points)
    price = float(product.get("min_price", product.get("current_price", 0.0)) or 0.0)
    if target_budget > 0:
        ratio = price / target_budget
        if 0.5 <= ratio <= 1.0:
            score += 25.0  # Fits comfortably under budget
        elif 0.2 <= ratio < 0.5:
            score += 20.0  # Great bargain
        elif 1.0 < ratio <= 1.15:
            score += 10.0  # Slightly exceeds budget
        else:
            score += 5.0
    else:
        # Default baseline if no budget filter specified
        score += 20.0

    return round(score, 1)


def rank_recommended_products(products: List[Dict[str, Any]], target_budget: float = 0.0, 
                             top_n: int = 6) -> List[Dict[str, Any]]:
    """
    Scores and ranks products to return the top N best-value recommendations.
    """
    scored = []
    for p in products:
        p_copy = dict(p)
        score = calculate_product_recommendation_score(p_copy, target_budget)
        p_copy["recommendation_score"] = score
        scored.append(p_copy)

    # Sort descending by recommendation score
    scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored[:top_n]
