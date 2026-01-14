import random

def get_crypto_data():
    coins = [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("SOL", "Solana"),
        ("BNB", "Binance Coin"),
        ("XRP", "Ripple"),
        ("ADA", "Cardano"),
        ("DOT", "Polkadot"),
        ("AVAX", "Avalanche"),
        ("DOGE", "Dogecoin"),
        ("LINK", "Chainlink"),
    ]

    data = []

    for symbol, name in coins:
        change_24h = round(random.uniform(-8, 8), 2)
        data.append({
            "symbol": symbol,
            "name": name,
            "change_1h": round(change_24h / 4, 2),
            "change_24h": change_24h,
            "probability": min(95, max(30, abs(change_24h) * 10)),
            "explanation_simple":
                "Relative short-term strength"
                if change_24h > 0
                else "Relative short-term weakness",
            "explanation_technical":
                "Momentum based on price change (mock)",
            "score": change_24h,
        })

    return data
