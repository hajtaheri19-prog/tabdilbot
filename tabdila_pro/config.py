import os

# External endpoints
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
TGJU_URL = "https://api.tgju.org/v1/market/overview"
TSETMC_URL = "http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx"

# Caching
CACHE_TIME_SECONDS = int(os.getenv("TABDILA_CACHE_SECONDS", "300"))

# Networking
DEFAULT_TIMEOUT = 8
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)










