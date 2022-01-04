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

# LOAD DATA
def get_data(is_atp: bool, yrstart=2019, yrend=2021) -> DataFrame:
    """
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
    # from 2 rows by match to only 1 row
    dfMatches = dfMatches[dfMatches["IndexP"] == 0]
    # sort by Date and Rounds to get the right order in case 2 matches played on the same day
    dfMatches = dfMatches.sort_values(by=["Date", "RoundId"], ascending=True)
    # filter Tournaments to exclude non relevant ones
    queryTrn = "( TrnRk <= 5 | Trn.str.startswith('Hopman') | Trn.str.startswith('Mubadala') | Trn.str.find('(juniors)')>0 )"
    dfMatches = dfMatches.query(queryTrn)
    return dfMatches


playersElo = PlayersElo.deserialize("./results/AllElo.json")
if playersElo == None:
    playersElo: PlayersElo = {}
    # create/build the matches and elo files
    isatp = True
    df = get_data(isatp, 2013, 2021)

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
    # save a dataframe with all matches and Elo rating of each player for the matches
    df.to_csv("./results/dfWithElos.csv")
    # save the historical rating for each player
    PlayersElo.serialize(playersElo, "./results/AllElo.json")


dfWithElos = pd.read_csv("./results/dfWithElos.csv", parse_dates=["Date"])
# show 2021 end of year ratings
print("-----" + str(2021) + "-----")
playersEloYr = PlayersElo.filterplayersratings_byyear(playersElo, 2021)
# PlayersElo.get_latest_ranking_year(playersEloYr)

# dont keep year 1 as it served to make elo stable rankings
dfWithElos = dfWithElos[dfWithElos["Date"] > datetime(2013, 12, 10)]

# Only Completed matches
dfWithElos = dfWithElos[dfWithElos["IsCompleted"]]

# dont predict/test at lower levels ( ATP level only) andR1+
dfWithElos = dfWithElos[(dfWithElos["TrnRk"] >= 2) & (dfWithElos["TrnRk"] <= 5)]

compare_predictions_accuracy(dfWithElos)
analyse_predictions(dfWithElos)
analyse_out_periods_predictions(dfWithElos)
