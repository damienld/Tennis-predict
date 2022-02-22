from tt_init import translate_tipstop_data
from typing import Tuple
from pandas import DataFrame
import pandas as pd
from elo.elodataframe import (
    apply_elo,
    apply_mixed_elo,
    apply_mixed_elo2,
    set_last9m_court_elo_dataframe,
)
from elo.elorating import PlayerElo, PlayersElo
import sys
from main import load_playersElo

if __name__ == "__main__":
    path = "../tipstop_elo/"
    filename = sys.argv[1]  # "tennis_predict.csv"
    isatp = True
    # load existing df and playerElo
    playersElo, dfWithElos = load_playersElo(isatp, None, path)
    df_to_predict: DataFrame = translate_tipstop_data(isatp, filename)
    # load df with updates after translating it
    df_to_predict["IsCompleted"] = False
    df_to_predict["SetsP1"] = "0"
    df_to_predict["SetsP2"] = "0"
    df_to_predict, playersElo = apply_elo(df_to_predict, playersElo, isatp)
    df_to_predict["ProbaElo"] = round(
        PlayerElo.get_match_proba(df_to_predict["Elo2"], df_to_predict["Elo1"], 2), 3
    )
    df_to_predict["ProbaEloCourt"] = round(
        PlayerElo.get_match_proba(
            df_to_predict["Elo2Court"], df_to_predict["Elo1Court"], 2
        ),
        3,
    )

    df_to_predict = apply_mixed_elo(df_to_predict)
    df_to_predict = set_last9m_court_elo_dataframe(
        df_to_predict, dfWithElos, playersElo, "../tipstop_elo/"
    )
    df_to_predict = apply_mixed_elo2(df_to_predict)
    # dont save PlayersElo it is just used for predictions
    df_to_predict = df_to_predict[["eventid", "ProbaEloMix2"]]
    df_to_predict["Proba2"] = df_to_predict.apply(
        lambda row: (1 - row["ProbaEloMix2"]) if row["ProbaEloMix2"] > 0 else -1, axis=1
    )
    df_to_predict.rename(columns={"ProbaEloMix2": "Proba1"}, inplace=True)
    df_to_predict.to_csv(path + "out-" + filename)
