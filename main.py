"""
1-Create a virtual environment in VS Code:
> python -m venv tennis-predict_venv  

2-Activate the venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
tennis-predict_venv\scripts\activate
3 - Select your new environment from the Palette:Python: Select Interpreter (might need to refresh)
4 - Install the packages
python -m pip install matplotlib
5 - pip freeze > requirements.txt

Set up Black auto-formatting: https://dev.to/adamlombard/how-to-use-the-black-python-code-formatter-in-vscode-3lo0

Auto activate venv https://stackoverflow.com/questions/58433333/auto-activate-virtual-environment-in-visual-studio-code

CTRL+SHIFT+0 to show objects
then:   ":" to display by types
"""
from datetime import datetime
import json
import pandas as pd
import numpy as np
from pandas import DataFrame
from analysis.brier_score import calc_brier
from analysis.out_periods_elo import analyse_out_periods_predictions
from elo.elorating import PlayerElo, PlayersElo
from analysis.analysis import analyse_predictions, compare_predictions_accuracy
from typing import Tuple
from elo.elodataframe import apply_elo, set_last9m_court_elo_dataframe
from elo.elopeak import set_peak_elo
from elo.elodataframe import apply_mixed_elo

# LOAD DATA
def load_data(is_atp: bool, yrstart=2019, yrend=2022) -> DataFrame:
    """Load all yearly CSV files to build one dataframe

    Args:
        is_atp (bool):
        yrstart (int, optional): Defaults to 2019.
        yrend (int, optional): Defaults to 2021.

    Returns:
        DataFrame: a global dataframe aggregating all matches with 1 row per match
        Ordered by date/round ascending
        Exluding Exhibitions (except Hopman, Mubadala, juniors)
    """
    if is_atp:
        name_tour = "ATP"
    else:
        name_tour = "WTA"
    dfMatches = pd.DataFrame()
    for year in range(yrend, yrstart - 1, -1):
        dfyear = pd.read_csv(
            (
                r"https://raw.githubusercontent.com/damienld/Pro-Tennis-Analysis/main/Data/{0}{1}_all_matches.csv"
            ).format(name_tour, str(year)),
        )
        # dfyear=pd.read_csv(("./Data/ATP{0}_all_matches.csv").format(str(year)))
        dfyear.Date = pd.to_datetime(dfyear.Date, format="%d/%m/%y %H:%M:%S")
        dfMatches = pd.concat([dfMatches, dfyear], axis=0)
    # drop useless rows
    try:
        dfMatches = dfMatches.drop(
            [
                "TrnSite",
                "TrnSpeed",
                "TrnSpeedNb",
                "Round",
                "Player",
                "AceRatePlayer",
                "Srv1PtsP1",
                "Srv2PtsP1",
                "Srv1PtsWonP1",
                "Srv2PtsWonP1",
                "StatusP1",
                "StatusP2",
                "AvgAceRateP",
                "AvgAceRateOpp",
                "AvgPtsWonServ",
                "AvgPtsWonRetrnOpp",
                "IsEnoughData3",
                "IsValidData",
            ],
            axis=1,
        )
    except:
        pass
    # from 2 rows by match to only 1 row
    dfMatches = dfMatches[dfMatches["IndexP"] == 0]
    # sort by Date and Rounds to get the right order in case 2 matches played on the same day
    dfMatches = dfMatches.sort_values(by=["Date", "RoundId"], ascending=True)
    # filter Tournaments to exclude non relevant ones
    queryTrn = "( TrnRk <= 5 | Trn.str.startswith('Hopman') | Trn.str.startswith('Mubadala') | Trn.str.find('(juniors)')>0 )"
    dfMatches = dfMatches.query(queryTrn)
    return dfMatches


isatp = True


