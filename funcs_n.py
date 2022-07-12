## HELP CREATE OPEN SOURCE ALGORITHMIC CODE AND REDUCE INFORMATION ASYMMETRY IN STOCK MARKETS/CRYPTO
## WE WILL IMPORT THIS MODULE/FILE FOR OTHER FILES TO USE, import funcs_n as n
## NEW BASE FILE FROM SCRATCH
## SELF NOTE: NONE OF PREVIOUS FILE ON 'RANDOM FORESTS - FEATURE SELECTION.py' IS USED IN THIS FILE
## FILE EXISTS AS A BASE TEMPLATE
## ANY COMPLEXITIES WILL BE ADDED IN SUBSEQUENT FILES
## THEREFORE, ANYONE CAN MANIPULATE THIS BASE/FOUNDATION FOR MORE ADVANCED TRADING QUANTITATIVE/ALGORITHMIC STRATEGIES
## SMA_15M ARE NOT THE SIGNALS USED, SUBSEQUENT MODULES WILL HAVE MORE SIGNALS AS IT IS BUILT OUT
## ONLY CODE, NOT INVESTMENT ADVICE
## NEED TO FILE APPROPRIATELY MEETING REQS TO DO BUSINESS AS A RETAIL/DISCRETIONARY/ALGO TRADER
## WITH WASH SALES AND CURRENT LIMITING REGULATIONS, TYPICALLY AT-HOME RETAIL/DISCRETIONARY/ALGO TRADERS AREN'T CLASSIFIED AS BUSINESS, THEREFORE HAVE WASH SALES, AND TAXED AT ORDINARY INCOME GAINS
## SO IT IS VERY COSTLY TO DO RETAIL BUSINESS
## ALGO TRADING REQUIRES MICROFRACTIONAL TIME UNITS, ANOTHER LIMITING FACTOR
## PAIRS TRADES, L/S QUANTITATIVE STRATS CAN BE A STRONG STARTING POINT FOR NEW RETAIL INVESTORS
## STUDY CAREFULLY, TEST/CODE THRICE BEFORE LIVE TRADING ONCE
## BASIC SMA'S WON'T CUT IT, WE WILL NEED TO ADD TO MAKE QUANTITATIVE L/S, ARBITRAGE CRYPTO STRATEGIES
## GOOD START AS WE CAN USE CONTENT COUPLING FOR NEW INHERITED MODULES (MAKING INDEPENDENT MODULE WHERE WE IMPORT THIS MODULE TO SUBSEQUENT MODULES, HIGH COHESION/LOW COUPLING)
## SHORT-TERM TREND FOLLOWING, GOOD IN VOLATILE, STRONG DIRECTIONAL BIAS DAYS
## EXCLAIMER: DATASETS ARE TYPICALLY SHORT-TERM (i.e. 2-3 DAYS), NOT ANY LONG TERM ADVICE
## EXCLAIMER: NOT INVESTMENT ADVICE

import ccxt
import pandas as pd
import numpy as np
from datetime import date, datetime  # timezome, tzinfo
import time, schedule
import json as js

## IMPORTANT: CREATE APIKEY ON PHEMEX 
## USE ONE-TIME SECRET AND APIKEY PLUG-IN TO 'APIKEY' AND 'SECRET' FIELDS BELOW

phemex = ccxt.phemex({
    'enableRateLimit': True,
    'apiKey': 'APIKEY',
    'secret': 'SECRET'
})

## CUSTOMIZE ALL INPUTS HERE!
# Define Symbol Used
symbol = 'uBTCUSD'
index_pos = 0  ## CHANGE BASED ON WHICH ASSET --> SEE RANDO.JSON FILE, FORMAT TO JSON:  SHIFT+ALT+F

# the time between trades
pause_time = 60

# for volume calculations: Vol_repeat * Vol_time == TIME of VOLUME collection
vol_repeat = 11
vol_time = 5

# Position Size Takes Bid Executes Limit Order, Can Customize
pos_size = 1  ## Contract Size
params = {'timeInForce': 'PostOnly',}
# phemex.create_limit_buy_order(symbol=symbol, pos_size=pos_size, price=bid_ask()[0], params=params)
target = 150  ## % percentage points
max_loss = -65  ## % percentage points
vol_decimal = .4

