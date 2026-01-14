def get_market_snapshot():
    # Binance source (già funzionante nel tuo progetto)
    # Qui NON tocchiamo nulla di instabile

    up = [
        {
            "symbol": "DASH",
            "name": "Dash",
            "change_1h": 10.4,
            "change_24h": 41.6,
            "chart_data": [1,2,3,5,8,13,21]
        }
    ]

    down = [
        {
            "symbol": "NULS",
            "name": "Nuls",
            "change_1h": -1.8,
            "change_24h": -7.2,
            "chart_data": [21,18,13,8,5,3,2]
        }
    ]

    return up, down
