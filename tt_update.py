from tt_init import translate_tipstop_data
from typing import Tuple
from pandas import DataFrame
import pandas as pd
from elo.elodataframe import apply_elo, apply_mixed_elo, set_last9m_court_elo_dataframe
from elo.elorating import PlayersElo
import sys
from main import load_playersElo


def delete_duplicated(dfglobal: DataFrame, df_with_updates: DataFrame) -> DataFrame:
    # Perform a left-join, eliminating duplicates in df2 so that each row of df1 joins with exactly 1 row of df2.
    # Use the parameter indicator to return an extra column "_merge" indicating which table the row was from.
    df_all = df_with_updates.merge(
        dfglobal.drop_duplicates(),
        indicator=True,
        how="left",
        on=["eventid"],
    )
    # Create a boolean condition to keep only the rows in df1 which are not in df2
    new_eventids = df_all[df_all["_merge"] == "left_only"]["eventid"]
    # filter df_with_updates with just the eventids above
    df_with_updates = df_with_updates[(df_with_updates.eventid.isin(new_eventids))]
    print("{0} matches added".format(len(df_with_updates)))
    return df_with_updates


if __name__ == "__main__":
    path = "../tipstop_elo/"
    filename = sys.argv[1]  # "tennis_update.csv"
    isatp = True
    # load existing df and playerElo
    playersElo, dfWithElos = load_playersElo(isatp, None, path)
    # load df with updates after translating it
    df_with_updates = translate_tipstop_data(isatp, filename)
    # delete duplicated rows between both
    df_with_updates = delete_duplicated(dfWithElos, df_with_updates)
    # process Elo infos on the non duplicated rows from the update
    df_with_updates, playersElo = apply_elo(df_with_updates, playersElo, isatp)
    df_with_updates = apply_mixed_elo(df_with_updates)
    dfWithElos = pd.concat([dfWithElos, df_with_updates], axis=0)
    dfWithElos = dfWithElos.drop(["Unnamed: 0"], axis=1)
    # df_with_updates = set_last9m_court_elo_dataframe(
    #    df_with_updates, dfWithElos, playersElo, "../tipstop_elo/"
    # )
    dfWithElos.to_csv(path + "dfWithElos.csv")
    # save the historical rating for each player
    PlayersElo.serialize(playersElo, path + "AllElos.json")
