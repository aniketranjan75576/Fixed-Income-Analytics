# Fixed Income Analytics

A Python-based framework for yield curve bootstrapping and fixed income instrument pricing using market data.

## Overview

This project implements a **yield curve bootstrapping engine** that constructs a zero-rate curve from market quotes of liquid instruments (deposits and interest rate swaps). The engine uses both analytical solutions (for deposits) and numerical optimization (for swaps) to solve for implied zero rates.

## Project Structure

```
.
├── instruments.py      # Instrument class definitions and cash flow generation
├── marketData.py       # Market data loader with fake quotes
├── engine.py           # Yield curve bootstrapping engine
├── visualization.py    # Visualization and plotting utilities
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
Core bootstrapping engine:

- **`YieldCurve`**: Manages the zero-rate curve
  - Linear interpolation of zero rates
  - Discount factor calculation using continuous compounding: `DF = e^(-r*t)`

- **`BootstrapEngine`**: Builds the yield curve
  - **Deposits**: Analytical solution using `z = -ln(DF) / t`
  - **Swaps**: Numerical solution using Newton-Raphson optimization
  - Sorts instruments by maturity for sequential bootstrapping

### 4. **visualization.py**
Visualization utilities for yield curves:

- **`CurveVisualizer`**: Plotting class with static methods:
  - `plot_zero_curve()`: Plots zero-rate curve with bootstrapped points
  - `plot_discount_factors()`: Visualizes discount factor curve
  - `plot_forward_rates()`: Shows implied 1-year forward rates
  - `plot_all()`: Creates a 3-subplot dashboard with all curves

Uses matplotlib for publication-quality plots with grid, legends, and proper formatting.

## Key Features

✅ **Analytical Solution for Deposits**: Direct calculation of zero rates  
✅ **Numerical Optimization for Swaps**: Newton-Raphson root-finding  
✅ **Linear Interpolation**: Forward-looking rate estimation during optimization  
✅ **Continuous Compounding**: Standard market convention  
✅ **Inverted Yield Curve**: Realistic market scenario  

## Usage

```python
from marketData import get_market_data
from instruments import Deposit, InterestRateSwap
from engine import BootstrapEngine
from visualization import CurveVisualizer

# 1. Get market data
market_df = get_market_data()

# 2. Create instruments
instruments = []
for _, row in market_df.iterrows():
    if row['Type'] == 'Cash':
        instruments.append(Deposit(
            name=row['Instrument'],
            maturity=row['Maturity'],
            rate=row['Rate']
        ))
    else:  # Swap
        instruments.append(InterestRateSwap(
            name=row['Instrument'],
            maturity=row['Maturity'],
            rate=row['Rate']
        ))

# 3. Build curve
engine = BootstrapEngine()
curve = engine.build_curve(instruments)

# 4. Use the curve
zero_rate_at_2y = curve.get_zero_rate(2.0)
discount_factor_at_2y = curve.get_discount_factor(2.0)

# 5. Visualize the curve
visualizer = CurveVisualizer()
visualizer.plot_zero_curve(curve)
visualizer.plot_discount_factors(curve)
visualizer.plot_forward_rates(curve)
# Or plot all in one dashboard:
visualizer.plot_all(curve, show=True)
```

## Output Example

```
Instrument      | Maturity | Market Rate | Solved Zero Rate
------------------------------------------------------------
LIBOR_ON        | 0.00    | 5.50%       | 5.5006%
LIBOR_3M        | 0.25    | 5.40%       | 5.3970%
SWAP_1Y         | 1.00    | 5.20%       | 5.1924%
SWAP_2Y         | 2.00    | 5.00%       | 4.9918%
SWAP_3Y         | 3.00    | 4.80%       | 4.7931%
...
```

## Requirements

- `numpy`: Numerical computations
- `pandas`: Data handling
- `scipy`: Optimization (Newton-Raphson)
- `matplotlib`: Visualization and plotting

Install dependencies:
```bash
pip install numpy pandas scipy matplotlib
```

## Mathematical Details

### Continuous Compounding
$$DF(t) = e^{-r(t) \cdot t}$$

### Deposit Pricing
Simple interest: $PV = \frac{1}{1 + r \cdot t}$

Zero rate: $z = -\frac{\ln(DF)}{t}$

### Swap Pricing
$$PV = \sum_{i=1}^{n} c \cdot DF(t_i) + 1.0 \cdot DF(T)$$

where $c$ is the annual coupon and $T$ is maturity.

## Notes

- Instruments must be **sorted by maturity** for proper bootstrapping
- The curve uses **linear interpolation** for rate estimation between known points
- Swaps are assumed to be **par instruments** (PV = 1.0) for pricing
- Annual coupon frequency assumed for simplicity

## License

MIT License

---

**Author**: Fixed Income Analytics Project  
**Date**: January 2026
