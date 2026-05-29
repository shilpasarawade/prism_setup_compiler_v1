import pandas as pd
import numpy as np

def create_setup_score_log():
    
    # Setup validation Report json
    # Bar-by-bar score with component scores and final tier.
    columns = ["Trade ID", "Structure Score", "Positioning Score", "regime_score" , "microstructure_score", 
               "Interaction Score", "setup_score", "Tier"]
    df = pd.DataFrame(columns=columns)
    df.to_csv("outputs/setup_score_log.csv", index=False)
    print("setup_score_log.csv created successfully")

def getSetupScore(df):

    # -------------------------
    # Structure Score
    # -------------------------
    df['structure_score'] = np.where(
        df['close'] > df['breakout_level'],
        8.0,
        4.0
    )

    # -------------------------
    # Positioning Score
    # Based on close position
    # -------------------------
    df['positioning_score'] = (
        df['close_position'] * 10
    )

    # -------------------------
    # Regime Score
    # -------------------------
    df['regime_score'] = np.where(
        df['close'] > df['vwap'],
        8.0,
        3.0
    )

    # -------------------------
    # Microstructure Score
    # Lower spread = better
    # -------------------------
    df['microstructure_score'] = np.where(
        df['spread_pct'] < 0.5,
        8.0,
        4.0
    )

    # -------------------------
    # Interaction Score
    # Retest interaction quality
    # -------------------------
    df['interaction_score'] = np.where(
        df['retest_condition'],
        8.0,
        3.0
    )

    # -------------------------
    # Final Setup Score
    # -------------------------
    df['setup_score'] = (
        df['structure_score'] * 0.25 +
        df['positioning_score'] * 0.25 +
        df['regime_score'] * 0.15 +
        df['microstructure_score'] * 0.15 +
        df['interaction_score'] * 0.20
    )

    # -------------------------
    # Tier Mapping
    # -------------------------
    conditions = [
        (df['setup_score'] < 5.5),

        (df['setup_score'] >= 5.5) &
        (df['setup_score'] < 6.5),

        (df['setup_score'] >= 6.5) &
        (df['setup_score'] < 7.5),

        (df['setup_score'] >= 7.5)
    ]

    tiers = [
        'IGNORE',
        'MINIMUM',
        'STRONG',
        'PREMIUM'
    ]

    df['tier'] = np.select(
        conditions,
        tiers,
        default='IGNORE'
    )

    create_setup_score_log()
    setup_score_log = pd.DataFrame({ "Trade ID" : df["trade_id"],
                                "structure Score"  : df["structure_score"] ,
                                "Regime Score" : df["regime_score"] ,
                                "Microstructure Score" :df['microstructure_score'], 
                                "Interaction score" : df["interaction_score"],
                                "Setup score" : df['setup_score'],
                                "Tier" : df['tier']}) 
    
    setup_score_log.to_csv( "outputs/setup_score_log.csv", mode="a", index=False, header=False)
  
    return df