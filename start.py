"""
1-Create a virtual environment in VS Code:
> python -m venv tennis-predict_venv  

2-Activate the venv
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> tennis-predict_venv\scripts\activate
3 - Select your new environment from the Palette:Python: Select Interpreter (might need to refresh)
4 - Install the packages
python -m pip install matplotlib
5 - pip freeze > requirements.txt

Set up Black auto-formatting: https://dev.to/adamlombard/how-to-use-the-black-python-code-formatter-in-vscode-3lo0
"""
import pandas as pd
import numpy as np

# LOAD DATA
def get_data(is_atp: bool, yrstart=2013, yrend=2021):
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
    # sort by Date and Round to get the right order in case 2 matches played on the same day
    dfMatches = dfMatches.sort_values(by=["Date", "RoundId"], ascending=False)
    return dfMatches


get_data(True, 2021, 2021)
