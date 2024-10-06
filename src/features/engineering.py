import pandas as pd
from typing import Dict, Tuple, Optional


def add_features(
    df: pd.DataFrame,
    features: Dict[str, Tuple[str, int, str, Optional[int]]],
) -> None:
    """
    Add rolling features to the DataFrame based on the specified aggregations.
    For each sku_id, the features are computed as the aggregations of the last N-days.
    Current date is always included into rolling window.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to add the feature to. Changes are applied inplace.
    features : Dict[str, Tuple[str, int, str, Optional[int]]]
        Dictionary with the following structure:
        {
            "feature_name": ("agg_col", "days", "aggregation_function", "quantile"),
            ...
        }
        where:
            - feature_name: name of the feature to add
            - agg_col: name of the column to aggregate
            - int: number of days to include into rolling window
            - aggregation_function: one of the following: "quantile", "avg"
            - int: quantile to compute (only for "quantile" aggregation_function)

    Raises
    ------
    ValueError
        If aggregation_function is not one of the following: "quantile", "avg"
    """
    for feature_name, (agg_col, days, agg_func, quantile) in features.items():
        if agg_func == "quantile":
            df[feature_name] = (
                df.groupby("sku_id")[agg_col]
                .rolling(window=days)
                .quantile(quantile / 100)
                .reset_index(level=0, drop=True)
            )
        elif agg_func == "avg":
            df[feature_name] = (
                df.groupby("sku_id")[agg_col]
                .rolling(window=days)
                .mean()
                .reset_index(level=0, drop=True)
            )
        else:
            raise ValueError(f"Unknown aggregation function: {agg_func}")



def add_targets(df: pd.DataFrame, targets: Dict[str, Tuple[str, int]]) -> None:
    """
    Add targets to the DataFrame based on the specified aggregations.
    For each sku_id, the target is computed as the aggregation of the next N-days.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to add the target to. Changes are applied inplace.
    targets : Dict[str, Tuple[str, int]]
        Dictionary with the following structure:
        {
            "target_name": ("agg_col", "days"),
            ...
        }
        where:
            - target_name: name of the target to add
            - agg_col: name of the column to aggregate
            - days: number of next days to include in the rolling window
            (current date is always excluded from the rolling window)
    """
    for target_name, (agg_col, days) in targets.items():
        # Инвертируем порядок строк
        df_inverted = df.iloc[::-1]
        
        df[target_name] = (
            df_inverted.groupby("sku_id")[agg_col]
            .shift(1)  
            .groupby(df_inverted['sku_id'])  
            .rolling(window=days)
            .sum()
            .reset_index(level=0, drop=True)
        )
        
        # Вернём инвертированные данные в исходный порядок
        df[target_name] = df[target_name].iloc[::-1]