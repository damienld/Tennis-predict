from pandas import DataFrame
from analysis.brier_score import calc_brier
from analysis.roi import calc_roi
import plotly.express as px


def compare_predictions_accuracy(df: DataFrame):
    # the dataframe always have the winner as the first player
    # classical ATP ranking
    df_atp = df[(df["Rk1"] > 0) & (df["Rk2"] > 0)]
    atp_exact = len(df_atp[df_atp["Rk1"] <= df_atp["Rk2"]])
    atp = 100 * atp_exact / len(df_atp)
    # Elo ranking
    df_elo = df[(df["nbElo1"] >= 50) & (df["nbElo2"] >= 50)]
    elo_exact = len(df_elo[df_elo["Elo1"] >= df_elo["Elo2"]])
    elo = 100 * elo_exact / len(df_elo)
    # Bookmakers Odds
    # Check margin is between 0.98 and 1.1
    df_book = df[
        (df["Odds1"] > 1)
        & (df["Odds2"] >= 1)
        & (1.1 > 1 / df["Odds1"] + 1 / df["Odds2"])
        & (df["Odds1"] + 1 / df["Odds2"] > 0.98)
    ]
    book_exact = len(df_book[df_book["Odds1"] <= df_book["Odds2"]])
    book = 100 * book_exact / len(df_book)
    # Our prediction
    # our = 100 * conf.win0.sum() / len(conf)
    # Plot
    labels = ["Best ATP ranking", "Best Elo ranking", "Best Odds"]
    values = [atp, elo, book]
    xaxis_label = "% of matches correctly predicted"
    title = (
        "Prediction of all ATP main draw matches since 2014 <br> ("
        + str(len(df))
        + " matches)"
    )

    fig = px.bar(
        x=labels,
        y=values,
        color=labels,
        title=title,
        width=500,
        height=600,
        labels={"x": "Prediction Method", "y": "Accuracy (%)"},
    )
    fig.update_yaxes(range=[60, 75])
    # fig.show()


def analyse_predictions(df: DataFrame):
    df = calc_brier(df, "IndexP", "ProbaElo")
    df["Proba_odds"] = 1 / df["Odds1"]
    df = calc_brier(df, "IndexP", "Proba_odds", "brier_odds")
    # need X sets in player histo ratings to trust Elo rating, update proba to -1 for those rows
    df.loc[(df["nbElo1"] >= 50) & (df["nbElo2"] >= 50), "ProbaElo"] = -1
    df = calc_roi(df, "Odds1", "Odds2", "IndexP", "ProbaElo")

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
    df.to_csv("./results/predictions.csv")
