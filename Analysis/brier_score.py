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
    
def calc_brier(df: DataFrame, col_result: str, col_prediction: str)->DataFrame:
    
    df["brier"] = df.apply(lambda row: apply_brier(row[col_result], row[col_prediction]), axis=1)
    return df