from pandas import DataFrame
from brier_score import calc_brier
from roi import calc_roi


def analyse_predictions(df: DataFrame):
    df = calc_brier(df, "IndexP", "ProbaElo")
    df["Proba_odds"] = 1 / df["Odds1"]
    df = calc_brier(df, "IndexP", "Proba_odds", "brier_odds")
    df = calc_roi(df, "Odds1", "Odds2", "IndexP", "ProbaElo")
    df.to_csv("./results/predictions.csv")

    print("Brier score for Elo " + str(df["brier"].mean()))
    # 0.2053(set, adj_out) 0.(set, NO adj_out)
    print("Brier score for Odds " + str(df["brier_odds"].mean()))
    # 0.1885
    sumROI_stake = df["stake_roi1"].sum()
    sumROI_profit = df["pnl_roi1"].sum()
    roi = 100 * round(sumROI_profit / sumROI_stake, 3)
    print(
        "Roi(Kelly) for Elo: stake={} Profit={} => ROI={} %".format(
            str(sumROI_stake), str(sumROI_profit), str(roi)
        ),
    )
