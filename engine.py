import numpy as np
from typing import List
from scipy.optimize import newton
from scipy.interpolate import interp1d
from instruments import Instrument, Deposit, InterestRateSwap

# --- PART 3: BOOTSTRAP ENGINE ---

class YieldCurve:
    def __init__(self):
        # We start with t=0, rate=0 (just an anchor)
        self.times = [0.0]
        self.zero_rates = [0.0]

    def add_point(self, t, r):
        self.times.append(t)
        self.zero_rates.append(r)

    def get_zero_rate(self, t_target):
        # Linear Interpolation of Zero Rates
        # 'fill_value="extrapolate"' handles looking forward during optimization
        interpolator = interp1d(self.times, self.zero_rates, kind='linear', fill_value="extrapolate")
        return float(interpolator(t_target))

    def get_discount_factor(self, t):
        r = self.get_zero_rate(t)
        # Continuous Compounding: DF = e^(-r*t)
        return np.exp(-r * t)


class BootstrapEngine:
    def __init__(self):
        self.curve = YieldCurve()

    def build_curve(self, instruments: List[Instrument]):
        # Sort by maturity (Critical for bootstrapping)
        sorted_instruments = sorted(instruments, key=lambda x: x.maturity)

        print(f"{'Instrument':<15} | {'Maturity':<5} | {'Market Rate':<10} | {'Solved Zero Rate':<10}")
        print("-" * 60)

        for inst in sorted_instruments:
            if isinstance(inst, Deposit):
                self._solve_deposit(inst)
            elif isinstance(inst, InterestRateSwap):
                self._solve_swap(inst)

        return self.curve

    def _solve_deposit(self, inst: Deposit):
        # Analytic solution for Deposits
        # DF = 1 / (1 + r*t)
        # DF = e^(-z*t)  =>  -z*t = ln(DF)  => z = -ln(DF)/t
        df = 1.0 / (1.0 + inst.rate * inst.maturity)
        zero_rate = -np.log(df) / inst.maturity
        
        self.curve.add_point(inst.maturity, zero_rate)
        print(f"{inst.name:<15} | {inst.maturity:<5.2f} | {inst.rate:<10.2%} | {zero_rate:<10.4%}")

    def _solve_swap(self, inst: InterestRateSwap):
        # Numerical solution for Swaps
        # We need to find a Zero Rate 'z' at maturity T such that Swap PV = 1.0
        
        def objective_function(guess_rate):
            # 1. Temporarily assume the Zero Rate at Maturity is 'guess_rate'
            # We assume linear interpolation from the LAST known point to this new point
            self.curve.times.append(inst.maturity)
            self.curve.zero_rates.append(guess_rate)
            
            # 2. Price the swap
            pv = 0.0
            for cf in inst.get_cash_flows():
                df = self.curve.get_discount_factor(cf.time)
                pv += cf.amount * df
            
            # 3. Remove temp point (clean up for next iteration)
            self.curve.times.pop()
            self.curve.zero_rates.pop()
            
            # 4. Return Error (Target PV is 1.0 for Par Swap)
            return pv - 1.0

        # Solve for the rate that makes Error = 0
        # Start guess can be the previous known zero rate
        initial_guess = self.curve.zero_rates[-1]
        solved_rate = newton(objective_function, x0=initial_guess)
        
        self.curve.add_point(inst.maturity, solved_rate)
        print(f"{inst.name:<15} | {inst.maturity:<5.2f} | {inst.rate:<10.2%} | {solved_rate:<10.4%}")