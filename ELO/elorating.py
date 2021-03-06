"""
"""
from datetime import datetime, timedelta
import json
from typing import Tuple
from pandas import DataFrame
from tennis.tennis_common import calc_datediff_withoutoffseason
from collections import namedtuple
import numpy as np

from tennis.tennis_probas import get_match_proba_bo5

# from dataclasses import dataclass, field

MatchDetails = namedtuple(
    "MatchDetails",
    [
        "trn_rk",
        "round",  # 1
        "is_completed",
        "opp_id",  # 3
        "sets1",
        "sets2",  # 5
        "opp_elo",
        "opp_elo_nb",  # 7
        "opp_elo_c",
        "opp_elo_nb_c",
    ],
)


class PlayerElo:
    """
    A class to represent a player in the Elo Rating System
    """

    coeff_KCoeff_opp = 100  # try values from 1 to 100 (see Kcoeff calculation)
    elo_initialrating = 1500
    min_day_outperiod = 55
    isAtp = True

    def __init__(self, name: str, id: str):  # , rank: int):
        self.id = id
        self.name = name
        # comment the 2 lines below in order to start with a rating associated to current player rank
        initalrating = PlayerElo.elo_initialrating
        # if rank > 0:
        #    initalrating = PlayerElo.get_elo_value_from_rank(rank, PlayerElo.isAtp)
        self.eloratings_clay = {-1: initalrating}
        self.elomatches_clay = {-1: 0}
        self.eloratings_nonclay = {-1: initalrating}
        self.elomatches_nonclay = {-1: 0}
        self.eloratings = {-1: initalrating}
        self.elomatches = {-1: 0}
        # self.elomatchdetails = {-1: None}

    def __repr__(self):
        rating = self.get_latest_rating(0)
        return ("{} {} {} ({})").format(self.name, self.id, rating[0], rating[1])

    @staticmethod
    def get_elo_from_mixed(
        elo: float, elo_court_cat: float, nb_elo_court_cat: int
    ) -> Tuple[float, int]:
        """Mix Elo rating and Elo rating on court_cat
        Args:
            elo (float): [description]
            elo_court_cat (float): [description]
            nb_elo_court_cat (int): [description]

        Returns: Tuple
            - float: Mixed ELO if enough match on court_cat (else just overall Elo)
            - int: Number of matches/sets taken into account on court_cat
        """
        if nb_elo_court_cat >= PlayerElo.coeff_KCoeff_opp / 2:
            avg_elo = (elo + elo_court_cat) / 2
            avg_nb = nb_elo_court_cat
        else:
            avg_elo = elo
            avg_nb = nb_elo_court_cat
        return avg_elo, avg_nb

    @staticmethod
    def get_elo_from_mixed2(
        elo: float,
        elo_court_cat: float,
        nb_elo_court_cat: int,
        elo_court9M: float,
        nb_elo_court9M: int,
    ) -> Tuple[float, int]:
        """Mix Elo rating, Elo rating on court_cat and Elo9M
        Args:
            elo (float): [description]
            elo_court_cat (float): [description]
            nb_elo_court_cat (int): [description]

        Returns: Tuple
            - float: Mixed ELO if enough match on court_cat (else just overall Elo)
            - int: Number of matches/sets taken into account on court_cat
        """
        if nb_elo_court_cat >= PlayerElo.coeff_KCoeff_opp / 2:
            if nb_elo_court9M < 20:
                avg_elo = (elo + elo_court_cat) / 2
                avg_nb = nb_elo_court_cat
            else:
                avg_elo = (elo + elo_court_cat + elo_court9M) / 3
                avg_nb = nb_elo_court9M
        else:
            avg_elo = elo
            avg_nb = nb_elo_court_cat
        return avg_elo, avg_nb

    def build_elo_court_cat_lastXmonths(
        self, dateend: datetime, df_to_look_for_results: DataFrame, months: int = 9
    ) -> Tuple[int, int, int]:
        # get date - 9M in date_elo format YYYYMMDDn
        date_start = dateend + timedelta(days=round(-months * 30.5))
        # filter df to get the matches
        df_to_look_for_results = df_to_look_for_results.loc[
            (df_to_look_for_results["Date"] >= date_start.strftime("%Y-%m-%d"))
            & (df_to_look_for_results["Date"] < dateend.strftime("%Y-%m-%d"))
            & (
                (df_to_look_for_results["P1Id"] == self.id)
                | (df_to_look_for_results["P2Id"] == self.id)
            )
            # & ((df["P1Id"] == str(self.id)) | (df["P2Id"] == str(self.id)))
        ]
        # filter dict self.eloratings_<court_cat> where ( date_elo >= (date - 9M) )
        """dict_elo_ratings_court_cat = self.__get_ratings_dict(idcourt_cat)
        dates_ratings_court_cat = dict_elo_ratings_court_cat.keys()
        dates_ratings_court_cat = [
            int(date)
            for date in dates_ratings_court_cat
            if (int(date) >= date_start_int)
        ]
        dates_ratings_court_cat = [
            int(date) for date in dates_ratings_court_cat if (int(date) < date_end_int)
        ]"""
        # init starting ELO
        nb_last9m = 0
        if len(df_to_look_for_results) > 0:
            indexplayer: str = "1"
            if df_to_look_for_results.iloc[0]["P2Id"] == self.id:
                indexplayer = "2"
            elo_last9m = df_to_look_for_results.iloc[0]["Elo" + indexplayer]
        else:
            elo_last9m = 1500
        # loop each match for last 9M
        print(self.name + "-9M start:" + str(elo_last9m))
        for idx, row in df_to_look_for_results.iterrows():
            indexopp = "1"
            indexp = "2"
            if row["P1Id"] == self.id:
                indexopp = "2"
                indexp = "1"
            # match_details: MatchDetails = self.elomatchdetails[str(date_match)]
            match_details = MatchDetails(
                row["TrnRk"],
                row["RoundId"],
                row["IsCompleted"],
                row["P" + indexopp + "Id"],
                row["SetsP" + indexp],
                row["SetsP" + indexopp],
                row["Elo" + indexopp],
                row["nbElo" + indexopp],
                row["Elo" + indexopp + "Court"],
                row["nbElo" + indexopp + "Court"],
            )
            if match_details.is_completed:
                nb_last9m += match_details.sets1 + match_details.sets2
                elo_opp, elo_nb_opp = PlayerElo.get_elo_from_mixed(
                    match_details.opp_elo,
                    match_details.opp_elo_c,
                    match_details.opp_elo_nb_c,
                )
                elo_last9m = self.get_new_elo_ratings_setbyset(
                    elo_last9m,
                    elo_opp,
                    nb_last9m,
                    elo_nb_opp,
                    match_details.sets1,
                    match_details.sets2,
                    match_details.trn_rk,
                    match_details.round,
                )[0]
                print(
                    "{}-{} v {} {}({})=>{}".format(
                        (match_details.sets1),
                        match_details.sets2,
                        row["P" + indexopp],
                        elo_opp,
                        elo_nb_opp,
                        elo_last9m,
                    )
                )
        return (elo_last9m, nb_last9m)

    def get_lastXdays_elo_gain(
        self, dateend: datetime, df_to_look_for_results: DataFrame, days: int
    ) -> Tuple[int, int, int]:
        # get date - 9M in date_elo format YYYYMMDDn
        date_start = dateend + timedelta(days=-days)
        # filter df to get the matches
        df_to_look_for_results = df_to_look_for_results.loc[
            (df_to_look_for_results["Date"] >= date_start.strftime("%Y-%m-%d"))
            & (df_to_look_for_results["Date"] < dateend.strftime("%Y-%m-%d"))
            & (
                (df_to_look_for_results["P1Id"] == self.id)
                | (df_to_look_for_results["P2Id"] == self.id)
            )
            # & ((df["P1Id"] == str(self.id)) | (df["P2Id"] == str(self.id)))
        ]
        print(
            self.name
            + "-{}d start: ".format(str(days))
            + date_start.strftime("%Y-%m-%d")
        )
        score = 0
        # loop each match for last 30 days
        for idx, row in df_to_look_for_results.iterrows():
            indexopp = "1"
            indexp = "2"
            if row["P1Id"] == self.id:
                indexopp = "2"
                indexp = "1"

            is_retirement = "ret." in row["Result"] or "w/o" in row["Result"]
            """if match_details.is_completed:
                nb_last9m += match_details.sets1 + match_details.sets2
                elo_opp, elo_nb_opp = PlayerElo.get_elo_from_mixed(
                    match_details.opp_elo,
                    match_details.opp_elo_c,
                    match_details.opp_elo_nb_c,
                )
                elo_last9m = self.get_new_elo_ratings_setbyset(
                    elo_last9m,
                    elo_opp,
                    nb_last9m,
                    elo_nb_opp,
                    match_details.sets1,
                    match_details.sets2,
                    match_details.trn_rk,
                    match_details.round,
                )[0]
                print(
                    "{}-{} v {} {}({})=>{}".format(
                        (match_details.sets1),
                        match_details.sets2,
                        row["P" + indexopp],
                        elo_opp,
                        elo_nb_opp,
                        elo_last9m,
                    )
                )"""
        return (0, 0, 0)

    def __get_ratings_dict(self, idcourt_cat: int) -> dict:
        if idcourt_cat == 0:
            return self.eloratings
        elif idcourt_cat == 1:
            return self.eloratings_clay
        elif idcourt_cat == 2:
            return self.eloratings_nonclay
        else:
            raise Exception("incorrect value for idcourt_cat")

    def __get_matches_dict(self, idcourt_cat: int) -> dict:
        if idcourt_cat == 0:
            return self.elomatches
        elif idcourt_cat == 1:
            return self.elomatches_clay
        elif idcourt_cat == 2:
            return self.elomatches_nonclay
        else:
            raise Exception("incorrect value for idcourt_cat")

    def get_peak_Elo(self, dateend: datetime) -> Tuple[int, datetime]:
        """
            Get the peak Elo and the number of days since that

        Args:
            playerid (int): player to look for
            dateend (datetime): Date of the match, don't look for peak elo after that
            df (DataFrame): Full dataframe to look for previous elo and determine the peak

        Returns:
            Tuple[int, datetime]:
            - value peak elo
            - date peak elo
        """
        dateend_int = PlayersElo.get_date_eloformat(dateend)
        filt_Dict = {
            key: value
            for (key, value) in self.eloratings.items()
            if int(key) < dateend_int
        }
        maxi = max(filt_Dict, key=filt_Dict.get)
        return self.eloratings[maxi], PlayersElo.get_datetime(int(maxi))

    def add_rating(
        self,
        idcourt_cat: int,
        newrating: int,
        date: datetime,
        nr_matches_to_set: int,
    ) -> None:
        """Add the updated ELO rating to eloratings. And the total number of matches.
        Also add the matchdetails which are used for example when recalculating lastXmonths elo

        Args:
            idcourt_cat (int): [description]
            newrating (int): Updated elo rating after the new match
            date (datetime): Date of the match
            nr_matches_to_set (int): Set the new total number of matches! (no addition)
            matchdetails (MatchDetails): used for example when recalculating lastXmonths elo. Can be set to None if no need.
        """
        ref_to_rating: dict = self.__get_ratings_dict(idcourt_cat)
        ref_to_matches: dict = self.__get_matches_dict(idcourt_cat)
        # the key will be the date of the day + the match index for the day: 0
        day = "{0}{1}{2}{3}".format(
            date.year, "%02d" % date.month, "%02d" % date.day, 0
        )
        if ref_to_matches.get(day, None) != None:
            day = "{0}{1}{2}{3}".format(
                date.year, "%02d" % date.month, "%02d" % date.day, 1
            )
            # if a match has always been added for this day change the end of key to 2
            if ref_to_matches.get(day, None) == None:
                day = "{0}{1}{2}{3}".format(
                    date.year, "%02d" % date.month, "%02d" % date.day, 2
                )
                if ref_to_matches.get(day, None) == None:
                    day = "{0}{1}{2}{3}".format(
                        date.year, "%02d" % date.month, "%02d" % date.day, 3
                    )
        day = int(day)
        ref_to_rating[day] = newrating
        ref_to_matches[day] = nr_matches_to_set
        # if matchdetails != None:
        #    self.elomatchdetails[day] = matchdetails

    def get_latest_rating(self, idcourt_cat: int) -> Tuple[int, int, int]:
        """Returns the rating information (Elo rating, # matches, date) from the last match played

        Args:
            idcourt_cat(int): id court category (0=all, 1=clay, 2=non clay)
        Returns:
            Tuple:
            - int: value of latest Elo rating
            - int: nb matches for the calculation of this latest rating
            - int: (-1 if no previous elo) date with format(YYYYMMDDn) where n is the match index of that day (often 0)
        """
        ref_to_rating: dict = self.__get_ratings_dict(idcourt_cat)
        ref_to_matches: dict = self.__get_matches_dict(idcourt_cat)
        # to filter before a date:
        # filtered_dict = {k: v for (k, v) in ref_to_rating.items() if k < date}
        if len(ref_to_rating) <= 0:
            return self.elo_initialrating, 0, -1
        else:
            max_date = max(ref_to_rating.keys(), key=int)
            return (
                round(ref_to_rating[max_date], 1),
                ref_to_matches[max_date],
                max_date,
            )

    ################################## STATIC ###########################################
    @staticmethod
    def get_adjustment_elo_when_player_was_out(nr_days_out: int) -> float:
        """Returns an adjustment value to add up to the current Elo rating of the player
        For example if he was out 55 days his ELO rating will be decreased by 100

        Args:
            nr_days_out (int): The number of days since last match

        Returns:
            float: the elo adjustment matching the number of days out. Min -150.
        """
        if nr_days_out >= PlayerElo.min_day_outperiod:
            val = 10 * nr_days_out / 39 + 3350 / 39
            return max(-150, -val)
        else:
            return 0

    @staticmethod
    def get_idcourt_cat_from_idcourt(idcourt: int) -> int:
        """Returns the idcourt category from the id court
        Args:
            idcourt (int): 1 to 5 (hard, clay, ..)
        Raises:
            Exception: idcourt invalid
        Returns:
            (int): 0 (all courts), 1 (clay), 2 (all non clay)
        """
        if idcourt == 2:  # clay
            return 1
        elif idcourt in [1, 3, 4, 5]:
            return 2
        else:
            raise Exception("idcourt is not valid (must be int in [1:5])")

    @staticmethod
    def get_nr_days_since_last_rating(
        date_match, isadj_for_out_period, elo1, date_last_elo1
    ):
        if int(date_last_elo1) >= 0:
            date_last_elo1 = PlayersElo.get_datetime(date_last_elo1)
            if elo1 > 1600 and isadj_for_out_period:
                # only check out periods for players in top 100
                # because others might have gone to lower level rather than
                # really being out
                days_since_last_elo1 = calc_datediff_withoutoffseason(
                    date_match, date_last_elo1
                )
                eloadj1 = PlayerElo.get_adjustment_elo_when_player_was_out(
                    days_since_last_elo1
                )
                elo1 = elo1 + eloadj1
            else:
                days_since_last_elo1 = max(0, (date_match - date_last_elo1).days)
        else:
            days_since_last_elo1 = -1
        return elo1, days_since_last_elo1

    @staticmethod
    def __get_new_elo_ratings(
        rating1: float,
        rating2: float,
        aKcoeff1: float,
        aKcoeff2: float,
        is_player1won: bool,
        nbsetstowinformatch: int,
    ) -> Tuple[float, float]:
        """Private. Calculate the new Elo ratings for both players after the match.

        Args:
            rating1 (float): [description]
            rating2 (float): [description]
            aKcoeff1 (float): [description]
            aKcoeff2 (float): [description]
            is_player1won (bool): [description]
            nbsetstowinformatch (int):#sets to win for the match (3 or 5)
        Returns:
            Tuple[float, float]:
            - New rating P1
            - New rating P2
        """
        proba_match2 = PlayerElo.get_match_proba(rating1, rating2, nbsetstowinformatch)
        proba_match1 = PlayerElo.get_match_proba(rating2, rating1, nbsetstowinformatch)

        if is_player1won:
            rating1 = rating1 + aKcoeff1 * (1 - proba_match1)
            rating2 = rating2 + aKcoeff2 * (0 - proba_match2)
        else:
            rating1 = rating1 + aKcoeff1 * (0 - proba_match1)
            rating2 = rating2 + aKcoeff2 * (1 - proba_match2)
        return round(rating1, 1), round(rating2, 1)

    @staticmethod
    def get_new_elo_ratings_match(
        rating1: float,
        rating2: float,
        nbmatches1: int,
        nbmatches2: int,
        is_player1_won: bool,
        idround: int,
        trnrk: int,
        nbsetstowinformatch: int,
    ) -> Tuple[float, float]:
        """Calculate the new Elo ratings for both players after the match. Using MATCH method (not set_by_set)

        Args:
            rating1 (float): [description]
            rating2 (float): [description]
            nbmatches1 (int): [description]
            nbmatches2 (int): [description]
            is_player1_won (bool): [description]
            idround (int): [description]
            trnrk (int): [description]
            nbsetstowinformatch (int):#sets to win for the match (3 or 5)
        Returns:
            Tuple[float, float]: [description]
        """
        if rating2 < 0 or rating1 < 0:
            return rating1, rating2
        coeffKA = PlayerElo.get_Kcoeff(nbmatches1, nbmatches2, idround, trnrk)
        coeffKB = PlayerElo.get_Kcoeff(nbmatches2, nbmatches1, idround, trnrk)
        return PlayerElo.__get_new_elo_ratings(
            rating1, rating2, coeffKA, coeffKB, is_player1_won, nbsetstowinformatch
        )

    @staticmethod
    def get_new_elo_ratings_setbyset(
        rating1: float,
        rating2: float,
        nbmatches1: int,
        nbmatches2: int,
        nbsets_won1: int,
        nbsets_won2: int,
        trnrk: int,
        idround: int,
    ) -> Tuple[int, int]:
        """Calculate the new Elo ratings for both players after the match. Using set_by_set method (not MATCH)

        Args:
            rating1 (float): [description]
            rating2 (float): [description]
            nbmatches1 (int): [description]
            nbmatches2 (int): [description]
            nbsets_won1 (int): [description]
            nbsets_won2 (int): [description]
            trnrk (int): [description]
            idround (int): [description]

        Returns:
            Tuple[int, int]: [description]
        """
        # is_slam = False
        nbsets_won1 = int(nbsets_won1)
        nbsets_won2 = int(nbsets_won2)
        gainToRating1 = 0
        gainToRating2 = 0
        for i in range(1, nbsets_won1 + 1):
            newratings = PlayerElo.get_new_elo_ratings_match(
                rating1,
                rating2,
                nbmatches1,
                nbmatches2,
                True,
                trnrk,
                idround,
                max(nbsets_won1, nbsets_won2),
            )
            gainToRating1, gainToRating2 = (
                gainToRating1 + newratings[0] - rating1,
                gainToRating2 + newratings[1] - rating2,
            )

        for i in range(1, nbsets_won2 + 1):
            newratings = PlayerElo.get_new_elo_ratings_match(
                rating1,
                rating2,
                nbmatches1,
                nbmatches2,
                False,
                trnrk,
                idround,
                max(nbsets_won1, nbsets_won2),
            )
            gainToRating1, gainToRating2 = (
                gainToRating1 + newratings[0] - rating1,
                gainToRating2 + newratings[1] - rating2,
            )
        is_bestof5sets = max(nbsets_won1, nbsets_won2) >= 3
        if is_bestof5sets:
            # gains ared divided by 1.5 as there is 3 sets rather than 2 sets in BO5, and 5 rather than 3
            return round(rating1 + gainToRating1 / 1.5, 1), round(
                rating2 + gainToRating2 / 1.5, 1
            )
        else:
            return round(rating1 + gainToRating1), round(rating2 + gainToRating2, 1)

    @staticmethod
    def get_elobeforematch_orcreate(
        listplayers: dict, name: str, id: str, idcourt_cat: int
    ):  # , rank: int, isatp: bool

        """[summary]

        Args:
            listplayers (dict): [description]
            name (str): [description]
            id (str): [description]
            idcourt_cat (int): 0(all), 1 (clay) or 2 (non clay)
            rank (int): [description]
            isatp (bool): [description]

        Returns Tuple:
        - PlayerElo
        - int: value of latest Elo rating
        - int: nb matches for the calculation of this latest rating
        - int: (-1 if no previous elo)date with format(YYYYMMDDx) where X is the match id of that day (often 0)
        """
        player: PlayerElo
        player = listplayers.get(id, None)
        if player == None:
            # player not created yet
            player = PlayerElo(name=name, id=id)  # , rank=rank)
            listplayers[id] = player
        latest_rating = player.get_latest_rating(idcourt_cat)
        return (player, latest_rating[0], latest_rating[1], latest_rating[2])

    @staticmethod
    def get_Kcoeff(
        nbmatches: int, nbmatchesopp: int, roundid: int, trnrk: int
    ) -> float:
        """[summary]

        Args:
            nbmatches (int): [description]
            nbmatchesopp (int): set to 1000+ to ignore
            roundid (int): [description]
            trnrk (int): [description]

        Returns:
            float: [description]
        """
        # ToDo if (days_since_last_elo)
        aCoeffK = 1

        if trnrk < 2 or trnrk == 6:
            # Level Challenger or -
            aCoeffK = 0.6
        if roundid == 4:
            # Round 2 or -
            aCoeffK = aCoeffK * 0.85
        elif roundid == 5:
            # Round 1
            aCoeffK = aCoeffK * 0.95
        elif roundid < 4:
            # Round Q
            aCoeffK = aCoeffK * 0.7
        if trnrk == 4 and roundid >= 4:
            aCoeffK *= 1.15

        # 538 K-Factor https://www.betfair.com.au/hub/tennis-elo-modelling/
        # which is 130 at start and 20 after 250 matches
        coeffKplayer = aCoeffK * 250 / ((nbmatches + 5) ** 0.4)

        if nbmatchesopp < PlayerElo.coeff_KCoeff_opp:
            # if the ELO of the opponent is not really defined yet (less than 100 sets/matches)
            # K factor is largely decreased (as the opp's ELO rating can't be trusted)
            # K is divided by (for p_KCoeff_opp=50):
            #  - 5 if 10 matches or less for opp
            #  - 2 if 25 matches
            #  - 1 if 50+ matches...
            # K is divided by (for p_KCoeff_opp=100):
            #  - 5 if 10 matches or less for opp
            #  - 2 if 25 matches
            #  - 1 if 50+ matches...
            nbmatchesopp = max(nbmatchesopp, 1)
            coeffKplayer = coeffKplayer / max(
                1, PlayerElo.coeff_KCoeff_opp / max(nbmatchesopp, 10)
            )
        return coeffKplayer

    @staticmethod
    def get_elo_value_from_rank(rank, isatp: bool) -> int:
        ranks_elo_min = ListRankEloATPMin
        values_elo_rank = values_elo_rankATP
        if not (isatp):
            list = ListRankEloWTAMin
            list2 = values_elo_rankWTA

        if rank < 1 or rank >= ranks_elo_min[0]:
            # init all players at this minimum value
            return round(values_elo_rank[0])
        index = 0
        while rank < ranks_elo_min[index]:
            index += 1
        # valueELo will be a weighted average of the value
        valueEloIntervallMin = 0
        intervalMin = ranks_elo_min[0]
        intervalMax = ranks_elo_min[index]
        if index > 0:
            valueEloIntervallMin = values_elo_rank[index - 1]
            intervalMin = ranks_elo_min[index - 1]
        valueEloIntervallMax = values_elo_rank[index]
        valueElo = (
            valueEloIntervallMax * (intervalMin - rank)
            + valueEloIntervallMin * (rank - intervalMax)
        ) / (intervalMin - intervalMax)
        return round(valueElo)

    @staticmethod
    def get_match_proba(rating1: float, rating2: float, nbsetsforwin: int) -> float:
        """Return the proba for player 1

        Args:
            rating1 ([float]): rating P2!
            rating2 ([float]): rating P1!
            nbsetsforwin (int): #sets for winning the match (3 or 5)
        Returns:
            float: [description]
        """

        proba = (1 + 10 ** ((rating1 - rating2) / 400.0)) ** -1
        if nbsetsforwin == 3:
            proba = get_match_proba_bo5(proba)
        return proba


