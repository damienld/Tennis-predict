"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
from datetime import datetime

from pandas.core.frame import DataFrame
from elo.elorating import PlayersElo, PlayerElo
from main import load_data
import pandas as pd
import pytest
import main


@pytest.fixture
def load_dftest() -> DataFrame:
    try:
        df = pd.read_csv("./tests/df.csv")
        df.Date = pd.to_datetime(df.Date, format="%d/%m/%y %H:%M:%S")
    except:
        df = load_data(True, 2014, 2014)
        # df = df.query("(P1Id==673 | P2Id==673)")  # David Ferrer
        df.to_csv("./tests/df.csv")
        df.Date = pd.to_datetime(df.Date, format="%d/%m/%y %H:%M:%S")
    return df


@pytest.fixture
def loadPlayers_elos(dftest: DataFrame) -> PlayersElo:
    try:
        playersElo = PlayersElo.deserialize("./tests/AllElo.json")
        dftest.to_csv("./tests/dfWithElos.csv")
    except:
        playersElo: PlayersElo = {}
        # create/build the matches and elo files
        isatp = True
        (
            dftest["Elo1"],
            dftest["nbElo1"],
            dftest["EloAfter1"],
            dftest["DaysLastElo1"],
            dftest["Elo2"],
            dftest["nbElo2"],
            dftest["EloAfter2"],
            dftest["DaysLastElo2"],
            dftest["ProbaElo"],
            dftest["Elo1Court"],
            dftest["nbElo1Court"],
            dftest["EloAfter1Court"],
            dftest["DaysLastElo1Court"],
            dftest["Elo2Court"],
            dftest["nbElo2Court"],
            dftest["EloAfter2Court"],
            dftest["DaysLastElo2Court"],
            dftest["ProbaEloCourt"],
        ) = zip(
            *dftest.apply(
                lambda row: PlayerElo.update_elos_matches(
                    playersElo,
                    row["P1"],
                    row["P1Id"],
                    row["Rk1"],
                    row["P2"],
                    row["P2Id"],
                    row["Rk2"],
                    row["SetsP1"],
                    row["SetsP2"],
                    row["TrnRk"],
                    row["RoundId"],
                    row["CourtId"],
                    row["Date"],
                    row["IsCompleted"],
                    isatp,
                    True,
                    True,
                ),
                axis=1,
            )
        )
        # player: PlayerElo = playersElo.get(673, None)
        dftest.to_csv("./tests/dfWithElos.csv")
        # save the historical rating for each player
        PlayersElo.serialize(playersElo, "./tests/AllElo.json")

    return df


def test_load_dftest(load_dftest):
    df = load_dftest()
    assert len(df) > 50 and type(list(df.loc[:, "Date"])[0]) == pd.Timestamp


class Test_Elo:
    def test_get_elo_court_cat_lastXmonths():
        p: PlayerElo = playersElo[673]
        p.build_elo_court_cat_lastXmonths(datetime(2014, 12, 10), 1, 6)

    def test_set_elos(self, get_dftest):
        df = get_dftest
        playersElo: PlayersElo = {}
        # create/build the matches and elo files
        isatp = True
        (
            df["Elo1"],
            df["nbElo1"],
            df["EloAfter1"],
            df["DaysLastElo1"],
            df["Elo2"],
            df["nbElo2"],
            df["EloAfter2"],
            df["DaysLastElo2"],
            df["ProbaElo"],
            df["Elo1Court"],
            df["nbElo1Court"],
            df["EloAfter1Court"],
            df["DaysLastElo1Court"],
            df["Elo2Court"],
            df["nbElo2Court"],
            df["EloAfter2Court"],
            df["DaysLastElo2Court"],
            df["ProbaEloCourt"],
        ) = zip(
            *df.apply(
                lambda row: PlayerElo.update_elos_matches(
                    playersElo,
                    row["P1"],
                    row["P1Id"],
                    row["Rk1"],
                    row["P2"],
                    row["P2Id"],
                    row["Rk2"],
                    row["SetsP1"],
                    row["SetsP2"],
                    row["TrnRk"],
                    row["RoundId"],
                    row["CourtId"],
                    row["Date"],
                    row["IsCompleted"],
                    isatp,
                    True,
                    True,
                ),
                axis=1,
            )
        )
        player: PlayerElo = playersElo.get(673, None)
        df.to_csv("./results/dfTestWithElo.csv")
        # save the historical rating for each player
        PlayersElo.serialize(playersElo, "./results/AllElo.json")
        # TODO
        # assert(player.)

    def test_update_elos_matches(self):
        df = load_dftest()
        isatp = True
        row = df.iloc[0]
        playersElo: PlayersElo = {}
        (
            elo1,
            nbelo1,
            elo1after,
            days_since_last_elo1,
            elo2,
            nbelo2,
            elo2after,
            days_since_last_elo2,
            proba_match1,
            elo1_court,
            nbelo1_court,
            elo1_court_after,
            days_since_last_elo1_court,
            elo2_court,
            nbelo2_court,
            elo2_court_after,
            days_since_last_elo2_court,
            proba_match1_court,
        ) = PlayerElo.update_elos_matches(
            playersElo,
            row["P1"],
            row["P1Id"],
            row["Rk1"],
            row["P2"],
            row["P2Id"],
            row["Rk2"],
            row["SetsP1"],
            row["SetsP2"],
            row["TrnRk"],
            row["RoundId"],
            row["CourtId"],
            row["Date"],
            row["IsCompleted"],
            isatp,
            True,
            True,
        )
        assert (
            elo1 == 1500
            and nbelo1 == 0
            and round(elo1after) == 1502
            and days_since_last_elo1 == -1
            and elo2 == 1500
            and nbelo2 == 0
            and round(elo2after) == 1498
            and days_since_last_elo2 == -1
            and proba_match1 == 0.5
            and len(playersElo) == 2
        )


def test_get_datetime():
    res = PlayersElo.get_datetime(202111041)
    assert res == datetime(2021, 11, 4)


def test_get_date_eloformat():
    res = PlayersElo.get_date_eloformat(datetime(2021, 11, 4))
    assert res == 202111040
