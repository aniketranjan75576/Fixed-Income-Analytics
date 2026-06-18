# Fixed Income Analytics

A Python-based framework for yield curve bootstrapping, parametric curve fitting, and fixed income instrument pricing.

## Overview

This project constructs zero-rate curves from liquid market quotes (deposits and interest rate swaps) using a dual-engine approach. It provides both an **Exact Bootstrapping Engine** with continuous spline interpolation and a **Parametric Engine** based on the Nelson-Siegel-Svensson (NSS) model.

## Project Structure

```text
.
├── instruments.py      # Instrument class definitions and cash flow generation
├── marketData.py       # Market data loader with sample quotes
├── engine.py           # Core engines (Bootstrap & NSS)
├── visualization.py    # Visualization and comparison utilities
├── main.py             # Execution script for curve generation and comparison
└── README.md           # This file
```

## Components

### 1. **instruments.py**
Defines the core instrument classes:

- **`CashFlow`**: Dataclass representing a single cash flow with time and amount
- **`Instrument`**: Abstract base class for all instruments with properties:
  - `name`: Instrument identifier
  - `maturity`: Time to maturity (in years)
  - `rate`: Market quote rate
  - `get_cash_flows()`: Abstract method returning list of cash flows

- **`Deposit`**: Simple interest instrument (cash/LIBOR)
  - Cash flow: `1.0 + r*t` at maturity
  
- **`InterestRateSwap`**: Vanilla interest rate swap
  - Annual coupon payments of `r*dt` plus principal repayment at maturity

### 2. **marketData.py**
Provides market data:

- `get_market_data()`: Returns a pandas DataFrame with market quotes
- Sample data includes:
  - LIBOR quotes (ON, 3M)
  - Swap rates (1Y to 10Y)
  - **Inverted yield curve** for mathematically interesting results

### 3. **engine.py**
Contains the dual yield curve engines:
- **`BootstrapEngine`**: Sequentially solves for implied zero rates using numerical root-finding and returns a smooth, continuous **Natural Cubic Spline**.
- **`NSSEngine`**: Calibrates the 6-parameter **Nelson-Siegel-Svensson (NSS)** model to market data using non-linear optimization for a globally smooth parametric fit.

### 4. **visualization.py**
Features a `CurveVisualizer` that plots raw market data against both the exact bootstrapped spline and the smooth NSS curve for direct visual comparison.

## Key Features

✅ **Dual Curve Engines**: Compare exact local interpolation (Cubic Spline) with smooth global parametric fits (NSS).  
✅ **Non-Linear Optimization**: Uses SciPy's SLSQP to calibrate NSS parameters to market data.  
✅ **Smooth Interpolation**: Employs Natural Cubic Splines to prevent unnatural jumps in the exact curve.  
✅ **Root-Finding**: Uses Newton-Raphson optimization for accurate swap rate bootstrapping.  
✅ **Continuous Compounding**: Standard market convention applied universally.  

## Usage

Run `main.py` to execute the full pipeline and launch the visual dashboard, or use the components directly:

```python
from marketData import get_market_data
from instruments import Deposit, InterestRateSwap
from engine import BootstrapEngine, NSSEngine
from visualization import CurveVisualizer

# 1. Load data and create instruments
df = get_market_data()
instruments = [
    Deposit(r['Instrument'], r['Maturity'], r['Rate']) if r['Type'] == 'Cash' 
    else InterestRateSwap(r['Instrument'], r['Maturity'], r['Rate']) 
    for _, r in df.iterrows()
]

# 2. Build Exact Curve (Cubic Spline)
boot_curve = BootstrapEngine().build_curve(instruments)

# 3. Build Parametric Curve (NSS)
nss_engine = NSSEngine()
nss_curve_func = nss_engine.build_curve(instruments)

print(f"Calibrated NSS Parameters: {nss_engine.params.round(4)}")

# 4. Compare Visually
CurveVisualizer.plot_comparison(boot_curve, nss_curve_func, df)
```

## Requirements

- `numpy`: Numerical computations
- `pandas`: Data handling
- `scipy`: Optimization and Interpolation
- `matplotlib`: Visualization

Install dependencies:
```bash
pip install numpy pandas scipy matplotlib
```

---

**Author**: aniketranjan75576@gmail.com  
