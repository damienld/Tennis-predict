import out_periods_elo
import pandas as pd
from datetime import datetime
from brier_score import calc_brier


class Test_Analyse_out_periods_predictions:
    def test_analyse_out_periods_predictions_1(self):
        dfWithElos = pd.read_csv("./results/dfWithElos.csv", parse_dates=["Date"])
        # dont keep year 1 as it served to make elo stable rankings
        dfWithElos = dfWithElos[dfWithElos["Date"] > datetime(2013, 12, 10)]
        # dont predict/test at lower levels ( ATP level only)
        dfWithElos = dfWithElos[(dfWithElos["TrnRk"] >= 2) & (dfWithElos["TrnRk"] <= 5)]
        dfWithElos = calc_brier(dfWithElos, "IndexP", "ProbaElo")
        dfWithElos["Proba_odds"] = 1 / dfWithElos["Odds1"]
        dfWithElos = calc_brier(dfWithElos, "IndexP", "Proba_odds", "brier_odds")

        out_periods_elo.analyse_out_periods_predictions(dfWithElos)
