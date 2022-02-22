from datetime import datetime
from pandas import DataFrame
from typing import Tuple
from elo.elorating import PlayerElo, PlayersElo


def apply_elo(
    df_to_update: DataFrame, playersElo: dict, isatp: bool
) -> Tuple[DataFrame, dict]:
    """Complete the list of matches from the input dataframe with the Elo and Elo by Court ratings.
       Record all historical Elo rating by player/date into a dictionnary.
    Args:
        df_to_update (DataFrame): [description]
        playersElo (dict): dictionnaryt to update with elo history by player
        isatp (bool): [description]

    Returns:
        Tuple[DataFrame, dict]:
        - the input dataframe completed with the additionnal Elo rating columns:
        Elo1, nbElo1, EloAfter1, DaysLastElo1...Elo1Court, nbElo1Court ...
        - a dictionnary {<playerid>:PlayerElo} where Player Elo contains several dictionnaries
        with the historical elo for each date played
            - eloratings_clay
            - elomatchess_clay
            ...
    """
    (
        df_to_update["Elo1"],
        df_to_update["nbElo1"],
        df_to_update["EloAfter1"],
        df_to_update["DaysLastElo1"],
        df_to_update["Elo2"],
        df_to_update["nbElo2"],
        df_to_update["EloAfter2"],
        df_to_update["DaysLastElo2"],
        df_to_update["ProbaElo"],
        df_to_update["Elo1Court"],
        df_to_update["nbElo1Court"],
        df_to_update["EloAfter1Court"],
        df_to_update["DaysLastElo1Court"],
        df_to_update["Elo2Court"],
        df_to_update["nbElo2Court"],
        df_to_update["EloAfter2Court"],
        df_to_update["DaysLastElo2Court"],
        df_to_update["ProbaEloCourt"],
    ) = zip(
        *df_to_update.apply(
            lambda row: PlayersElo.build_elos_for_match(
                playersElo,
                row["P1"],
                row["P1Id"],
                # row["Rk1"],
                row["P2"],
                row["P2Id"],
                # row["Rk2"],
                row["SetsP1"],
                row["SetsP2"],
                row["TrnRk"],
                row["RoundId"],
                row["CourtId"],
                row["Date"],
                row["IsCompleted"],
                # isatp,
                True,
                True,
            ),
            axis=1,
        )
    )
    return df_to_update, playersElo


###########################################################################################
###########################################################################################
###########################################################################################
def set_last30d_elo_gain_match(
    row, playersElo, df_to_look_for_past_results: DataFrame
) -> Tuple[float, int, float, int]:

    datematch = row["Date"]
    # last 9M
    p1: PlayerElo = playersElo[row["P1Id"]]
    elo1court9m, nbelo1court9m = p1.get_lastXdays_elo_gain(
        row["Date"], df_to_look_for_past_results, 30
    )
    p2: PlayerElo = playersElo[row["P2Id"]]
    elo2court9m, nbelo2court9m = p2.get_lastXdays_elo_gain(
        row["Date"], df_to_look_for_past_results, 30
    )
    return elo1court9m, nbelo1court9m, elo2court9m, nbelo2court9m


def set_last30d_elo_gain_dataframe(
    df_to_update: DataFrame, df_to_look_for_past_results: DataFrame, playersElo
) -> DataFrame:
    (
        df_to_update.loc[:, ["EloGain30d1"]],
        df_to_update.loc[:, ["EloGain30d_nb1"]],
        df_to_update.loc[:, ["EloGain30d2"]],
        df_to_update.loc[:, ["EloGain30d_nb2"]],
    ) = zip(
        *df_to_update.apply(
            lambda row: set_last30d_elo_gain_match(
                row, playersElo, df_to_look_for_past_results
            ),
            axis=1,
        )
    )
    # save a dataframe with all matches and Elo rating of each player for the matches
    df_to_update.to_csv("./results/dfWithElos9M_peak_30d.csv")
    return df_to_update


###########################################################################################
###########################################################################################
###########################################################################################
def set_last9m_court_elo_match(
    row, playersElo, df_to_look_for_past_results: DataFrame
) -> Tuple[float, int, float, int]:

    print(row["Date"])
    # last 9M
    p1: PlayerElo = playersElo[row["P1Id"]]
    elo1court9m, nbelo1court9m = p1.build_elo_court_cat_lastXmonths(
        row["Date"], df_to_look_for_past_results, 9
    )
    p2: PlayerElo = playersElo[row["P2Id"]]
    elo2court9m, nbelo2court9m = p2.build_elo_court_cat_lastXmonths(
        row["Date"], df_to_look_for_past_results, 9
    )
    return elo1court9m, nbelo1court9m, elo2court9m, nbelo2court9m


