from datetime import datetime
from pandas import DataFrame
from typing import Tuple
from elo.elorating import PlayerElo


def set_last9m_court_elo_match(
    row, playersElo, df2: DataFrame
) -> Tuple[float, int, float, int]:

    print(row["Date"])
    # last 9M
    p1: PlayerElo = playersElo[row["P1Id"]]
    elo1court9m, nbelo1court9m = p1.get_elo_court_cat_lastXmonths(row["Date"], df2, 9)
    p2: PlayerElo = playersElo[row["P2Id"]]
    elo2court9m, nbelo2court9m = p2.get_elo_court_cat_lastXmonths(row["Date"], df2, 9)
    return elo1court9m, nbelo1court9m, elo2court9m, nbelo2court9m


def set_last9m_court_elo_dataframe(
    df: DataFrame, df2: DataFrame, playersElo
) -> DataFrame:
    (
        df.loc[:, ["Elo1court9m"]],
        df.loc[:, ["nbElo1court9m"]],
        df.loc[:, ["Elo2court9m"]],
        df.loc[:, ["nbElo2court9m"]],
    ) = zip(
        *df.apply(
            lambda row: set_last9m_court_elo_match(row, playersElo, df2),
            axis=1,
        )
    )
    # save a dataframe with all matches and Elo rating of each player for the matches
    df.to_csv("./results/dfWithElos9m.csv")
    return df