# for df
timeframe = '30m'
limit = 500
sma = 20

# START HERE
# fetch ohlcv - open high low close volume
print('STARTING... ')
print('FETCHING OHLCV DATA... ')
bars = phemex.fetch_ohlcv('uBTCUSD', timeframe='15m', limit=500)
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
print(df.tail(20))

#GETS BEST BID ASK
def bid_ask(symbol=symbol):

    ob = phemex.fetch_order_book(symbol)   #BTC/USD #BTC/USDT
    #print(ob)

    bid = ob['bids'][0][0]
    ask = ob['asks'][0][0]
    print(f'${symbol}$ ASK PRICE: ${ask}') #if ask > sma20_d then BUY, else ask < sma20_d then SELL

    return bid, ask # bid_ask()[0] = bid, [1] = ask
    
bid_ask()    # Can use i.e.  bid_ask('DOGEUSD') to retrieve bid ask of any symbol


# returns: df_sma with sma (Can Customize df below)
# call: df_sma(symbol, timeframe, limit, sma) # not required to pass, if not passed, uses default
def df_sma(symbol=symbol, timeframe=timeframe, limit=limit, sma=sma):

    print('Starting Indices...'.upper())

    bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    # print(bars)
    df_sma = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    # 20 Day SMA - SMA20
    df_sma[f'sma{sma}d_{timeframe}'] = df_sma.close.rolling(sma).mean()

    # if bid < 20 Day SMA then sma = Bearish, if bid > 20 Day SMA then sma = Bullish
    bid = bid_ask(symbol)[1]    # Customize: pass diff. symbol or timeframe on daily_sma()

    df_sma.loc[df_sma[f'sma{sma}d_{timeframe}'] > bid, 'Signal'] = 'SELL! SELL! SELL!'
    df_sma.loc[df_sma[f'sma{sma}d_{timeframe}'] < bid, 'Signal'] = 'BUY! BUY! BUY!'

    print(df_sma.tail(25))
    
    return df_sma
    
df_sma()    # i.e. daily_sma('APEUSD', '15m', 10)    Symbol Timeframe Limit

# returns: open_positions() open_positions, openpos_bool, openpos_size, long, index_pos
# TO-DO Figure out a way to sort through rando.json and assign an index_pos
    # make a function that loops through dictionary and does that
def open_positions(symbol=symbol):

    #what is the position index for that symbol?

    if symbol == 'uBTCUSD':
        index_pos = 0
    elif symbol == 'ETHUSD':
        index_pos = 1
    elif symbol == 'DOGEUSD':
        index_pos = 2
    else:
        index_pos = None
    params = {'type': 'swap', 'code': 'USD'}
    balance = phemex.fetch_balance(params=params)
    open_positions = balance['info']['data']['positions']
    # print(open_positions)

    openpos_side = open_positions[index_pos]['side']
    openpos_size = open_positions[index_pos]['size']
    # print(open_positions)

    if openpos_side == ('BUY'):
        openpos_bool = True
        long = True
    elif openpos_side == ('SELL'):
        openpos_bool = True
        long = False
    else:
        openpos_bool = False
        long = None

    print(f'Open Positions... | openpos_bool (T|F): {openpos_bool} | openpos_size: {openpos_size} | long: {long}'.upper())
    
    return open_positions, openpos_bool, openpos_size, long, index_pos

open_positions()

