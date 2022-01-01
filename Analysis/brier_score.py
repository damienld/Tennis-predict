import pandas as pd
from pandas.core.frame import DataFrame

def apply_brier(col_result: int, col_prediction: float):
    if col_prediction <= 0 or col_prediction >= 1:
        return 0
    match (col_result):
        case 0:
            #p1 won
            return (1- col_prediction)**2
        case 1:
            #p2 won
            return (0- col_prediction)**2
        case _:
            return 0 
    
def calc_brier(df: DataFrame, col_result: str, col_prediction: str, newcolname: str="brier")->DataFrame:
    """[summary]

    Args:
        df (DataFrame): Will be used to get columns data and will be returned with the new column @newcolname
        col_result (str): Name of the column with the result value (format int: 0 or 1 (player 1 or player 2 won))
        col_prediction (str): Name of the columns with the probability to be tested
        newcolname (str, optional): Name fo the columns to input the result. Defaults to "brier".

    Returns:
        DataFrame: with the new column
    """
    df[newcolname] = df.apply(lambda row: apply_brier(row[col_result], row[col_prediction]), axis=1)
    return df