## ALGORITHMIC TRADING - ALGORITHMICALLY SUBMIT LIMIT ORDERS FOR REDUCED EXCHANGE FEES - ALLOWS USER CONTROL FOR DISCRETIONARY AND SIZE-BY-SIZE TRADING IN VOLATILITY EVENTS

import funcs_n as n
import ccxt
import pandas as pd
import numpy as np
import time, schedule
from datetime import datetime
from pprint import pprint

phemex = ccxt.phemex({
    'enableRateLimit': True,
    'apiKey': 'APIKEY',
    'secret': 'SECRET'
})

## CUSTOMIZE ALL INPUTS HERE!
# Define Symbol Used
symbol = 'uBTCUSD'
spread = .001  ## CHANGE TO .002 (.2%) OR WHICHEVER REDUCED/WORSE SPREAD GETS FILLS
index_pos = 0  ## CHANGE BASED ON WHICH ASSET --> SEE RANDO.JSON FILE, FORMAT TO JSON:  SHIFT+ALT+F

# the time between trades
pause_time = 60

# for volume calculations: Vol_repeat * Vol_time == TIME of VOLUME collection
vol_repeat = 11
vol_time = 5

# Position Size Takes Bid Executes Limit Order, Can Customize
pos_size = 100  ## Contract Size
params = {'timeInForce': 'PostOnly',}
# phemex.create_limit_buy_order(symbol=symbol, pos_size=pos_size, price=bid_ask()[0], params=params)
target = 150  ## % percentage points
max_loss = -65  ## % percentage points
vol_decimal = .4

def index_pos():

    if symbol == 'uBTCUSD':
        index_pos = 0
    elif symbol == 'ETHUSD':
        index_pos = 1
    elif symbol == 'DOGEUSD':
        index_pos = 2
    else:
        index_pos = None
    
    return index_pos

def get_pos():

    index = index_pos()

    params = {'type': 'swap', 'code': 'USD'}
    balance = phemex.fetch_balance(params=params)
    open_positions = balance['info']['data']['positions']
    # print(open_positions)

    openpos_side = open_positions[index]['side']
    openpos_size = open_positions[index]['size']
    openpos_size = int(openpos_size)
    # print(open_positions)

    openpos_lev = open_positions[index]['leverage']

    if openpos_size >= pos_size:
        openpos_bool = True
    else:
        openpos_bool = False

    if openpos_side == ('BUY'):
        openpos_size = (openpos_size)
    elif openpos_side == ('SELL'):
        openpos_size = (openpos_size)
    else:
        print('??? POSITION IS NEITHER POSITIVE NOR NEGATIVE')
    
    print(f'openpos_side: {openpos_side} | openpos_size: {openpos_size} | openpos_bool (T|F): {openpos_bool}'.upper())
    
    return openpos_size, openpos_size, openpos_bool, open_positions  # get_pos()

def balance():

    # FOR CONTRACT TRADING
    params={"type":"swap","code":"USD"}
    balance = phemex.fetch_balance(params=params)
    total = balance['total']['USD']
    used = balance['used']['USD']
    # print(f'BALANCE: ${round(balance)}')
    # print(f'TOTAL: ${round(total)}')
    # print(f'USED: ${round(used)}')
    print('')

    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S %p")

# update balance function, does not calculate

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('')
    print('')
    print(dt_string)
    print(f'BALANCE: ${round(total)} | CURRENTLY ${round(total)} IN TRADE')
    print('')
    print('')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('')

    return balance, used, total, now    ## balance()  balance = [0], [1] used, [2] total, [3] now

balance()

# n.kill_switch(symbol)
# n.open_positions(symbol)
# n.bid_ask(symbol)


def open_order():

    print('STARTING OPEN ORDER... ')

    side = input('BUY OR SELL? (B/S):')
    print(side)
    
    bidask = n.bid_ask(symbol)
    bid = bidask[1]
    ask = bidask[0]

    size = pos_size

    if side == 'B':
        buy_price = bid * (1-spread)
        print('CANCELLING OLD ORDERS... || SUBMITTING NEW ORDERS...')
        # phemex.cancel_all_orders(symbol)
        # phemex.create_limit_buy_order(symbol, size, buy_price, params)
        print(f'{side} ORDER 1 {size} PRICE: {buy_price}')
    else:
        sell_price = ask * (1+spread)
        print('CANCELLING OLD ORDERS... || SUBMITTING NEW ORDERS...')
        # phemex.cancel_all_orders(symbol)
        # phemex.create_limit_sell_order(symbol, size, sell_price, params)
        print(f'{side} ORDER 1 LOT {size} CONTRACTS | PRICE: ${sell_price}')

    print('FINISHED SUBMITTING ORDERS... SLEEPING FOR 120 SECONDS') ## 120 SECONDS WHEN LIVE TRADING
    time.sleep(1)  ## 5 WHEN RUNNING/TESTING CODE, 120 WHEN LIVE TRADING

    open_pos = get_pos()[0]  ## erring code, TypeError: '>=' not supported between instances of 'str' and 'int'  ##FIXED: CHANGED openpos_side to openpos_size 
    open_pos = abs(open_pos)

    while open_pos < size:
        print(f'STARTING LOOP... CHECKING IF POSITION IS FILLED')
        print(f'SLEEPING 15 SECONDS UNTIL ORDER FILL... FILLED: {open_pos}/{pos_size}')
        time.sleep(1)  ## TIME.SLEEP(15) 15 SECONDS

        ## IF WE HIT PROFIT TARGET OF ie 10% (CLOSE), IF WE HIT STOP LOSS OF ie 9% (CLOSE)
        n.pnl_close(symbol, target, max_loss)
        open_pos = get_pos()[0]
        open_pos = abs(open_pos)
    
    open_pos = get_pos()[0]
    open_pos = abs(open_pos)

    while open_pos > 0:
        print(f'STARTING LOOP SINCE WE HAVE OPEN POSITION: {open_pos}...')
        n.pnl_close(symbol, target, max_loss)
        print('JUST CHECKED PNL... SLEEPING 15 SECONDS MORE')
        time.sleep(1)  ## TIME.SLEEP(15) 15 SECONDS

        open_pos = get_pos()[0]
        open_pos = abs(open_pos)

    print(f'DONE!! MADE OPENING ORDER || FILLED || CLOSED WITH PNL_CLOSE || CHECKING RESULTS...')
    

open_order()

## CONTROL + C TO STOP TERMINAL!! (READS: ^C)