def load_playersElo(
    isatp: bool, initial_df: DataFrame, path: str = "./results/"
) -> Tuple[PlayersElo, DataFrame]:
    """Either Load from file OR Rebuild it:
    - playersElo: dictionnary of historical Elo ratings info for all players
    - df: a dataframe with all Elo info added to each match/row
    If one the files doesn't exist then both are fully rebuilt.
    Args:
        isatp (bool): [description]
        initial_df (DataFrame): Only needed if we are rebuilding the files
    Returns:
        Tuple[PlayersElo, DataFrame]: [description]
    """
    playersElo = PlayersElo.deserialize(path + "AllElos.json")
    dfWithElos = None
    try:
        dfWithElos = pd.read_csv(path + "/dfWithElos.csv", parse_dates=["Date"])
    except:
        pass
    # if one of the files is not already built
    if playersElo == None or len(dfWithElos) <= 0:
        # rebuild both files
        playersElo: PlayersElo = {}
        # create/build the matches and elo files
        dfWithElos = initial_df
        dfWithElos, playersElo = apply_elo(dfWithElos, {}, isatp)
        dfWithElos = apply_mixed_elo(dfWithElos)
        # save a dataframe with all matches and Elo rating of each player for the matches
        dfWithElos.to_csv(path + "dfWithElos.csv")
        # save the historical rating for each player
        PlayersElo.serialize(playersElo, path + "AllElos.json")
    # relaod the data fromt he saved file
    # playersElo = PlayersElo.deserialize("./results/AllElos.json")
    return playersElo, dfWithElos


def create_features(df: DataFrame):
    pass


if __name__ == "__main__":
    print("hello")
    initial_df = load_data(isatp, 2013, 2021)
    playersElo, dfWithElos = load_playersElo(isatp, initial_df)
    # show 2021 end of year ratings
    print("-----" + str(2021) + "-----")
    playersEloYr = PlayersElo.filterplayersratings_byyear(0, playersElo, 2021)
    PlayersElo.get_latest_ranking_year(playersEloYr)
    print("-----" + str(2021) + " CLAY -----")
    # PlayersElo.get_latest_ranking_year(playersEloYr, 1)

    # dont keep year 1 as it served to make elo stable rankings
    dfWithElos = dfWithElos[dfWithElos["Date"] > datetime(2013, 12, 10)]

    # Only Completed matches
    dfWithElos = dfWithElos[dfWithElos["IsCompleted"]]
    dfWithElos9M = dfWithElos

    # Set/Load ELO9M
    try:
        dfWithElos9M = pd.read_csv("./results/dfWithElos9m.csv", parse_dates=["Date"])
    except:
        # dont predict/test at lower levels ( ATP level only) andR1+
        dfWithElosATPmain = dfWithElos[
            (dfWithElos["TrnRk"] >= 2)
            & (dfWithElos["TrnRk"] <= 5)
            & (dfWithElos["RoundId"] >= 4)
        ]
        df_toupdate_9m = dfWithElosATPmain.copy().loc[
            dfWithElosATPmain["Date"] > datetime(2014, 12, 20)
        ]
        dfWithElos9M = set_last9m_court_elo_dataframe(
            df_toupdate_9m, dfWithElos, playersElo
        )

    # Set/Load PEAK Elo
    try:
        dfWithElos9M_peak = pd.read_csv(
            "./results/dfWithElos9m_peak.csv", parse_dates=["Date"]
        )
    except:
        dfWithElos9M_peak = set_peak_elo(dfWithElos9M, playersElo)

    # test
    # p: PlayerElo = playersElo[14177]
    # p.get_peak_Elo(datetime(2021, 12, 4))  # 1742.8 datetime(2020,9,2)
    # p.build_elo_court_cat_lastXmonths(datetime(2021, 12, 4), dfWithElos, 9)

    dfWithElos9M_peak = dfWithElos9M_peak[
        dfWithElos9M_peak["TrnRk"].isin([2, 3, 4, 5])
    ]  # no slam
    # dfWithElos9M = dfWithElos9M[dfWithElos9M.CourtId == 1]
    compare_predictions_accuracy(dfWithElos9M_peak)
    analyse_predictions(dfWithElos9M_peak)
    analyse_out_periods_predictions(dfWithElos9M_peak)

    create_features(dfWithElos9M)
