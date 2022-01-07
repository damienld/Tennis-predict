from datetime import datetime
from pandas import DataFrame
from typing import Tuple
from elo.elorating import PlayerElo


def set_peak_elo_match(row, playersElo: DataFrame) -> Tuple[float, int, float, int]:

    print(row["Date"])
    # last 9M
    p1: PlayerElo = playersElo[row["P1Id"]]
    elopeak1, daysince1 = p1.get_peak_Elo(row["Date"])
    p2: PlayerElo = playersElo[row["P2Id"]]
    elopeak2, daysince2 = p2.get_peak_Elo(row["Date"])
    return elopeak1, daysince1, elopeak2, daysince2


def set_peak_elo(df: DataFrame, playersElo) -> DataFrame:
    """Add 2 columns PeakElo and PeakEloSince to a dataframe containing Date, P1Id and P2Id fields

    Args:
        df (DataFrame): the dataframe from where we read row by row (match by match)
        playersElo ([type]): dict <id>:[eloratings_history]

    Returns:
        DataFrame: the input dataframe with 2 additionnal columns PeakElo, PeakEloSince
    """
    (
        df.loc[:, ["PeakElo1"]],
        df.loc[:, ["PeakEloSince1"]],
        df.loc[:, ["PeakElo2"]],
        df.loc[:, ["PeakEloSince2"]],
    ) = zip(
        *df.apply(
            lambda row: set_peak_elo_match(row, playersElo),
            axis=1,
        )
    )
    # save a dataframe with all matches and Elo rating of each player for the matches
    df.to_csv("./results/dfWithElos9m_peak.csv")
    return df
