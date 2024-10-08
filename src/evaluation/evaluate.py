from typing import List
import pandas as pd
import numpy as np


def quantile_loss(y_true: np.ndarray, y_pred: np.ndarray, quantile: float) -> float:
    """
    Calculate the quantile loss between the true and predicted values.
DEMOND FORECAST/sales-forecasting/src/evaluation/evaluate.py
    The quantile loss measures the deviation between the true
    and predicted values at a specific quantile.

    Parameters
    ----------
    y_true : np.ndarray
        The true values.
    y_pred : np.ndarray
        The predicted values.
    quantile : float
        The quantile to calculate the loss for.

    Returns
    -------
    float
        The quantile loss.
    """
    # Вычисляем разницу между истинными и предсказанными значениями
    errors = y_true - y_pred
    
    # Вычисляем потери в зависимости от ошибки и выбранного квантили
    loss = np.maximum(quantile * errors, (quantile - 1) * errors)

    # Возвращаем среднее значение потерь
    return np.mean(loss)

def evaluate_model(
    df_true: pd.DataFrame,
    df_pred: pd.DataFrame,
    quantiles: List[float] = [0.1, 0.5, 0.9],
    horizons: List[int] = [7, 14, 21],
) -> pd.DataFrame:
    """Evaluate model on data.

    Parameters
    ----------
    df_true : pd.DataFrame
        True values.
    df_pred : pd.DataFrame
        Predicted values.
    quantiles : List[float], optional
        Quantiles to evaluate on, by default [0.1, 0.5, 0.9].
    horizons : List[int], optional
        Horizons to evaluate on, by default [7, 14, 21].

    Returns
    -------
    pd.DataFrame
        Evaluation results.
    """
    losses = {}

    for quantile in quantiles:
        for horizon in horizons:
            true = df_true[f"next_{horizon}d"].values
            pred = df_pred[f"pred_{horizon}d_q{int(quantile*100)}"].values
            loss = quantile_loss(true, pred, quantile)

            losses[(quantile, horizon)] = loss

    losses = pd.DataFrame(losses, index=["loss"]).T.reset_index()
    losses.columns = ["quantile", "horizon", "avg_quantile_loss"]  # type: ignore

    return losses

def test_losses(df_pred: pd.DataFrame):
    pass