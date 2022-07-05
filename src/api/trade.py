from __future__ import annotations
import asyncio
import base64
from typing import Callable
from app.__internal import Function
from fastapi import FastAPI, APIRouter

import ccxt
from src.model.long_trade import LongTrade
from src.model.short_trade import ShortTrade

from src.core.exchange import CryptoExchange
# from src.core.telegrambot import TelegramBot
from src.core.trade_excuter import TradeExecutor
from src.utils.formatter import format_balance, format_open_orders, format_order

from src.schemas import OrderInput, TradeMethod

from config import cfg


class TradeAPI(Function):
  
    def __init__(self, error: Callable):
        self.log.info("Trading bot inited")
        
        self.ccxt_ex = ccxt.bitfinex()
        self.ccxt_ex.apiKey = base64.b64encode(bytes(cfg.API_KEY, "utf-8"))
        self.ccxt_ex.secret = cfg.SECRET

        self.exchange = CryptoExchange(self.ccxt_ex)
        self.trade_executor = TradeExecutor(self.exchange)
        
    def _execute_trade(self, trade):
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.trade_executor.execute_trade(trade))
        loop.run_until_complete(task)
        
    def Bootstrap(self, app: FastAPI):
        router = APIRouter(prefix='/api/trade')
        
        @router.get('/symbol', summary="Get all symbols")
        async def get_all_symbols():
          # print(self.exchange.markets)
          return self.exchange.markets
        
        @router.get('/order', summary="Get all order")
        async def get_all_order():
            orders = self.exchange.fetch_open_orders()
            print(orders)
            return format_open_orders(orders=orders)
        
        @router.get('/balance', summary="Get free balance")
        async def get_free_balance():
            balance = self.exchange.free_balance
            return format_balance(balance=balance)
          
        @router.post('/order', summary="Make order")
        async def make_order(data: OrderInput):
            if (data.method == TradeMethod.long):
                trade = LongTrade(start_price=data.start_price, symbol='BTC/USD', amount=data.amount, percent_change=data.percent_change)
            elif (data.method == TradeMethod.short):
                trade = ShortTrade(start_price=data.start_price, symbol='BTC/USD', amount=data.amount, percent_change=data.percent_change)
              
            self._execute_trade(trade)
          
        app.include_router(router)
        