import pandas as pd
from pandas import DataFrame
from typing import Tuple

def calc_kelly_stake(myproba:float, odds: float, minstake=0.5, maxstake=3)->float:
    """Calculate the stake associated to the value of the bet

    Args:
        myproba (float): my prediction
        odds (float): actual odds
        minstake (float, optional): minimum stake (under this stake => 0). Defaults to 0.5.

    Returns:
        [type]: [description]
    """
    kelly = 15*( (odds - 1) * myproba - (1 - myproba)) / (odds - 1)
    if (kelly >= minstake):
        return min(3, round(kelly, 1))
    else:
        return 0

def apply_roi(oddsP1: float, oddsP2: float, predictionP1win: float, result: int) -> Tuple[int, float]:
    """[summary]

    Args:
        oddsP1 (float): [description]
        oddsP2 (float): [description]
        predictionP1win (float): prediction probability
        result (int): 0=P1 won, 1=P2 won

    Returns: Tuple
        (int): The stake in units (0 to 3u)
        (float): The net benefit for this bet
    """
    isP1won = result==0
    margin = 1/oddsP1 + 1/oddsP2
    if predictionP1win <= 0 or predictionP1win >= 1 or oddsP1 <= 1 or oddsP1 >= 50  or oddsP2 <= 1 or oddsP2 >= 50 or margin>1.1 or margin < 0.98:
        return (0,0)
    stakeP1=calc_kelly_stake(predictionP1win, oddsP1)
    stakeP2=calc_kelly_stake(1-predictionP1win, oddsP2)
    indexbet = -1
    if (stakeP1==stakeP2==0):
        return (0,0)
    elif (stakeP1 >= stakeP2):
        indexbet = 0
    else:#(stakeP1 < stakeP2):
        indexbet = 1
    match (isP1won):
        case True:
            #p1 won
            if (indexbet == 0):
                return (stakeP1, stakeP1 * (oddsP1-1))
            else:
                return (stakeP2, -stakeP2)
        case False:
            #p2 won
            if (indexbet == 1):
                return (stakeP2, stakeP2 * (oddsP2-1))
            else:
                return (stakeP1, -stakeP1)
    
def calc_roi(df: DataFrame, col_odds1: str, col_odds2: str, col_result: str, col_prediction: str, stake_colname: str="stake_roi1"
, profit_colname: str="pnl_roi1")->DataFrame:
    """The ROI is calculated by applying a Kelly criterion on the difference between
    the prediction and the actual odds.

    Args:
        df (DataFrame): Will be used to get columns data and will be returned with the new column @newcolname
        col_result (str): Name of the column with the result value (format int: 0 or 1 (player 1 or player 2 won))
        col_prediction (str): Name of the columns with the probability to be tested
        newcolname (str, optional): Name fo the columns to input the result. Defaults to "brier".

    Returns:
        DataFrame: with the new column "brier"
    """
    (df[stake_colname],df[profit_colname]) = zip(*df.apply(lambda row: apply_roi(row[col_odds1], row[col_odds2], row[col_prediction], row[col_result]), axis=1))
    return df