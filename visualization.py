# --- PART 5: VISUALIZATION ---
import matplotlib.pyplot as plt
import numpy as np

class CurveVisualizer:
    @staticmethod
    def plot_curve(curve):
        """
        Generates a dashboard of 3 subplots:
        1. Zero Rate Curve
        2. Discount Factor Curve
        3. Instantaneous Forward Rate (Implied)
        """
        # Generate dense time points for smooth plotting (0 to 30 years)
        t_grid = np.linspace(0.1, 30, 100) 
        
        # Calculate derived values
        zero_rates = [curve.get_zero_rate(t) for t in t_grid]
        discount_factors = [curve.get_discount_factor(t) for t in t_grid]
        
        # Calculate Forward Rates: f(t) approx (R2*t2 - R1*t1) / (t2 - t1)
        # This shows the rate applicable between t and t+dt
        dt = 0.01
        forwards = []
        for t in t_grid:
            # We calculate the 1-day forward rate starting at t
            # R(t) * t is the total yield
            r_t = curve.get_zero_rate(t)
            r_t_dt = curve.get_zero_rate(t + dt)
            
            fwd = (r_t_dt * (t + dt) - r_t * t) / dt
            forwards.append(fwd)

        # --- PLOTTING ---
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Yield Curve Construction Results (Bootstrapped)', fontsize=16)

        # Plot 1: Zero Rates
        axes[0].plot(t_grid, np.array(zero_rates) * 100, label='Zero Rate', color='blue', linewidth=2)
        axes[0].set_title('Zero Coupon Yield Curve')
        axes[0].set_xlabel('Maturity (Years)')
        axes[0].set_ylabel('Rate (%)')
        axes[0].grid(True, linestyle='--', alpha=0.6)
        axes[0].legend()

        # Plot 2: Discount Factors
        axes[1].plot(t_grid, discount_factors, label='Discount Factor', color='green', linewidth=2)
        axes[1].set_title('Discount Factors P(0,t)')
        axes[1].set_xlabel('Maturity (Years)')
        axes[1].set_ylabel('DF')
        axes[1].grid(True, linestyle='--', alpha=0.6)

        # Plot 3: Forward Rates
        axes[2].plot(t_grid, np.array(forwards) * 100, label='Inst. Forward Rate', color='red', linestyle='--')
        axes[2].set_title('Implied Forward Rates')
        axes[2].set_xlabel('Maturity (Years)')
        axes[2].set_ylabel('Rate (%)')
        axes[2].grid(True, linestyle='--', alpha=0.6)
        axes[2].legend()

        plt.tight_layout()
        plt.show()