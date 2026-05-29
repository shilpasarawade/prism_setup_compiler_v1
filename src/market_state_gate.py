import numpy as np


def market_state_gateway(df):
    # -------------------------
    # Trend condition
    # -------------------------
    trend_up = ( df['close'] > df['vwap'])

    # -------------------------
    # Volatility condition
    # -------------------------
    atr_ok = ( df['atr_14'] > 5 )

    # -------------------------
    # Liquidity condition
    # -------------------------
    liquidity_ok = ( df['volume'] > 100000 )

    # -------------------------
    # Spread condition
    # -------------------------
    spread_ok = ( df['spread_pct'] < 0.5)

    # -------------------------
    # Market state
    # -------------------------
    df['market_state'] = np.where(
        trend_up &
        atr_ok &
        liquidity_ok &
        spread_ok,
        "TRADE_ALLOWED",
        "BLOCKED"
    )

    return df