## Cancel All Orders, Safety Switch
# NOTE: I marked out 2 orders below and the cancel, need to unmark before live
# returns: kill_switch() nothing
# kill_switch: pass in (symbol) if no symbol uses default
def kill_switch(symbol=symbol):

    print(f'STARTING KILL SWITCH FOR ${symbol}$')
    # Remember! Open Positions Returns: open_positions() open_positions, openpos_bool, openpos_size, long    <---    see index_pos
    openposi = open_positions(symbol)[1]  # true or false; Is there Open Position
    long = open_positions(symbol)[3]  # true or false; Long Position?
    kill_size = open_positions(symbol)[2] # size thats open

    print(f'Open Positions: {openposi}, long: {long}, size: {kill_size}'.upper())

    while openposi == True:

        print('Starting Kill Switch Loop til Limit Fills'.upper())
        temp_df = pd.DataFrame()
        print('Created: temporary DataFrame'.upper())

        #phemex.cancel_all_orders(symbol)
        openposi = open_positions(symbol)[1]
        long = open_positions(symbol)[3]  # true or false
        kill_size = open_positions(symbol)[2]
        kill_size = int(kill_size)

        bid = bid_ask(symbol)[1]
        ask = bid_ask(symbol)[0]

        if long == False:
            #phemex.create_limit_buy_order(symbol, kill_size, bid, params)
            print(f'Kill Switch: BUY TO CLOSE order of:  {kill_size}  ${symbol}$  at ${bid}'.upper())
            print('Sleeping for 30 seconds to see if it fills...')
            time.sleep(30)
        elif long == True:
            #phemex.create_limit_sell_order(symbol, kill_size, ask, params)
            print(f'Kill Switch: SELL TO CLOSE order of:  {kill_size}  ${symbol}$  at ${ask}'.upper())
            print('Sleeping for 30 seconds to see if it fills...')
            time.sleep(30)
        else:
            print('++++++ SOMETHING I DIDNT EXCEPT IN KILL SWITCH FUNCTION')

        openposi = open_positions(f'${symbol}$')[1]

kill_switch()

# returns nothing
# sleep_on_close(symbol=symbol, pause_time=pause_time)  # pause in minutes
def sleep_on_close(symbol=symbol, pause_time=pause_time):

    '''
    this func pulls closed orders, then if last close was in last 59 minutes
    then it sleeps for 1 minute
    sincelasttrade = minutes since last trade
    '''

    closed_orders = phemex.fetch_closed_orders(symbol)
    # print(closed_orders)

    for ord in closed_orders[-1::-1]:

        sincelasttrade = pause_time - 1 # how long we pause

        filled = False

        status = ord['info']['ordStatus']
        txttime = ord['info']['transactTimeNs']
        txttime = int(txttime)
        txttime = round((txttime/1000000000)) # in nanoseconds
        print(f'STATUS ORDER OF ${symbol}$: {status} | EPOCH TIME: {txttime}')
        print('Next Iteration...'.upper())
        print('------')

        if status == 'Filled':
            print('FOUND ORDER WITH LAST FILL...')
            print(f'TIME: {txttime} | ORDER STATUS: {status}')
            orderbook = phemex.fetch_order_book(symbol)
            ex_timestamp = orderbook['timestamp'] # in ms
            ex_timestamp = int(ex_timestamp/1000)
            print(' ----- BELOW IS TRANSACTION TIME, THEN EXCHANGE EPOCH TIME ----- ')
            print(txttime)
            print(ex_timestamp)

            time_spread = (ex_timestamp - txttime)/60

            if time_spread < sincelasttrade:
                # print ('time since last trade is less than time spread')
                # # if in pos is true, put close order here
                # if in_pos == True:

                sleepy = round(sincelasttrade - time_spread) * 60
                sleepy_min = sleepy/60

                print(f'Time spread: less than {sincelasttrade} minutes | time elapsed: {time_spread} So we sleep'.upper())
                time.sleep(60)

            else:
                print(f'Its been {time_spread} minutes since last fill so not sleeping since last trade is {sincelasttrade} minutes'.upper())
            break
        else:
            continue
    
    print(f'sleep on close function for ${symbol}$ complete!'.upper())

sleep_on_close(symbol, 600)

