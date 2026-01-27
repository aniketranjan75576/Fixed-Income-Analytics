import pandas as pd

# --- PART 1: FAKE MARKET DATA ---
def get_market_data():
    """
    Returns a DataFrame of market quotes.
    Note: We purposefully use an 'Inverted' curve (Short term > Long term)
    to make the results mathematically interesting.
    """
    data = [
        {"Instrument": "LIBOR_ON", "Maturity": 1/360, "Rate": 0.0550, "Type": "Cash"}, # 5.50%
        {"Instrument": "LIBOR_3M", "Maturity": 0.25, "Rate": 0.0540, "Type": "Cash"},
        {"Instrument": "SWAP_1Y",  "Maturity": 1.0,  "Rate": 0.0520, "Type": "Swap"},
        {"Instrument": "SWAP_2Y",  "Maturity": 2.0,  "Rate": 0.0500, "Type": "Swap"},
        {"Instrument": "SWAP_3Y",  "Maturity": 3.0,  "Rate": 0.0480, "Type": "Swap"},
        {"Instrument": "SWAP_4Y",  "Maturity": 4.0,  "Rate": 0.0460, "Type": "Swap"}, # Added 4Y for smoothness
        {"Instrument": "SWAP_5Y",  "Maturity": 5.0,  "Rate": 0.0450, "Type": "Swap"},
        {"Instrument": "SWAP_10Y", "Maturity": 10.0, "Rate": 0.0420, "Type": "Swap"},
    ]
    return pd.DataFrame(data)