import numpy as np
from typing import List
from scipy.optimize import newton, minimize
from scipy.interpolate import interp1d, CubicSpline
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
        # Sort by maturity
        sorted_instruments = sorted(instruments, key=lambda x: x.maturity)
        
        # THE FIX: Anchor the curve at t=0 using the shortest-term rate
        # This prevents the spline from trying to jump from 0% to 5.5% in one day
        self.curve.times = [0.0]
        self.curve.zero_rates = [sorted_instruments[0].rate]

        for inst in sorted_instruments:
            if isinstance(inst, Deposit):
                df = 1.0 / (1.0 + inst.rate * inst.maturity)
                z = -np.log(df) / inst.maturity
                self.curve.times.append(inst.maturity)
                self.curve.zero_rates.append(z)
            elif isinstance(inst, InterestRateSwap):
                def objective(guess_rate):
                    self.curve.times.append(inst.maturity)
                    self.curve.zero_rates.append(guess_rate)
                    pv = sum(cf.amount * self.curve.get_discount_factor(cf.time) for cf in inst.get_cash_flows())
                    self.curve.times.pop()
                    self.curve.zero_rates.pop()
                    return pv - 1.0
                
                z = newton(objective, x0=self.curve.zero_rates[-1])
                self.curve.times.append(inst.maturity)
                self.curve.zero_rates.append(z)
                
        # Return a continuous Cubic Spline function
        return CubicSpline(self.curve.times, self.curve.zero_rates, bc_type='natural')
class NSSEngine:
    """
    Parametric Yield Curve Engine using Nelson-Siegel-Svensson.
    Finds the 6 parameters that best fit the market data to a smooth formula.
    """
    def __init__(self):
        # Initial Guess: [beta0, beta1, beta2, beta3, tau1, tau2]
        self.curve = YieldCurve()
        self.params = np.array([0.03, -0.02, 0.02, 0.01, 1.5, 5.0])

    def nss_formula(self, t, params):
        b0, b1, b2, b3, t1, t2 = params
        t = np.maximum(t, 1e-6) # Prevent divide by zero error at t=0
        
        term1 = b1 * (1 - np.exp(-t/t1)) / (t/t1)
        term2 = b2 * ((1 - np.exp(-t/t1)) / (t/t1) - np.exp(-t/t1))
        term3 = b3 * ((1 - np.exp(-t/t2)) / (t/t2) - np.exp(-t/t2))
        
        return b0 + term1 + term2 + term3

    def build_curve(self, instruments):
        # Objective Function: Minimize Sum of Squared Errors (SSE)
        def error_function(guess_params):
            sse = 0.0
            for inst in instruments:
                model_rate = self.nss_formula(inst.maturity, guess_params)
                sse += (model_rate - inst.rate) ** 2
            return sse
        
        bnds = (
            (-1.0, 1.0),   # beta0
            (-1.0, 1.0),   # beta1
            (-1.0, 1.0),   # beta2
            (-1.0, 1.0),   # beta3
            (0.01, 30.0),  # tau1 (Time parameter, strictly positive)
            (0.01, 30.0)   # tau2 (Time parameter, strictly positive)
        )

        # The 'Nelder-Mead' algorithm handles non-linear curve fitting very well
        result = minimize(error_function, self.params, method='SLSQP', bounds = bnds)
        self.params = result.x
        
        # Return a callable lambda function representing the smooth curve
        return lambda t: self.nss_formula(t, self.params)