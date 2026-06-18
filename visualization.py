import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline

class CurveVisualizer:
    @staticmethod
    def plot_comparison(boot_curve, nss_curve_func, market_data_df):
        """
        Plots the exact Bootstrapped Spline against the smooth NSS Parametric curve.
        """
        t_grid = np.linspace(0.1, 30, 200)
        
        spline_rates = boot_curve(t_grid)
        
        # 3. Generate NSS rates from the optimized function
        nss_rates = [nss_curve_func(t) for t in t_grid]
        
        # --- PLOTTING ---
        plt.figure(figsize=(10, 6))
        
        # Plot Market Data Points (Black Dots)
        plt.scatter(market_data_df['Maturity'], market_data_df['Rate'] * 100, 
                    color='black', zorder=5, label='Raw Market Quotes')
        
        # Plot Exact Spline Curve (Blue Line)
        plt.plot(t_grid, spline_rates * 100, color='blue', linestyle='-', 
                 linewidth=2, label='Bootstrapped (Cubic Spline)')
        
        # Plot Smooth NSS Curve (Red Dashed Line)
        plt.plot(t_grid, np.array(nss_rates) * 100, color='red', linestyle='--', 
                 linewidth=2, label='NSS Parametric Fit')
        
        plt.title("Yield Curve Construction: Exact Spline vs. Smooth NSS", fontsize=14)
        plt.xlabel("Maturity (Years)", fontsize=12)
        plt.ylabel("Zero Rate (%)", fontsize=12)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend(fontsize=12)
        plt.tight_layout()
        plt.show()