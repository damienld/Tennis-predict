import pandas as pd
from pandas import DataFrame


def analyse_out_periods_predictions(dfWithElos: DataFrame):
    """Filter on the number of days sicne last match and check the prediction results

    Args:
        dfWithElos (DataFrame): A dataframe containing the list of matches with the elo ratings

    Returns:
        None (just print the results to the console)
    """
    # keep only out periods and check results
    # be careful an out period is not strictly given by DaysSinceLastElo
    # because the players might have played at a lower level
    # hence let s look just for 100 players who rarely play at lower levels (itf<25k)
    dfOutPeriods = dfWithElos[
        (dfWithElos["DaysLastElo2"] > 50) & (dfWithElos["Rk2"] <= 100)
    ]
    print(dfOutPeriods["brier"].mean())
    dfOutPeriods = dfOutPeriods[dfOutPeriods["DaysLastElo2"] > 100]
    print(dfOutPeriods["brier"].mean())
    dfOutPeriods = dfOutPeriods[dfOutPeriods["DaysLastElo2"] > 150]
    print(dfOutPeriods["brier"].mean())
    dfOutPeriods = dfOutPeriods[dfOutPeriods["DaysLastElo2"] > 250]
    print(dfOutPeriods["brier"].mean())
