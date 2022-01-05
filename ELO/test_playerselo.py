"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
from datetime import datetime

from pandas.core.frame import DataFrame
from elo.elorating import PlayersElo, PlayerElo
from main import get_data
import pandas as pd
import typing

# @pytest.fixture  # (scope="session", autouse=True)
def get_dftest() -> DataFrame:
    try:
        df = pd.read_csv("./results/dfTest.csv")
        df.Date = pd.to_datetime(df.Date, format="%d/%m/%y %H:%M:%S")
    except:
        df = get_data(True, 2013, 2013)
        df = df.query("(P1Id==673 | P2Id==673)")
        df.to_csv("./results/dfTest.csv")
    return df


def test_file_test():
    df = get_dftest()
    assert len(df) > 50 and type(list(df.loc[:, "Date"])[0]) == pd.Timestamp


class Test_Elo:
    def test_elo_1(self):
        df = get_dftest()
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
        # df.to_csv("./results/dfTestWithElo.csv")
        # TODO
        # assert(player.)

    def test_update_elos_matches(self):
        df = get_dftest()
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
