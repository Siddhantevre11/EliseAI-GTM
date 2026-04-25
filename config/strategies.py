# Strategy routing rules for enrichment pipeline

KNOWN_GIANTS = [
    "greystar", "asset living", "equity residential", "avalonbay", "maa",
    "camden property trust", "bell partners", "bh management", "fpi management",
    "westlake management", "landmark", "lincoln property", "related",
    "conifer residential", "campus", "harbor", "century living", "湖水 living",
    "lincoln property", "river", "star", "grove", "pin", "oak", "park", "haven",
    "vista",
]

TIER_1_METROS = [
    "new york", "los angeles", "chicago", "houston", "austin", "phoenix",
    "atlanta", "dallas", "san francisco", "boston", "seattle", "denver",
    "miami", "d.c.", "washington", "san diego", "san jose", "nashville",
    "raleigh", "charlotte",
]

TIER_2_METROS = [
    "denver", "seattle", "orlando", "portland", "charlotte", "raleigh",
    "nashville", "tampa", "minneapolis", "pittsburgh", "cleveland",
    "salt lake", "las vegas", "irvine", "anaheim", "jersey city", "burbank",
    "albuquerque", "richmond", "virginia beach",
]


def get_strategy(company: str, city: str, state: str) -> str:
    company_lower = company.lower()
    city_lower = city.lower()

    if any(g in company_lower for g in KNOWN_GIANTS):
        return "A"
    if any(m in city_lower for m in TIER_1_METROS):
        return "A"
    if any(m in city_lower for m in TIER_2_METROS):
        return "B"
    return "C"


def get_apis_for_strategy(strategy: str) -> list[str]:
    """
    Return list of APIs to call based on strategy.
    
    Strategy A (Full): All APIs for priority targets
    Strategy B (Core): Market + company data (skip DDG for speed)
    Strategy C (Minimal): Core market data only
    """
    if strategy == "A":
        # Full enrichment: Census + FRED + News + WalkScore + DuckDuckGo
        return ["census", "fred", "news", "walkscore", "ddg"]
    if strategy == "B":
        # Core: Census + News + WalkScore (skip DDG for speed)
        return ["census", "news", "walkscore"]
    # Minimal: Census + WalkScore (always get walkability data)
    return ["census", "walkscore"]