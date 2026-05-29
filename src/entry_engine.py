import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import csv

#df = pd.read_csv("data/sample_market_data.csv")

def entry_logic(config):
    # Get data
    df = get_market_data(config["symbol"], config["period"], config["timeframe"])
    
    # -------------------------
    # Previous 20-bar high
    # -------------------------
    df['breakout_level'] = (df['high'].rolling(config["breakout_logic"]["lookback_bars"]).max().shift(1))

    # -------------------------
    # Retest zone
    # -------------------------
    df['retest_zone_low']  = ( df['breakout_level'] - (config["retest_logic"]["atr_multiplier"] * df['atr_14']) )
    df['retest_zone_high'] = ( df['breakout_level'] + (config["retest_logic"]["atr_multiplier"] * df['atr_14']) )
    df['retest_midpoint']  = ( df['retest_zone_low'] + df['retest_zone_high'] ) / 2

    # -------------------------
    # Breakout condition
    # -------------------------
    df['prior_breakout'] = (df['close'] > df['breakout_level'])

    # -------------------------
    # Retest condition
    # Price enters retest zone
    # -------------------------
    df['retest_condition'] = ((df['low'] <= df['retest_zone_high']) & (df['high'] >= df['retest_zone_low']) )

    # -------------------------
    # Close position
    # -------------------------
    df['close_position'] = ( (df['close'] - df['low']) / (df['high'] - df['low']) )

    # Avoid divide by zero
    df['close_position'] = df['close_position'].fillna(0)

    # -------------------------
    # setup score
    # -------------------------
    df['setup_score'] = config["setup_score"]

    # -------------------------
    # Final Entry Signal
    # -------------------------
    df['entry_signal'] = (
        df['prior_breakout'] &
        df['retest_condition'] &
        (df['close'] > df['retest_midpoint']) &
        (df['close'] > df['vwap']) &
        (df['close_position'] >= 0.60) &
        (df['setup_score'] >= 6.5)
    )

    ## StopLoss Logic
    # -------------------------
    # Entry price
    # -------------------------
    df['entry_price'] = df['close']

    # ATR multiplier
    atr_multiplier = 1.2

    # -------------------------
    # ATR stop
    # -------------------------
    df['atr_stop'] = ( df['entry_price'] - (df['atr_14'] * atr_multiplier) )

    # -------------------------
    # Structure stop
    # -------------------------
    df['structure_stop'] = df['retest_zone_low']

    # -------------------------
    # Final stop loss
    # Use tighter/safer stop
    # -------------------------
    df['stop_loss'] = df[['atr_stop', 'structure_stop']].min(axis=1)

    # -------------------------
    # Risk per unit
    # -------------------------
    df['R'] = (df['entry_price'] - df['stop_loss'])

    # Reject invalid trades
    df['valid_risk'] = (df['R'] > 0)

    # -------------------------
    # Final tradable signal
    # -------------------------
    df['final_signal'] = ( df['entry_signal'] & df['valid_risk'] )

    ## Calculate target
    # -------------------------
    # Target 1
    # -------------------------
    df['T1'] = ( df['entry_price'] + (1.5 * df['R']) )
    
    # -------------------------
    # Target 2
    # -------------------------
    df['T2'] = ( df['entry_price'] + (2.5 * df['R']) )
   
    
    enrty_intent_logs = pd.DataFrame({"Timestamp" : df["timestamp"], 
                                        "Entry type" :config['entry_type'],
                                        "Breakout level" : df['breakout_level'],
                                        "Retest zone" :df['retest_condition'], 
                                        "Entry price" :df['entry_price'],
                                        "Stop loss" :df['stop_loss'], 
                                        "Target 1" : df['T1'], 
                                        "Target 2" : df['T2'],
                                        "Reason codes": df['final_signal']}) 
    
    enrty_intent_logs.to_csv( "outputs/entry_intent_log.csv", mode="a", index=False, header=False)
      
    trade_df = generate_trade(df)
    print("Generated trade Id successfully ")

    trade_logs = pd.DataFrame({ "Trade ID" : trade_df["trade_id"],
                                "Entry time"  : trade_df["entry_time"] ,
                                "Exit time" : trade_df["exit_time"] ,
                                "Stop loss" :trade_df['stop_loss'], 
                                "Target 1" : trade_df['T1'], 
                                "Target 2" : trade_df['T2'],
                                "Entry price" : trade_df["entry_price"],
                                "Exit price" : trade_df["exit_price"],
                                "Exit reasone" : trade_df["trade_status"],
                                "R multiple" : trade_df["R"],
                                "Setup score at entry" : trade_df['setup_score'],
                                "Regime at entry" : trade_df['regime']}) 
    
    trade_logs.to_csv( "outputs/trade_log.csv", mode="a", index=False, header=False)
  
    return trade_df