########################################################################################
########################################################################################
########################################################################################
########################################################################################


class PlayersElo:
    @staticmethod
    def build_elos_for_match(
        players: dict,
        name1: str,
        id1: str,
        # rank1: int,
        name2: str,
        id2: str,
        # rank2: int,
        nbsets_won1: int,
        nbsets_won2: int,
        trn_rk: int,
        idround: int,
        idcourt: int,
        date_match: datetime,
        is_completed: bool,
        # isatp: bool,
        issetbysetupdate: bool,
        isadj_for_out_period: bool,
    ):
        """From a match result info, it calculates/returns the ELO info for each player:
        Args:
            players (dict): the dictionnary containing all Elo history by players. {<idP>: <PlayerElo>}. It will be used/updated.
            name1 (str): P1 name
            id1 (str): id1
            name2 (str): P2 name
            id2 (str): id2
            nbsets_won1 (int): sets won P1
            nbsets_won2 (int): sets won P2
            trn_rk (int): Trn Category/Rank
            idround (int): Round Id
            idcourt(int): Court Id
            date (datetime):
            is_completed (bool):
            issetbysetupdate (bool): 2 modes exist for updating ELO. Either by counting just the match result or Each set.
            isadj_for_out_period (bool): True if we should update ELO for out periods (Only applied to player 1600+ Elo)
        Returns:
            Tuple:
            - Elo1 before match
            - Nb matches for calc of Elo1
            - Elo1 after match
            - Days since last elo1 before match
            - Elo2 before match
            - Nb matches for calc of Elo2
            - Elo2 after match
            - Days since last elo2 before match
            - Proba elo
        """
        idcourt_cat = PlayerElo.get_idcourt_cat_from_idcourt(idcourt)
        # get the latest ELo rating before the match
        p1, elo1, nbelo1, date_last_elo1 = PlayerElo.get_elobeforematch_orcreate(
            players, name1, id1, 0  # , rank1, isatp
        )
        p2, elo2, nbelo2, date_last_elo2 = PlayerElo.get_elobeforematch_orcreate(
            players, name2, id2, 0  # , rank2, isatp
        )
        (
            _,
            elo1_court,
            nbelo1_court,
            date_last_elo1_court,
        ) = PlayerElo.get_elobeforematch_orcreate(
            players, name1, id1, idcourt_cat  # , rank1, isatp
        )
        (
            _,
            elo2_court,
            nbelo2_court,
            date_last_elo2_court,
        ) = PlayerElo.get_elobeforematch_orcreate(
            players, name2, id2, idcourt_cat  # , rank2, isatp
        )

        days_since_last_elo1 = -1
        eloadj1 = 0
        days_since_last_elo2 = -1
        eloadj2 = 0
        days_since_last_elo1_court = -1
        days_since_last_elo2_court = -1

        elo1, days_since_last_elo1 = PlayerElo.get_nr_days_since_last_rating(
            date_match, isadj_for_out_period, elo1, date_last_elo1
        )
        elo2, days_since_last_elo2 = PlayerElo.get_nr_days_since_last_rating(
            date_match, isadj_for_out_period, elo2, date_last_elo2
        )
        _, days_since_last_elo1_court = PlayerElo.get_nr_days_since_last_rating(
            date_match, False, elo1_court, date_last_elo1_court
        )
        _, days_since_last_elo2_court = PlayerElo.get_nr_days_since_last_rating(
            date_match, False, elo2_court, date_last_elo2_court
        )

        # init the 2 var in case not updated later
        elo1after = elo1
        elo2after = elo2
        elo1_court_after = elo1_court
        elo2_court_after = elo2_court
        proba_match1 = -1
        proba_match1_court = -1
        if is_completed:
            nbsetstowin = max(nbsets_won1, nbsets_won2)
            proba_match1 = round(PlayerElo.get_match_proba(elo2, elo1, nbsetstowin), 3)
            proba_match1_court = round(
                PlayerElo.get_match_proba(elo2_court, elo1_court, nbsetstowin), 3
            )
            if issetbysetupdate:
                elo1after, elo2after = PlayerElo.get_new_elo_ratings_setbyset(
                    elo1,
                    elo2,
                    nbelo1,
                    nbelo2,
                    nbsets_won1,
                    nbsets_won2,
                    trn_rk,
                    idround,
                )

                (
                    elo1_court_after,
                    elo2_court_after,
                ) = PlayerElo.get_new_elo_ratings_setbyset(
                    elo1_court,
                    elo2_court,
                    nbelo1_court,
                    nbelo2_court,
                    nbsets_won1,
                    nbsets_won2,
                    trn_rk,
                    idround,
                )
            else:
                elo1after, elo2after = PlayerElo.get_new_elo_ratings_match(
                    elo1,
                    elo2,
                    nbelo1,
                    nbelo2,
                    True,
                    idround,
                    trn_rk,
                )
                (
                    elo1_court_after,
                    elo2_court_after,
                ) = PlayerElo.get_new_elo_ratings_match(
                    elo1_court,
                    elo2_court,
                    nbelo1_court,
                    nbelo2_court,
                    True,
                    idround,
                    trn_rk,
                )
            # add overall rating P1
            p1.add_rating(
                0,
                elo1after,
                date_match,
                nbelo1 + nbsets_won1 + nbsets_won2,
            )
            # add court_cat rating P1
            p1.add_rating(
                idcourt_cat,
                elo1_court_after,
                date_match,
                nbelo1_court + nbsets_won1 + nbsets_won2,
            )
            # add rating P2
            p2.add_rating(
                0,
                elo2after,
                date_match,
                nbelo2 + nbsets_won1 + nbsets_won2,
            )
            # add court_cat rating P2
            p2.add_rating(
                idcourt_cat,
                elo2_court_after,
                date_match,
                nbelo2_court + nbsets_won1 + nbsets_won2,
            )
        print(
            elo1,
            nbelo1,
            elo1after,
            days_since_last_elo1,
            elo2,
            nbelo2,
            elo2after,
            days_since_last_elo2,
            proba_match1,
        )
        return (
            elo1,
            nbelo1,
            elo1after,
            days_since_last_elo1,
            elo2,
            nbelo2,
            elo2after,
            days_since_last_elo2,
            proba_match1,
            elo1_court,
            nbelo1_court,
            elo1_court_after,
            days_since_last_elo1_court,
            elo2_court,
            nbelo2_court,
            elo2_court_after,
            days_since_last_elo2_court,
            proba_match1_court,
        )

    @staticmethod
    def get_datetime(myelodate: int) -> datetime:
        """Returns a datetime from the ELO date

        Args:
            myelodate (int): ELO date format "YYYYMMDDn" with n=index of match of the day

        Returns:
            datetime: can be None if myelodate==-1
        """
        if str(myelodate) == "-1":
            return None
        else:
            return datetime.strptime(str(myelodate)[:-1], "%Y%m%d")

    @staticmethod
    def get_date_eloformat(date: datetime) -> int:
        """Returns a ELO date from the datetime

        Args:
            date (datetime): date to transform

        Returns:
            int: ELO date format "YYYYMMDDn" with n=0 of match of the day
        """
        return int(date.strftime("%Y%m%d") + "0")

    @staticmethod
    def get_latest_ranking_year(players: dict, idcourt_cat: int = 0):
        playersandlastelo = []
        for p in players:
            player: PlayerElo = players[p]
            last_rating = player.get_latest_rating(idcourt_cat)
            # if int(str(last_rating[2])[0:4]) >= 2020:
            playersandlastelo.append((player.name, last_rating))
        playersandlastelo.sort(key=lambda x: x[1][0], reverse=True)
        for i in range(1, 50):
            print(
                str(i)
                + "-"
                + playersandlastelo[i - 1][0]
                + "-"
                + str(playersandlastelo[i - 1][1][0]),
                sep="\n",
            )
        """"
        indices = list(range(len(input)))
        indices.sort(key=lambda x: input[x])
        output = [0] * len(indices)
        for i, x in enumerate(indices):
            output[x] = i"""

    @staticmethod
    def to_dict(players):
        newdict = {}
        for player in players.values():
            if isinstance(player, PlayerElo):
                dict = {
                    "name": player.name,
                    "eloratings": player.eloratings,
                    "elomatches": player.elomatches,
                }
                newdict[player.id] = dict
            else:
                type_name = player.__class__.__name__
                raise TypeError("Unexpected type {0}".format(type_name))
        return newdict

    @staticmethod
    def fromJson(players):
        newdict = {}
        for player in players.values():
            if isinstance(player, PlayerElo):
                dict = {
                    "name": player.name,
                    "eloratings": player.eloratings,
                    "elomatches": player.elomatches,
                }
                newdict[player.id] = dict
            else:
                type_name = player.__class__.__name__
                raise TypeError("Unexpected type {0}".format(type_name))
        return newdict

    @staticmethod
    def serialize(ratings, filename="AllElos.json"):
        newdict = {i: j.__dict__ for i, j in ratings.items()}
        json.dump(newdict, open(filename, "w"), indent=2)

    @staticmethod
    def deserialize(filename="AllElos.json"):
        try:
            o = json.load(open(filename))
            pe = {}
            try:
                for k, v in o.items():
                    obj = PlayerElo(name="0", id="0")  # , rank=-1)
                    obj.__dict__.update(v)
                    pe[int(k)] = obj
                return pe
            except:
                raise Exception("Error parsing " + filename)
        except:
            return None

    @staticmethod
    def filterplayersratings_byyear(idcourt_cat: int, players: dict, year: int) -> dict:
        """From the playerd ratings dictionnary it filters to only keep a specific year

        Args:
            idcourt_cat (int): [description]
            players (dict): [description]
            year (int): [description]

        Returns:
            (dict): [description]
        """
        playersCopy = {}
        for p in players:
            player = players[p]
            last_rating = player.get_latest_rating(idcourt_cat)
            if int(str(last_rating[2])[0:4]) >= year and last_rating[1] > 25:
                playerCopy = PlayerElo(name=player.name, id=player.id)  # , rank=-1)
                filtered_dict = {
                    k: v
                    for (k, v) in player.eloratings.items()
                    if int(str(k)[0:4]) == year
                }
                filtered_dict2 = {
                    k: v
                    for (k, v) in player.elomatches.items()
                    if int(str(k)[0:4]) == year
                }
                filtered_dict_clay = {
                    k: v
                    for (k, v) in player.eloratings_clay.items()
                    if int(str(k)[0:4]) == year
                }
                filtered_dict2_clay = {
                    k: v
                    for (k, v) in player.elomatches_clay.items()
                    if int(str(k)[0:4]) == year
                }
                filtered_dict_nonclay = {
                    k: v
                    for (k, v) in player.eloratings_nonclay.items()
                    if int(str(k)[0:4]) == year
                }
                filtered_dict2_nonclay = {
                    k: v
                    for (k, v) in player.elomatches_nonclay.items()
                    if int(str(k)[0:4]) == year
                }
                playerCopy.eloratings = filtered_dict
                playerCopy.elomatches = filtered_dict2
                playerCopy.eloratings_clay = filtered_dict_clay
                playerCopy.elomatches_clay = filtered_dict2_clay
                playerCopy.eloratings_nonclay = filtered_dict_nonclay
                playerCopy.elomatches_nonclay = filtered_dict2_nonclay
                playersCopy[playerCopy.id] = playerCopy
        # playersCopy.sort(key=lambda x: x[1][0], reverse=True)
        return playersCopy


# constants
ListRankEloATPMin = [450, 380, 300, 250, 200, 150, 100, 75, 50, 25, 15, 10, 1]
values_elo_rankATP = [
    1200,
    1300,
    1420,  # 300
    1473,
    1532,  # 200
    1602,
    1685,  # 100
    1730,
    1797,  # 50
    1860,
    1920,  # 15
    1960,
    2200,
]
ListRankEloWTAMin = [
    700,
    500,
    450,
    400,
    350,
    300,
    250,
    200,
    150,
    100,
    75,
    50,
    25,
    15,
    10,
    1,
]
values_elo_rankWTA = [
    970,
    1040,
    1070,
    1100,
    1195,
    1297,
    1397,
    1492,
    1592,
    1674,
    1742,
    1806,
    1866,
    1931,
    1973,
    2100,
]
