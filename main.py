from marketData import get_market_data
from instruments import Instrument, Deposit, InterestRateSwap
from engine import BootstrapEngine
from visualization import CurveVisualizer

if __name__ == "__main__":
    # 1. Load Data
    df = get_market_data()
    
    # 2. Create Objects
    my_instruments = []
    for _, row in df.iterrows():
        if row['Type'] == 'Cash':
            my_instruments.append(Deposit(row['Instrument'], row['Maturity'], row['Rate']))
        else:
            my_instruments.append(InterestRateSwap(row['Instrument'], row['Maturity'], row['Rate']))

    # 3. Run Bootstrapper
    engine = BootstrapEngine()
    final_curve = engine.build_curve(my_instruments)
    print("\n--- DONE: Curve Built Successfully ---")

    # 4. Visualize
    print("Generating Plots...")
    CurveVisualizer.plot_curve(final_curve)