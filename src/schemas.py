from pydantic import BaseModel, Field
from typing import Union
from enum import Enum

class TradeMethod(str, Enum): 
  short = "Short Trade"
  long = "Long Trade"


class OrderInput(BaseModel):
    method: TradeMethod = TradeMethod.short
    start_price: float
    amount: float
    percent_change: float