def ob(symbol=symbol, vol_repeat=vol_repeat, vol_time=vol_time):

    print('FETCHING ORDER BOOK DATA...')

    df = pd.DataFrame()
    temp_df = pd.DataFrame()

    ob = phemex.fetch_order_book(symbol)
    # print(ob)
    bids = ob['bids']
    asks = ob['asks']

    first_bid = bids[0]
    first_ask = asks[0]

    bid_vol_list = []

    # for set in bids:
    #     print(set)
    #     price = set[0]
    #     vol = set[1]
    #     bid_vol_list.append(vol)
    #     print(price)
    #     print(vol)
    
    ask_vol_list = []

    # for set in asks:
    #     print(set)
    #     price = set[0]
    #     vol = set[1]
    #     ask_vol_list.append(vol)
    #     print(price)
    #     print(vol)

    # print(bid_vol_list)
    # sum_bidvol = sum(bid_vol_list)
    # print(sum_bidvol)
    # temp_df['bid_vol'] = [sum_bidvol]


    # if SELL vol > BUY vol AND profit target hit, exit

    # get last 1 minute of volume... and if SELL > BUY vol do x
    # TO-DO: make range a var
    # repeat == the amount of times program iterates through, and multiplies
    # by repeat_time to calculate the time
    for x in range(vol_repeat):

        for set in bids:
            # print(set)
            price = set[0]
            vol = set[1]
            bid_vol_list.append(vol)
            # print(price)
            # print(vol)

            # print(bid_vol_list)
            sum_bidvol = sum(bid_vol_list)
            # print(sum_bidvol)
            temp_df['bid_vol'] = [sum_bidvol]

        for set in asks:
            # print(set)
            price = set[0]
            vol = set[1]
            ask_vol_list.append(vol)
            # print(price)
            # print(vol)

            sum_askvol = sum(ask_vol_list)
            # print(sum_askvol)
            temp_df['ask_vol'] = [sum_askvol]
        
        # print(temp_df)
# TO-DO: change sleep to var
        time.sleep(vol_time)
        df = pd.concat([df, temp_df])
        print(df)  # Very Slow
        print(' ')
        print('------')
        print(' ')
    print('Done Collecting Volume Data for BIDS & ASKS'.upper())
    print('Calculating Sums...'.upper())
    total_bidvol = df['bid_vol'].sum()
    total_askvol = df['ask_vol'].sum()
    seconds = vol_time * vol_repeat
    mins = round(seconds / 60, 2)
    print(f'Last {mins} minutes for symbol ${symbol}$ | Total Bid Volume: {total_bidvol} | Total Ask Volume: {total_askvol}'.upper())

    if total_bidvol > total_askvol:

        control_dec = (total_askvol/total_bidvol)
        print(f'CRYPTO BULLS ARE DOMINATING VOLUME in ${symbol}$ | ASK/BID RATIO: {control_dec}')
        # if bulls are in control, use regular target
        bullish = True

    else:
        control_dec = (total_askvol/total_bidvol)
        print(f'CRYPTO BEARS ARE DOMINATING VOLUME in ${symbol}$ | ASK/BID RATIO: {control_dec}')
        bullish = False

# open_positions() open_positions, openpos_bool, openpos_size, long

    open_posi = open_positions(symbol)
    openpos_tf = open_posi[1]
    long = open_posi[3]
    print(f'OPEN POSITION: {openpos_tf} || LONG: {long}')

    # if target is hit, check book vol
    # if book vol is:  <.4  ... stay in position... sleep?
    # need to check if long or short

    if openpos_tf == True:
        if long == True:
            print('WE ARE IN A LONG POSITION')
            if control_dec < vol_decimal:  # # vol decimal set at .4 at top (inputs)
                vol_under_dec = True
                # print('going to sleep for a minute... under vol decimal of .4')
                # time.sleep(6)  #change to 60
            else:
                print('VOLUME NOT UNDER DECIMAL... SETTING VOL_UNDER_DEC AS FALSE')
                control_dec > vol_decimal
                vol_under_dec = False
        else:
            print('WE ARE IN A SHORT POSITION')
            if control_dec < vol_decimal:  # # vol dec set to .4 at top
                vol_under_dec = True
                # print('going to sleep for a minute... under vol decimal of .4')
                # time.sleep(6)  # change to 60
            else:
                print('VOLUME NOT UNDER DECIMAL... SETTING VOL_UNDER_DEC AS FALSE')
                control_dec > vol_decimal
                vol_under_dec = False
    else:
        print('WE ARE NOT IN A POSITION... ')
        vol_under_dec = None
    
    # when vol_under_dec == FALSE AND target hit, then exit
    print(vol_under_dec)

    return vol_under_dec

    # for volume calculations: Vol_repeat * Vol_time == TIME of VOLUME collection

ob('uBTCUSD', 3, 3)  ## symbol, times it loops, seconds

