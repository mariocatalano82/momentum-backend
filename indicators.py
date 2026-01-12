import numpy as np

def momentum(change_1h):
    return np.tanh(change_1h / 5)

def volume_score(volume):
    return np.tanh(volume / 1e9)

def rsi_score(rsi=50):
    if rsi < 30:
        return 0.6
    if rsi > 70:
        return -0.6
    return 0.4

def trend_score(change_1h):
    return 0.5 if change_1h > 0 else -0.5

def volatility_score(change_1h):
    return -abs(change_1h) / 10
