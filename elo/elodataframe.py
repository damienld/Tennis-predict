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


###########################################################################################


def get_mixed_elo(row) -> float:
    elomix1 = PlayerElo.get_elo_from_mixed(
        row["Elo1"], row["Elo1Court"], row["nbElo1Court"]
    )
    elomix2 = PlayerElo.get_elo_from_mixed(
        row["Elo2"], row["Elo2Court"], row["nbElo2Court"]
    )
    return PlayerElo.get_match_proba(elomix2[0], elomix1[0])


def apply_mixed_elo(df: DataFrame) -> DataFrame:
    """Add a column ProbaEloMix which is the proba of the match using average of Elo and EloCourt for both players

    Args:
        df (DataFrame): [description]

    Returns:
        DataFrame: [description]
    """
    df["ProbaEloMix"] = df.apply(lambda row: get_mixed_elo(row), axis=1)
    return df
