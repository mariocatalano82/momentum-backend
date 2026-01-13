import requests

def get_crypto_data():
    # Usiamo l'endpoint globale di Binance che restituisce TUTTO il mercato in un colpo solo
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        response = requests.get(url, timeout=10)
        all_tickers = response.json()
        
        formatted_data = []
        for item in all_tickers:
            symbol = item['symbol']
            # Filtriamo: prendiamo solo coppie che finiscono in USDT (es. BTCUSDT)
            # Escludiamo monete "Leveraged" (UP/DOWN) che falsano il momentum
            if symbol.endswith('USDT') and not any(x in symbol for x in ['UP', 'DOWN', 'BEAR', 'BULL']):
                formatted_data.append({
                    "id": symbol.lower(),
                    "symbol": symbol.replace('USDT', '').lower(),
                    "name": symbol.replace('USDT', ''),
                    "price_change_percentage_24h": float(item['priceChangePercent']),
                    "volume_usd": float(item['quoteVolume']) # Volume utile per calcoli predittivi
                })
        
        # Ordiniamo per performance (momentum) così l'app vede subito le migliori
        formatted_data.sort(key=lambda x: x['price_change_percentage_24h'], reverse=True)
        
        print(f"Scanner completato: monitorate {len(formatted_data)} criptovalute.")
        return formatted_data
        
    except Exception as e:
        print(f"Errore Scanner: {e}")
        return []