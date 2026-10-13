"""
ShopFinder Algorithms: Sorting Module (ADS & Python Syllabus Unit II & ADS)
Implements:
1. Merge Sort - Divide & Conquer O(N log N)
2. Ascending & Descending sort order
3. Comparison with Python built-in Timsort

Telugu Guide (తెలుగు వివరణ):
- Merge Sort: విభజించు మరియు పాలించు (Divide and Conquer) సూత్రంపై పనిచేస్తుంది.
- జాబితాను రెండు సమాన భాగాలుగా విభజించి, ప్రతి భాగాన్ని క్రమబద్ధీకరించి, చివరలో కలుపుతుంది (Merge చేస్తుంది).
- Time Complexity: O(N log N) అన్ని సందర్భాలలోనూ స్థిరంగా ఉంటుంది (Guaranteed).
"""

from typing import List, Dict, Any, Callable
import time


def merge_sort_products(items: List[Dict[str, Any]], key: str = "min_price", 
                        reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Sorts a list of dictionaries by a given numeric or string key using Merge Sort.
    Supports both ascending (reverse=False) and descending (reverse=True) order.

    Time Complexity: O(N log N)
    Space Complexity: O(N)

    Parameters:
    - items: List of product/offer dictionaries.
    - key: Dictionary key to sort by (e.g., 'min_price', 'rating', 'best_discount').
    - reverse: If True, sorts descending (Highest first). If False, sorts ascending (Lowest first).
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left_half = merge_sort_products(items[:mid], key=key, reverse=reverse)
    right_half = merge_sort_products(items[mid:], key=key, reverse=reverse)

    return _merge(left_half, right_half, key=key, reverse=reverse)


def _merge(left: List[Dict[str, Any]], right: List[Dict[str, Any]], 
           key: str, reverse: bool) -> List[Dict[str, Any]]:
    """
    Helper function to merge two sorted sublists.
    """
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        val_left = left[i].get(key, 0) or 0
        val_right = right[j].get(key, 0) or 0

        # Type safety: handle strings or numbers gracefully
        if isinstance(val_left, str) and not isinstance(val_right, str):
            val_right = str(val_right)
        elif not isinstance(val_left, str) and isinstance(val_right, str):
            val_left = str(val_left)

        condition = (val_left >= val_right) if reverse else (val_left <= val_right)

        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def benchmark_merge_sort(items: List[Dict[str, Any]], key: str = "min_price") -> Dict[str, Any]:
    """
    Benchmarks custom Merge Sort against Python's built-in Timsort (sorted()).
    Validates correctness and measures execution time.
    """
    # 1. Custom Merge Sort
    start_custom = time.perf_counter()
    custom_sorted = merge_sort_products(items, key=key, reverse=False)
    time_custom = (time.perf_counter() - start_custom) * 1000  # ms

    # 2. Python Built-in sorted()
    start_builtin = time.perf_counter()
    builtin_sorted = sorted(items, key=lambda x: x.get(key, 0) or 0)
    time_builtin = (time.perf_counter() - start_builtin) * 1000  # ms

    # Verify both algorithms yield the same prices in order
    custom_vals = [x.get(key, 0) for x in custom_sorted]
    builtin_vals = [x.get(key, 0) for x in builtin_sorted]
    is_identical = (custom_vals == builtin_vals)

    return {
        "is_correct": is_identical,
        "items_count": len(items),
        "custom_merge_sort_ms": round(time_custom, 4),
        "builtin_timsort_ms": round(time_builtin, 4),
        "algorithm": "Merge Sort (Divide and Conquer, O(N log N))",
        "notes": "Custom merge sort guarantees O(N log N) stability across platforms."
    }
