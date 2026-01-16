# Profiles tuning
PROFILES = {
    "balanced": {
        "confidence_bias": 0.0,
        "risk_multiplier": 1.0
    },
    "aggressive": {
        "confidence_bias": 5.0,
        "risk_multiplier": 1.25
    }
}

# Confidence bounds (no fake 95% everywhere)
CONFIDENCE_MIN = 35.0
CONFIDENCE_MAX = 92.0

# Cache (in-memory, simple but effective)
CACHE_TTL_SECONDS = 300  # 5 minutes