def set_last9m_court_elo_dataframe(
    df_to_update: DataFrame,
    df_to_look_for_past_results: DataFrame,
    playersElo,
    path: str = "./results/",
) -> DataFrame:
    (
        df_to_update.loc[:, ["Elo1court9m"]],
        df_to_update.loc[:, ["nbElo1court9m"]],
        df_to_update.loc[:, ["Elo2court9m"]],
        df_to_update.loc[:, ["nbElo2court9m"]],
    ) = zip(
        *df_to_update.apply(
            lambda row: set_last9m_court_elo_match(
                row, playersElo, df_to_look_for_past_results
            ),
            axis=1,
        )
    )
    df_to_update = apply_mixed_elo2(df_to_update)
    # save a dataframe with all matches and Elo rating of each player for the matches
    df_to_update.to_csv(path + "dfWithElos9m.csv")
    return df_to_update


###########################################################################################
###########################################################################################
###########################################################################################


def get_mixed_elo(row) -> float:
    nbsets_won1: int = row["SetsP1"]
    nbsets_won2: int = row["SetsP2"]
    is_completed: bool = row["IsCompleted"]
    if is_completed:
        elomix1 = PlayerElo.get_elo_from_mixed(
            row["Elo1"], row["Elo1Court"], row["nbElo1Court"]
        )
        elomix2 = PlayerElo.get_elo_from_mixed(
            row["Elo2"], row["Elo2Court"], row["nbElo2Court"]
        )
        return PlayerElo.get_match_proba(
            elomix2[0], elomix1[0], max(nbsets_won1, nbsets_won2)
        )
    else:
        elomix1 = PlayerElo.get_elo_from_mixed(
            row["Elo1"], row["Elo1Court"], row["nbElo1Court"]
        )
        elomix2 = PlayerElo.get_elo_from_mixed(
            row["Elo2"], row["Elo2Court"], row["nbElo2Court"]
        )
        return PlayerElo.get_match_proba(
            elomix2[0], elomix1[0], max(nbsets_won1, nbsets_won2)
        )


def get_mixed_elo2(row) -> float:
    nbsets_won1: int = row["SetsP1"]
    nbsets_won2: int = row["SetsP2"]
    is_completed: bool = row["IsCompleted"]
    if is_completed:
        elomix1 = PlayerElo.get_elo_from_mixed2(
            row["Elo1"],
            row["Elo1Court"],
            row["nbElo1Court"],
            row["Elo1court9m"],
            row["nbElo1court9m"],
        )
        elomix2 = PlayerElo.get_elo_from_mixed2(
            row["Elo2"],
            row["Elo2Court"],
            row["nbElo2Court"],
            row["Elo2court9m"],
            row["nbElo2court9m"],
        )
        return PlayerElo.get_match_proba(
            elomix2[0], elomix1[0], max(nbsets_won1, nbsets_won2)
        )
    else:
        elomix1 = PlayerElo.get_elo_from_mixed2(
            row["Elo1"],
            row["Elo1Court"],
            row["nbElo1Court"],
            row["Elo1court9m"],
            row["nbElo1court9m"],
        )
        elomix2 = PlayerElo.get_elo_from_mixed2(
            row["Elo2"],
            row["Elo2Court"],
            row["nbElo2Court"],
            row["Elo2court9m"],
            row["nbElo2court9m"],
        )
        return PlayerElo.get_match_proba(
            elomix2[0], elomix1[0], max(nbsets_won1, nbsets_won2)
        )


def apply_mixed_elo(df_to_update: DataFrame) -> DataFrame:
    """Add a column ProbaEloMix which is the proba of the match using average of Elo and EloCourt for both players

    Args:
        df (DataFrame): [description]

    Returns:
        DataFrame: [description]
    """
    df_to_update["ProbaEloMix"] = df_to_update.apply(
        lambda row: get_mixed_elo(row), axis=1
    )
    return df_to_update


def apply_mixed_elo2(df_to_update: DataFrame) -> DataFrame:
    """Add a column ProbaEloMix2 which is the proba of the match using average of Elo, EloCourt, Elo9M for both players

    Args:
        df (DataFrame): [description]

    Returns:
        DataFrame: [description]
    """
    df_to_update["ProbaEloMix2"] = df_to_update.apply(
        lambda row: get_mixed_elo2(row), axis=1
    )
    return df_to_update
