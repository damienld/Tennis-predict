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
from datetime import date, datetime
from os import stat
import json
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
from Analysis.brier_score import calc_brier
from ELO.elorating import PlayerElo, PlayersElo

# LOAD DATA
def get_data(is_atp: bool, yrstart=2013, yrend=2021) -> DataFrame:
    """
    @param is_atp: True/False
    @param yrstart
    @param yrend
    Returns a DataFrame with all matches ordered by date and round
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
    # from 2 rows by match to only 1 row
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
    dfMatches = dfMatches[dfMatches["IndexP"] == 0]
    # sort by Date and Round to get the right order in case 2 matches played on the same day
    dfMatches = dfMatches.sort_values(by=["Date", "RoundId"], ascending=True)
    # filter Tournaments
    queryTrn = "( TrnRk <= 5 | Trn.str.startswith('Hopman') | Trn.str.startswith('Mubadala') | Trn.str.find('(juniors)')>0 )"
    dfMatches = dfMatches.query(queryTrn)
    return dfMatches


playersElo: PlayersElo
playersElo = PlayersElo.deserialize("./results/AllElo.json")
if playersElo == None:
    isatp = True
    df = get_data(True, 2013, 2021)
    playersElo = {}

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
                row.name,
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
                row["Date"],
                row["IsCompleted"],
                isatp,
                True,
            ),
            axis=1,
        )
    )
    df = calc_brier(df, "IndexP", "ProbaElo")
    df = calc_brier(df, "IndexP", "ProbaElo")
    df.to_csv("./results/dfWithElos.csv")
    PlayersElo.serialize(playersElo, "./results/AllElo.json")


dfWithElos = pd.read_csv("./results/dfWithElos.csv", parse_dates=["Date"])
dfWithElos["Proba_odds"] = 1 / dfWithElos["Odds1"]
dfWithElos = calc_brier(dfWithElos, "IndexP", "Proba_odds", "brier_odds")
dfWithElos = dfWithElos[dfWithElos["IsCompleted"] == True]
# PlayersElo.get_ranking(playersElo)

print("-----" + str(2014) + "-----")
# playersEloYr = PlayersElo.filterplayersratings_byyear(playersElo, 2014)
# PlayersElo.get_ranking(playersEloYr)

# dont keep year 1 as it served to get elo stable rankings
dfWithElos = dfWithElos[dfWithElos["Date"] > datetime(2013, 12, 10)]
print("Brier score for Elo " + str(dfWithElos["brier"].mean()))
print("Brier score for Odds " + str(dfWithElos["brier_odds"].mean()))

# keep only out periods
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
