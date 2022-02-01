from typing import Tuple
from pandas import DataFrame
import pandas as pd
from elo.elodataframe import set_last9m_court_elo_dataframe
from elo.elorating import PlayersElo

from main import load_playersElo

"""Used to map the tipstop csv data to the needed fields for building ELO
"""
def trasnlate_trnrk(trn_tiptop: str)->int:
    match trn_tiptop:
        case "ATP":
            return 2
        case "Challenger":
            return 1
        case "Exhibition":
            return 6
        case "Grand Slam":
            return 4
    return 2

def translate_round(round_tiptop: str, trn_name: str, start_round: str, end_round: str) -> int:
    is_qualif: bool = trn_name.lower().__contains__(", qualif")
    if str(round_tiptop)=="nan" or str(start_round)=="nan" or start_round.lower()=="null":
        return 4
    
    mapping_roundsid_text: dict={"null":0,"fina":8, "semi":7, "quar":6, "1/8":5
    , "1/7":5, "1/6":5, "1/16":4, "1/12":4, "1/14":4, "1/24":3,"1/28":3, "1/32":3, "1/48":2, "1/64":2, "1/96":1, "1/128":1}
    start_round_id=mapping_roundsid_text[start_round.lower()[:4]]
    #end_round_id=mapping_roundsid_text[end_round.lower()][:4]
    # F=8, SF=7; QF=6, 1/8=5, 1/16=4, 1/32=3,1/64=2, 1/128=1
    roundid_tiptop: int = int(str(round_tiptop)[:1])
    # O preq, 1-2-3 Qualies, 8 RR, 4=1st, 10=1/2, 11 bronze, 12 final
    if is_qualif:
        return roundid_tiptop-start_round_id+1
    elif round_tiptop == 8: #Final
        return 12
    elif roundid_tiptop == 7:  # 1/2
        return 10
    elif roundid_tiptop == 6:  # 1/4
        return 9
    elif roundid_tiptop == 5:  # 1/8
        return 8
    else:
        return roundid_tiptop - start_round_id +4

def translate_surface(surface: str, inoutdoor: str) -> Tuple[str, int]:
    """From the couple (surface, inoutdoor)  returns the actual surface among hard, indoor, clay, grass, carpet
    with an id
    Args:
        surface (str): [description]
        inoutdoor (str): [description]

    Returns:
        str: [description]
    """
    if str(surface) == "nan":
        return 1#"hard", 1
    if surface.lower() == "hard":
        if inoutdoor.lower() == "indoor":
            return 3#"indoor", 3
        else:
            return 1#"hard", 1
    elif surface.lower() == "clay":
        return 2#"clay", 2
    elif surface.lower() == "carpet":
        return 4#"carpet", 4
    elif surface.lower() == "grass":
        return 5#"grass", 5
    else:
        return 1#"hard", 1

def translate_tipstop_data(is_atp: bool, filename: str) -> DataFrame:
    if is_atp:
        gender = "male"
    else:
        gender = "female"
    dfMatches: DataFrame = pd.read_csv(
        "../tipstop_elo/{0}".format(filename), sep=";", parse_dates=["date", "datetime"]
    )
    query_gender = "( gender == '{0}' )".format(gender)
    dfMatches = dfMatches.query(query_gender)
    print(len(dfMatches))
    dfMatches["isDoubles"]=dfMatches['event'].str.contains("/")
    dfMatches=dfMatches[dfMatches["isDoubles"]==False]
    print(len(dfMatches))
    # dfyear=pd.read_csv(("./Data/ATP{0}_all_matches.csv").format(str(year)))
    # dfMatches["date"] = pd.to_datetime(dfMatches["date"], format="%yyyy-%m-%d")
    # drop useless rows
    dfMatches = dfMatches[
        [
            "eventid",
            "event",
            "date",
            "id_participant",
            "name",
            "position",
            "setswon",
            "is_win",
            "surface",  # Hard Unknown Clay Grass Carpet
            "inoutdoor",  # Indoor Outdoor
            "round",
            "tournament_name",
            "typetournament",
            "wo-Retired",
            "start_round", "end_round"
        ]
    ]
    print(len(dfMatches))
    # from 2 rows by match to only 1 row
    dfMatches1 = dfMatches[dfMatches["position"] == 1]
    print(len(dfMatches1))
    dfMatches2 = dfMatches[dfMatches["position"] == 2]
    print(len(dfMatches2))
    dfMatches = pd.merge(dfMatches1, dfMatches2, on="eventid", how="inner")
    print(len(dfMatches))
    # sort by Date and Rounds to get the right order in case 2 matches played on the same day
    dfMatches = dfMatches.sort_values(by=["date_x", "round_x"], ascending=True)
    # filter Tournaments to exclude non relevant ones
    # queryTrn = "( TrnRk <= 5 | Trn.str.startswith('Hopman') | Trn.str.startswith('Mubadala') | Trn.str.find('(juniors)')>0 )"
    # dfMatches = dfMatches.query(queryTrn)
    # SURFACES
    dfMatches["CourtId"] = dfMatches.apply(
        lambda row: translate_surface(row["surface_x"], row["inoutdoor_x"]), axis=1
    )
    # ROUND
    dfMatches["RoundId"] = dfMatches.apply(lambda row: translate_round(row["round_x"]
    ,row["tournament_name_x"],row["start_round_x"], row["end_round_x"]),
            axis=1,)
    # TRN
    dfMatches["TrnRk"] = dfMatches.apply(lambda row: trasnlate_trnrk(row["typetournament_x"]),
            axis=1,)
    #ISCompleted
    dfMatches["IsCompleted"] = dfMatches.apply(lambda row: row["wo-Retired_x"]=="None", axis=1)
    dfMatches=dfMatches.rename(
        columns={
            "id_participant_x": "P1Id",
            "id_participant_y": "P2Id",
            "name_x": "P1",
            "name_y": "P2",
            "date_x": "Date",
            "setswon_x": "SetsP1",
            "setswon_y": "SetsP2",
        }
    )
    dfMatches = dfMatches[
        ["eventid", "Date", "CourtId", "P1Id", "P2Id", "P1", "P2", "TrnRk", "RoundId","SetsP1","SetsP2","IsCompleted"]
    ]
    dfMatches.to_csv("../tipstop_elo/{0}.csv".format(gender))
    return dfMatches


if __name__ == "__main__":
    path="../tipstop_elo/"
    isatp=True
    initial_df=translate_tipstop_data(isatp, "tennis.csv")
    playersElo, dfWithElos = load_playersElo(isatp, initial_df,path)
    #df = set_last9m_court_elo_dataframe(
    #        initial_df, dfWithElos, playersElo,"../tipstop_elo/"
    #    )
    