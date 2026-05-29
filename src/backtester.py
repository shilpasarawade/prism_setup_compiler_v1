import pandas as pd
import numpy as np
import json
from datetime import datetime


def backtest_summary(trades_df):

    
    # -------------------------
    # Total trades
    # -------------------------
    total_trades = len(trades_df)

    # -------------------------
    # Wins / Losses
    # -------------------------
    wins_df = trades_df[
        trades_df['R'] > 0
    ]

    losses_df = trades_df[
        trades_df['R'] <= 0
    ]

    wins = len(wins_df)

    losses = len(losses_df)

    # -------------------------
    # Win rate
    # -------------------------
    win_rate = (

        (wins / total_trades) * 100

        if total_trades > 0

        else 0
    )

    # -------------------------
    # Average R
    # -------------------------
    average_r = float(
        trades_df['R'].mean()
    )

    # -------------------------
    # Gross R
    # -------------------------
    gross_r = float(
        trades_df['R'].sum()
    )

    # -------------------------
    # Equity curve
    # -------------------------
    trades_df['equity_curve'] = (
        trades_df['R']
        .cumsum()
    )

    # -------------------------
    # Max drawdown
    # -------------------------
    rolling_max = (
        trades_df['equity_curve']
        .cummax()
    )

    drawdown = (
        trades_df['equity_curve']
        - rolling_max
    )

    max_drawdown_r = float(
        drawdown.min()
    )

    # -------------------------
    # Expected value
    # -------------------------
    avg_win = (

        wins_df['R'].mean()

        if wins > 0

        else 0
    )

    avg_loss = abs(

        losses_df['R'].mean()

        if losses > 0

        else 0
    )

    loss_rate = (
        1 - (win_rate / 100)
    )

    expected_value_r = (

        (avg_win * (win_rate / 100))

        -

        (avg_loss * loss_rate)
    )

    # -------------------------
    # Profit factor
    # -------------------------
    gross_profit = (
        wins_df['R'].sum()
    )

    gross_loss = abs(
        losses_df['R'].sum()
    )

    profit_factor = (

        gross_profit / gross_loss

        if gross_loss > 0

        else np.inf
    )


    # -------------------------
    # JSON Summary
    # -------------------------
    summary = {

        "generated_at":
        str(datetime.now()),

        "total_trades":
        total_trades,

        "wins":
        wins,

        "losses":
        losses,

        "win_rate":
        round(win_rate, 2),

        "average_r":
        round(average_r, 2),

        "gross_r":
        round(gross_r, 2),

        "max_drawdown_r":
        round(max_drawdown_r, 2),

        "expected_value_r":
        round(expected_value_r, 2),

        "profit_factor":
        round(profit_factor, 2),

      }

    save_backtest_summary(summary)


def save_backtest_summary(summary):

    filename = "outputs/backtest_summary.json"

    with open(filename, "w") as f:

        json.dump(
            summary,
            f,
            indent=4,
            default=str
        )

    print(
        f"{filename} created successfully"
    )
