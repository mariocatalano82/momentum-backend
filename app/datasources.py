import random

ASSETS = [
    ("BTC", "Bitcoin"),
    ("ETH", "Ethereum"),
    ("SOL", "Solana"),
    ("ADA", "Cardano"),
    ("AVAX", "Avalanche"),
    ("BNB", "Binance Coin"),
    ("XRP", "Ripple"),
    ("DOT", "Polkadot"),
    ("LINK", "Chainlink"),
    ("MATIC", "Polygon"),
]

def fetch_assets_snapshot():
    assets = []
    for symbol, name in ASSETS:
        change_24h = random.uniform(-14, 14)
        change_1h = change_24h * random.uniform(0.15, 0.35)

        assets.append({
            "symbol": symbol,
            "name": name,
            "change_1h": round(change_1h, 1),
            "change_24h": round(change_24h, 1)
        })
    return assets
