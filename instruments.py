from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
import numpy as np

# --- PART 2: INSTRUMENT CLASSES ---

@dataclass
class CashFlow:
    time: float
    amount: float

class Instrument(ABC):
    def __init__(self, name: str, maturity: float, rate: float):
        self.name = name
        self.maturity = maturity
        self.rate = rate 

    @abstractmethod
    def get_cash_flows(self) -> List[CashFlow]:
        pass

class Deposit(Instrument):
    """ Cash Deposit: Simple Interest (1 + r*t) at maturity """
    def get_cash_flows(self) -> List[CashFlow]:
        # Cash/Libor typically pays Principal + Interest at end
        return [CashFlow(self.maturity, 1.0 + (self.rate * self.maturity))]

class InterestRateSwap(Instrument):
    """ Vanilla Swap: Annual Coupons + Principal at Maturity """
    def get_cash_flows(self) -> List[CashFlow]:
        flows = []
        # Assume Annual payments for simplicity
        dt = 1.0 
        times = np.arange(dt, self.maturity + 0.001, dt)
        
        # Coupons
        for t in times:
            flows.append(CashFlow(t, self.rate * dt))
            
        # Repay Principal (for bootstrapping pricing)
        flows[-1].amount += 1.0
        return flows