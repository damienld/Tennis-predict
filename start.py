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
"""
from datetime import date
from os import stat
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame

from elorating import *

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
            parse_dates=["Date"],
        )
        # dfyear=pd.read_csv(("./Data/ATP{0}_all_matches.csv").format(str(year)), parse_dates = ['Date'])
        dfMatches = pd.concat([dfMatches, dfyear], axis=0)
    # from 2 rows by match to only 1 row
    dfMatches = dfMatches[dfMatches["IndexP"] == 0]
    # sort by Date and Round to get the right order in case 2 matches played on the same day
    dfMatches = dfMatches.sort_values(by=["Date", "RoundId"], ascending=True)
    return dfMatches


isatp = True
df = get_data(True, 2013, 2021)
playersElo = {}

(
    df["Elo1"],
    df["nbElo1"],
    df["EloAfter1"],
    df["Elo2"],
    df["nbElo2"],
    df["EloAfter2"],
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
df.to_csv("a.csv")
PlayerElo.get_ranking(playersElo)
