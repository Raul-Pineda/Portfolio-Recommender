"""Portfolio simulation — buy the model's top picks each quarter, track returns."""

import numpy as np
import pandas as pd


def simulate_portfolio(test_df, score_col="predicted_score", return_col="forward_return",
                       quarter_col="quarter", top_n=30, risk_free_rate=0.05):
    """Buy top-N stocks each quarter (equal weight), return CAGR, Sharpe, max drawdown."""
    if return_col not in test_df.columns:
        return {"cagr": None, "sharpe": None, "max_drawdown": None, "period_returns": []}

    # Each quarter: pick top-N stocks, average their returns
    period_returns = []
    for q in sorted(test_df[quarter_col].unique()):
        q_data = test_df[test_df[quarter_col] == q]
        top = q_data.nlargest(min(top_n, len(q_data)), score_col)
        avg_ret = top[return_col].mean()
        if np.isfinite(avg_ret):
            period_returns.append(float(avg_ret))

    if not period_returns:
        return {"cagr": None, "sharpe": None, "max_drawdown": None, "period_returns": []}

    r = np.array(period_returns)
    n = len(r)
    n_years = n / 4  # quarterly data

    # CAGR — average annual growth rate
    cumulative = np.prod(1 + r)
    cagr = float(cumulative ** (1 / n_years) - 1) if (n_years > 0 and cumulative > 0) else None

    # Sharpe — return per unit of risk
    if n >= 2:
        ann_mean = float(np.mean(r) * 4)
        ann_std = float(np.std(r, ddof=1) * np.sqrt(4))
        sharpe = (ann_mean - risk_free_rate) / ann_std if ann_std > 1e-10 else 0.0
    else:
        sharpe = 0.0

    # Max drawdown — worst peak-to-trough drop
    cum = np.cumprod(1 + r)
    max_drawdown = float(np.min((cum - np.maximum.accumulate(cum)) / np.maximum.accumulate(cum)))

    return {"cagr": cagr, "sharpe": float(sharpe), "max_drawdown": max_drawdown,
            "period_returns": period_returns, "mean_return": float(np.mean(r)), "n_periods": n}
