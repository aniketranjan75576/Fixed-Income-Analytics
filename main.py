from marketData import get_market_data
from instruments import Deposit, InterestRateSwap
from engine import BootstrapEngine, NSSEngine
from visualization import CurveVisualizer

if __name__ == "__main__":
    print("Loading FICC Market Data...")
    df = get_market_data()
    
    # Instantiate Instrument Objects
    instruments = []
    for _, row in df.iterrows():
        if row['Type'] == 'Cash':
            instruments.append(Deposit(row['Instrument'], row['Maturity'], row['Rate']))
        else:
            instruments.append(InterestRateSwap(row['Instrument'], row['Maturity'], row['Rate']))

    # ---------------------------------------------------------
    # Engine 1: Exact Bootstrapping
    # ---------------------------------------------------------
    print("Running Bootstrapper Engine...")
    boot_engine = BootstrapEngine()
    boot_curve = boot_engine.build_curve(instruments)
    
    # ---------------------------------------------------------
    # Engine 2: Parametric Optimization
    # ---------------------------------------------------------
    print("Running NSS Optimization Engine...")
    nss_engine = NSSEngine()
    nss_curve_func = nss_engine.build_curve(instruments)
    
    print(f"\nOptimization Complete.")
    print(f"Calibrated NSS Parameters: {nss_engine.params.round(4)}")
    
    # ---------------------------------------------------------
    # Dashboard / Visualization
    # ---------------------------------------------------------
    print("Generating Dashboard...")
    CurveVisualizer.plot_comparison(boot_curve, nss_curve_func, df)