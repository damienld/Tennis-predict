from datetime import datetime
from pandas import DataFrame
from typing import Tuple
from elo.elorating import PlayerElo


"""def get_peak_Elo(
    playerid: int, dateend: datetime, df: DataFrame
) -> Tuple[int, datetime]:
    list_elos = df.loc[
        (df["Date"] < dateend.strftime("%Y-%m-%d")) & ((df["P1Id"] == playerid))
    ]
    index_elo_max_asP1 = list_elos[["Elo1After"]].idxmax()
    val_elo_max_asP1 = list_elos.loc[index_elo_max_asP1]["Elo1After"]
    date_elo_max_asP1 = list_elos.loc[index_elo_max_asP1]["Date"]
    list_elos = df.loc[
        (df["Date"] < dateend.strftime("%Y-%m-%d")) & ((df["P2Id"] == playerid))
    ]
    index_elo_max_asP2 = list_elos[["Elo2After"]].idxmax()
    val_elo_max_asP2 = list_elos.loc[index_elo_max_asP2]["Elo2After"]
    date_elo_max_asP2 = list_elos.loc[index_elo_max_asP2]["Date"]

    val_elo = index_elo_max_asP1
    date_elo_max = date_elo_max_asP1

    if val_elo_max_asP2 > val_elo_max_asP1:
        val_elo = index_elo_max_asP2
        date_elo_max = date_elo_max_asP2

    return val_elo, date_elo_max"""


def set_last9m_court_elo_match(
    row, playersElo, df2: DataFrame
) -> Tuple[float, int, float, int]:

    print(row["Date"])
    # last 9M
    p1: PlayerElo = playersElo[row["P1Id"]]
    elo1court9m, nbelo1court9m = p1.get_elo_court_cat_lastXmonths(row["Date"], df2, 9)
    p2: PlayerElo = playersElo[row["P2Id"]]
    elo2court9m, nbelo2court9m = p2.get_elo_court_cat_lastXmonths(row["Date"], df2, 9)
    # Peak Elo
    return elo1court9m, nbelo1court9m, elo2court9m, nbelo2court9m


def set_last9m_court_elo_dataframe(df: DataFrame, df2, playersElo) -> DataFrame:
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
