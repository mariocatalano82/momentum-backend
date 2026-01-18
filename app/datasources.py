import requests

def normalize_symbol(raw_symbol, source):
    """Normalizza i simboli per averli uniformi (es. BTC)"""
    s = raw_symbol.upper()
    if source == 'binance':
        return s.replace('USDT', '')
    elif source == 'kraken':
        # Kraken ha simboli strani (es. XXBTZUSD -> BTC)
        mapping = {'XXBT': 'BTC', 'XBT': 'BTC', 'XETH': 'ETH', 'XXRP': 'XRP', 'XDG': 'DOGE'}
        # Rimuove ZUSD o USD finale
        core = s.replace('ZUSD', '').replace('USD', '')
        return mapping.get(core, core)
    return s

def fetch_from_binance():
    """FONTE PRIMARIA: Veloce e completa"""
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data:
            if item['symbol'].endswith("USDT") and float(item['quoteVolume']) > 3000000:
                results.append({
                    "symbol": normalize_symbol(item['symbol'], 'binance'),
                    "change_24h": float(item['priceChangePercent']),
                    # Stimiamo il cambio 1h basandoci sulla volatilità intraday
                    # (High-Low)/Low per dare dinamicità senza scaricare klines pesanti
                    "change_1h_est": (float(item['priceChangePercent']) / 24) * 1.1, 
                    "volume": float(item['quoteVolume'])
                })
        return results
    except Exception as e:
        print(f"⚠️ Binance Error: {e}")
        return None

def fetch_from_kraken():
    """FALLBACK 1: Solida e affidabile"""
    url = "https://api.kraken.com/0/public/Ticker"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('error'):
            return None
            
        results = []
        for pair, details in data['result'].items():
            if pair.endswith("USD") and not pair.endswith("USDT"): # Kraken usa USD reale
                # Kraken format: a=[price, ...], v=[vol_today, vol_24h], p=[vwap_today, vwap_24h]
                open_24h = float(details['o'])
                current = float(details['c'][0])
                change_pct = ((current - open_24h) / open_24h) * 100
                
                results.append({
                    "symbol": normalize_symbol(pair, 'kraken'),
                    "change_24h": change_pct,
                    "change_1h_est": (change_pct / 24) * 1.1,
                    "volume": float(details['v'][1]) * current # Volume approssimativo in USD
                })
        return results
    except Exception as e:
        print(f"⚠️ Kraken Error: {e}")
        return None

def fetch_assets_snapshot():
    """Gestore intelligente del fallback"""
    print("🔄 Fetching data...")
    
    # 1. Prova Binance
    data = fetch_from_binance()
    if data: 
        print(f"✅ Data source: BINANCE ({len(data)} coins)")
        return data
        
    # 2. Se Binance fallisce, prova Kraken
    print("⚠️ Binance failed, switching to KRAKEN...")
    data = fetch_from_kraken()
    if data:
        print(f"✅ Data source: KRAKEN ({len(data)} coins)")
        return data
        
    # 3. Se tutto fallisce
    print("❌ CRITICAL: All datasources failed.")
    return []