"""
ShopFinder Algorithms: Search Module (Unit I, II, & ADS)
Implements:
1. Linear Search - O(N)
2. Binary Search over sorted price/name arrays - O(log N)
3. Trie Data Structure for fast Autocomplete Suggestions - O(L)

Telugu Guide (తెలుగు వివరణ):
- Linear Search: ప్రతి వస్తువును ఒకదాని తర్వాత ఒకటి వరుసగా తనిఖీ చేస్తుంది (Sequential Check).
- Binary Search: క్రమబద్ధీకరించిన (Sorted) లిస్ట్ లో సగం డేటాను విభజిస్తూ O(log N) సమయంలో వెతుకుతుంది.
- Trie (Prefix Tree): యూజర్ టైప్ చేసే మొదటి అక్షరాలను బట్టి తక్షణ సూచనలు (Suggestions) ఇస్తుంది.
"""

from typing import List, Dict, Any, Optional


def linear_search_products(products: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Performs case-insensitive partial matching across product name, brand, model,
    and category using Linear Search.

    Time Complexity: O(N * M) where N is the number of products and M is string length.
    Space Complexity: O(K) where K is the number of matching items.

    Telugu:
    ప్రతి ప్రొడక్ట్ పేరు, బ్రాండ్, లేదా కేటగిరీలో యూజర్ అడిగిన పదం ఉందో లేదో వరుసగా చూస్తుంది.
    """
    if not query or not query.strip():
        return products

    q = query.strip().lower()
    matches = []

    for item in products:
        name = item.get("product_name", "").lower()
        brand = item.get("brand", "").lower()
        model = item.get("model", "").lower()
        cat = item.get("category_name", "").lower()
        desc = item.get("description", "").lower()

        # Partial matching check (Unit I conditional statements)
        if (q in name) or (q in brand) or (q in model) or (q in cat) or (q in desc):
            matches.append(item)

    return matches


def binary_search_by_price(sorted_items: List[Dict[str, Any]], target_price: float, 
                           tolerance: float = 100.0) -> Optional[Dict[str, Any]]:
    """
    Performs Binary Search to locate a product offer closest to target_price
    in an ascendingly sorted list of items.

    Precondition: `sorted_items` MUST be sorted by 'min_price' or 'current_price'.
    Time Complexity: O(log N)
    Space Complexity: O(1)

    Telugu:
    క్రమబద్ధీకరించిన ధరల జాబితాలో మధ్య బిందువు (midpoint) ఆధారంగా టార్గెట్ ధరకు సరిపోయే వస్తువును కనుగొంటుంది.
    """
    if not sorted_items:
        return None

    low = 0
    high = len(sorted_items) - 1
    closest_item = None
    min_diff = float("inf")

    while low <= high:
        mid = (low + high) // 2
        item = sorted_items[mid]
        price = item.get("min_price", item.get("current_price", 0.0))

        diff = abs(price - target_price)
        if diff < min_diff:
            min_diff = diff
            closest_item = item

        if price == target_price:
            return item
        elif price < target_price:
            low = mid + 1
        else:
            high = mid - 1

    # Return closest item if within allowable tolerance
    if min_diff <= tolerance:
        return closest_item
    return closest_item


class TrieNode:
    """Node in the Trie data structure."""
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end_of_word: bool = False
        self.payload: Optional[Dict[str, Any]] = None


class SearchTrie:
    """
    Prefix Tree (Trie) for instantaneous search suggestions and auto-complete.
    Time Complexity for insert: O(L) where L is the word length.
    Time Complexity for autocomplete: O(P + K) where P is prefix length, K is number of suggestions.

    Telugu:
    ట్రై డేటా స్ట్రక్చర్: సెర్చ్ బార్ లో యూజర్ టైప్ చేస్తున్నప్పుడు తక్కువ సమయంలో ఆటోకంప్లీట్ సూచనలను అందిస్తుంది.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, phrase: str, payload: Optional[Dict[str, Any]] = None):
        """Inserts a word or product phrase into the Trie in lower-case."""
        if not phrase:
            return
        node = self.root
        phrase_clean = phrase.strip().lower()
        for char in phrase_clean:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.payload = payload or {"title": phrase}

    def autocomplete(self, prefix: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Returns up to `limit` suggestion phrases matching the given prefix.
        """
        if not prefix or not prefix.strip():
            return []

        node = self.root
        prefix_clean = prefix.strip().lower()

        # Step 1: Navigate to the end of the prefix
        for char in prefix_clean:
            if char not in node.children:
                return []
            node = node.children[char]

        # Step 2: Depth-first search (DFS) to collect completions
        results = []

        def dfs(curr_node: TrieNode, curr_str: str):
            if len(results) >= limit:
                return
            if curr_node.is_end_of_word:
                results.append(curr_node.payload or {"title": curr_str})
            for char, next_node in sorted(curr_node.children.items()):
                dfs(next_node, curr_str + char)
                if len(results) >= limit:
                    break

        dfs(node, prefix_clean)
        return results
