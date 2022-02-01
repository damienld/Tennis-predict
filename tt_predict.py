from tt_init import translate_tipstop_data
from typing import Tuple
from pandas import DataFrame
import pandas as pd
from elo.elodataframe import apply_elo, apply_mixed_elo, set_last9m_court_elo_dataframe
from elo.elorating import PlayersElo
import sys
from main import load_playersElo

if __name__ == "__main__":
    path = "../tipstop_elo/"
    filename = "tennis_update.csv"
    isatp = True
    # load existing df and playerElo
    playersElo, dfWithElos = load_playersElo(isatp, None, path)
    # load df with updates after translating it