# pnl_close() [0] pnlclose and [1] in_pos [2] size [3] long TF
def pnl_close(symbol=symbol, target=target, max_loss=max_loss):

    print(f'CHECKING TO SEE IF IT IS TIME TO EXIT SECURITY ${symbol}$')

    params = {'type':"swap", 'code':'USD'}
    pos_dict = phemex.fetch_positions(params=params)
    # print(pos_dict)

    index_pos = open_positions(symbol)[4]
    pos_dict = pos_dict[index_pos]  ## JSON position: BTC = [0] ETH = [1] DOGEUSD [2]
    side = pos_dict['side']
    size = pos_dict['contracts']
    entry_price = float(pos_dict['entryPrice'])
    leverage = float(pos_dict['leverage'])

    current_price = bid_ask(symbol)[0]

    print(f'SIDE: {side} | ENTRY_PRICE: {entry_price} | LEVERAGE: {leverage}')
    # SHORT OR LONG
    
    if side == 'long':
        diff = current_price - entry_price
        long = True
    else:
        diff = entry_price - current_price
        long = False

    try:
        perc = round(((diff/entry_price) * leverage), 10)
    except:
        perc = 0
    
    perc = 100 * perc
    print(f'PNL PERCENTAGE FOR ${symbol}$: {(perc)}%')

    pnlclose = False
    in_pos = False

    if perc > 0:
        in_pos = True
        print(f'FOR ${symbol}$ WE ARE IN A WINNING POSITION')
        if perc > target:
            print(':):) OUR POSITION IS PROFITABLE & HIT PROFIT TARGET %... ')
            pnlclose = True
            vol_under_dec = ob(symbol) # return TF
            if vol_under_dec == True:
                print(f'VOLUME IS UNDER THE DECIMAL THRESHOLD OF {vol_decimal}')
                time.sleep(30)
            else:
                print(f'STARTING KILL SWITCH... WE HAVE HIT OUR PROFIT TARGET %')
        else:
            print(f'WE HAVE NOT HIT OUR PROFIT TARGET %, AS OF PRINT')
            
    elif perc < 0: # -10, 20,

        in_pos = True

        if perc <= max_loss:  ## UNDER -55, -56
            print(f'EXIT POSITION! POSITION ${symbol}$ DOWN {perc}% | STARTING KILL SWITCH...')
            kill_switch()
        else:
            print(f'FOR ${symbol}$, WE ARE IN A LOSING POSITION OF {perc}%, BUT STAYING IN POSITION SINCE OUR MAX LOSS IS {max_loss}%')
    else:
        print('WE ARE NOT IN A POSITION...')

    if in_pos == True:

        # IF BREAKS OVER .8% OVER 15M SMA, THEN CLOSE POSITION (STOP LOSS)

        # PULL IN 15m SMA
        # CALL: df_sma(symbol, timeframe, limit, sma)
        # PLUG IN TIMEFRAME, SMA if desired
        timeframe = '15m'
        df_f = df_sma(symbol, timeframe, 100, sma)
        # print(df_f)
        # df_f['sma20_15'] # last value of this SMA
        last_sma15 = df_f.iloc[-1][f'sma{sma}d_{timeframe}']
        last_sma15 = int(last_sma15)
        print(f'SMA15: ${last_sma15}')
        # pull current bid
        curr_bid = bid_ask(symbol)[1]
        curr_bid = int(curr_bid)
        print(F'CURRENT BID: ${curr_bid}')

        sl_val = last_sma15 * 1.008
        print(f'SMA15 * 1.008: ${sl_val}')

        ## TURN KILL SWITCH ON

        # 5/11 REMOVED BELOW AND IMPLEMENTING 55% STOP LOSS
        # if curr_bid > sl_val:
        #   print('CURRENT BID IS ABOVE STOP LOSS VALUE... STARTING KILL SWITCH)
        #   kill_switch()
        # else:
        #   print('STAYING IN POSITION... ')

    else:
        print('WE ARE NOT IN A POSITION... ')

    

    print(f'...FINISHED CHECKING PNL % CLOSE FOR SYMBOL ${symbol}$')

    return pnlclose, in_pos,size, long, index_pos


# returns: open_positions() open_positions, openpos_bool, openpos_size, long, index_pos
pnl_close('uBTCUSD')

###END OF TEMPLATE###