def get_market_data(symbol, period, interval):
    # Download data
    df = yf.download(
        symbol,
        period=period,
        interval=interval
    )
    
    # Reset index
    #df.reset_index(inplace=True)

    # Rename columns
    df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    
    # Timestamp
    df['timestamp'] = df.index[-1];

    # VWAP
    typical_price = ( df['high'] +  df['low'] + df['close'] ) / 3
    df['vwap'] = ( (typical_price * df['volume']).cumsum() / df['volume'].cumsum())

    # ATR 14
    df['atr_14'] = ta.atr( df['high'], df['low'], df['close'],length=14 )

    # Spread approximation
    df['spread_pct'] = ( (df['high'] - df['low']) / df['close'] ) * 100

    # Liquidity score
    df['liquidity_score'] = ( df['volume'] / (df['spread_pct'] + 0.01) )

    # Regime detection
    df['ema_20'] = ta.ema(df['close'], length=20)

    df['regime'] = np.where( df['close'] > df['ema_20'], 'TREND_UP', 'TREND_DOWN')

    # MSE state
    df['mse_state'] = np.where(df['close'] > df['vwap'], 'BULLISH_STRUCTURE', 'BEARISH_STRUCTURE')

    # IPSE alignment
    df['ipse_alignment'] = np.where((df['close'] > df['vwap']) & (df['close'] > df['ema_20']),'ALIGNED_BULLISH', 'ALIGNED_BEARISH')

    # Microstructure state
    df['microstructure_state'] = np.where( df['spread_pct'] < 0.5,'LIQUID', 'ILLIQUID')

    # MPS state
    df['mps_state'] = np.where( df['atr_14'] > df['atr_14'].rolling(20).mean(), 'EXPANSION','CONTRACTION')

    # Optional Open Interest placeholder
    df['oi'] = np.nan

    # Final columns
    final_df = df[[
        'timestamp',
        'open',
        'high',
        'low',
        'close',
        'volume',
        'vwap',
        'atr_14',
        'spread_pct',
        'liquidity_score',
        'oi',
        'mse_state',
        'regime',
        'ipse_alignment',
        'microstructure_state',
        'mps_state'
    ]]


    final_df.to_csv("data/sample_market_data.csv")
    print("Market data created successfully in file sample_market_data.csv")
 
    return final_df

def generate_trade(df):
    for i in range(len(df)):
        row = df.iloc[i]
        
        # Entry signal
        if row['entry_signal']:
            entry_price = row['close']
            entry_time = row['timestamp']
            stop_loss = (
                entry_price -
                row['atr_14']
            )

            target = (
                entry_price +
                (2 * row['atr_14'])
            )

            trade_id = (
                f"TRD-{i}"
            )

            exit_time = None
            exit_price = None
            trade_status = "OPEN"

            # -------------------------
            # Find exit candle
            # -------------------------
            for j in range(i + 1, len(df)):

                next_row = df.iloc[j]

                # Stop loss hit
                if next_row['low'] <= stop_loss:
                    exit_price = stop_loss
                    exit_time = next_row['timestamp']
                    trade_status = "STOP_LOSS"
                    break

                # Target hit
                if next_row['high'] >= target:
                    exit_price = target
                    exit_time = next_row['timestamp']
                    trade_status = "TARGET"
                    break
                            
            df["trade_id"] = trade_id
            df["entry_time"] = entry_time
            df["exit_time"] = exit_time
            df["entry_price"] = entry_price
            df["exit_price"] = exit_price
            df["trade_status"] = trade_status

    return df

def create_log_files():

    # Trade log csv
    columns = ["Trade ID", "Entry time", "Entry price", "Stop loss", "Target 1", "Target 2", "Exit time", "Exit price", 
               "Exit reason", "R multiple", "Setup score at entry", "Regime at entry"]
    df = pd.DataFrame(columns=columns)
    df.to_csv("outputs/trade_log.csv", index=False)
    print("trade_log.csv created successfully")

def create_entry_intent_log():

    columns = ["Timestamp", "Entry type", "Breakout level", "Retest zone", "Entry price",
                 "Stop loss", "Target 1", "Target 2","Reason codes"]

    df = pd.DataFrame(columns=columns)

    df.to_csv("outputs/entry_intent_log.csv", index=False)

    print("entry_intent_log.csv created successfully")