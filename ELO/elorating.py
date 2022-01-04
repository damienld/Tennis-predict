"""
"""
from datetime import datetime
import json
from typing import Tuple
from pandas import DataFrame
from tennis.tennis_common import calc_datediff_withoutoffseason

# from dataclasses import dataclass, field


class PlayerElo:
    """
    A class to represent a player in the Elo Rating System
    """

    coeff_KCoeff_opp = 50  # try values from 1 to 100 (see Kcoeff calculation)
    elo_initialrating = 1500
    min_day_outperiod = 55

    def __init__(self, name: str, id: str):
        self.id = id
        self.name = name
        # comment the 2 lines below in order to start with a rating associated to current player rank
        self.eloratings = {-1: PlayerElo.elo_initialrating}
        self.elomatches = {-1: 0}

    def __repr__(self):
        rating = self.get_latest_rating()
        return ("{} {} {} ({})").format(self.name, self.id, rating[0], rating[1])

    """    def temp(
            players: dict,
            elo1: float,
            elo2: float,
            id1: str,
            rank1: int,
            id2: str,
            rank2: int,
            nbsets_won1: int,
            nbsets_won2: int,
            trn_rk: int,
            idround: int,
            date_match: datetime,
            is_completed: bool,
            isadj_for_out_period: bool,
        ):
            if is_completed:
                proba_match1 = round(PlayerElo.get_match_proba(elo2, elo1), 3)
                elo1after, elo2after = PlayerElo.get_new_elo_ratings_setbyset(
                    elo1,
                    elo2,
                    nbelo1,
                    nbelo2,
                    days_since_last_elo1,
                    days_since_last_elo2,
                    nbsets_won1,
                    nbsets_won2,
                    trn_rk == 4,
                    idround,
                )
                p1.add_rating(elo1after, date_match, nbelo1 + nbsets_won1 + nbsets_won2)
                p2.add_rating(elo2after, date_match, nbelo2 + nbsets_won1 + nbsets_won2)
    """

    def get_Elo_since(
        self,
        df_list_matches: DataFrame,
        surface_ids: list[int],
        date_start: datetime,
        date_end: datetime,
    ) -> float:
        """[summary]

        Args:
            df_list_matches (DataFrame): [description]
            surface_ids (list[int]): [description]
            date_start (datetime): date start (included)
            date_end (datetime): date end (included)

        Returns:
            float: [description]
        """
        query = "(P1Id==" + self.id + " | P2Id==" + self.id + ")"
        if date_start != None:
            query += "& (Date >= " + date_start + " & Date <= " + date_end + ")"
        df_filtered = df_list_matches.query(query)
        playerfilteredElo = PlayerElo(name=self.name, id=self.id)
        """df_filtered.apply(
            lambda row: temp(
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
                True,
            )
        )"""
        return 0

    def get_latest_rating(self) -> Tuple[int, int, int]:
        """Returns the rating information (Elo rating, # matches, date) from the last match played

        Args:

        Returns:
            Tuple:
            - int: value of latest Elo rating
            - int: nb matches for the calculation of this latest rating
            - int: (-1 if no previous elo) date with format(YYYYMMDDn) where n is the match index of that day (often 0)
        """
        # to filter before a date:
        # filtered_dict = {k: v for (k, v) in self.eloratings.items() if k < date}
        if len(self.eloratings) <= 0:
            return self.initialrating, 0, -1
        else:
            max_date = max(self.eloratings.keys(), key=int)
            return (
                round(self.eloratings[max_date]),
                self.elomatches[max_date],
                max_date,
            )

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

    def add_rating(
        self, newrating: int, date: datetime, nr_matches_to_set: int
    ) -> None:
        """Add the updated ELO rating to eloratings. And the total number of matches.

        Args:
            newrating (int): Updated elo rating after the new match
            date (datetime): Date of the match
            nr_matches_to_set (int): Set the new total number of matches! (no addition)
        """
        # the key will be the date of the day + the match index for the day: 0
        day = "{0}{1}{2}{3}".format(
            date.year, "%02d" % date.month, "%02d" % date.day, 0
        )
        if self.elomatches.get(day, None) != None:
            day = "{0}{1}{2}{3}".format(
                date.year, "%02d" % date.month, "%02d" % date.day, 1
            )
            # if a match has always been added for this day change the end of key to 2
            if self.elomatches.get(day, None) == None:
                day = "{0}{1}{2}{3}".format(
                    date.year, "%02d" % date.month, "%02d" % date.day, 2
                )
                if self.elomatches.get(day, None) == None:
                    day = "{0}{1}{2}{3}".format(
                        date.year, "%02d" % date.month, "%02d" % date.day, 3
                    )
        day = int(day)
        self.eloratings[day] = newrating
        self.elomatches[day] = nr_matches_to_set

    @staticmethod
    def update_elos_matches(
        players: dict,
        row_name: str,
        name1: str,
        id1: str,
        rank1: int,
        name2: str,
        id2: str,
        rank2: int,
        nbsets_won1: int,
        nbsets_won2: int,
        trn_rk: int,
        idround: int,
        date_match: datetime,
        is_completed: bool,
        isatp: bool,
        issetbysetupdate: bool,
        isadj_for_out_period: bool,
    ):
        """From a match result info, it calculates/returns the ELO info for each player:

        Args:
            players (dict): the dictionnary containing all Elo history by players. It will be used/updated.
            name1 (str): P1 name
            id1 (str): id1
            rank1 (int): ATP Rank P1
            name2 (str): P2 name
            id2 (str): id2
            rank2 (int): ATP Rank P2
            nbsets_won1 (int): sets won P1
            nbsets_won2 (int): sets won P2
            trn_rk (int): Trn Category/Rank
            idround (int): Round Id
            date (datetime):
            is_completed (bool):
            isatp (bool): Only used if we apply initial rating in function of the ATP Rank (Not Used atm)
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
        # try:
        p1, elo1, nbelo1, date_last_elo1 = PlayerElo.get_elobeforematch_orcreate(
            players, name1, id1, rank1, isatp
        )
        p2, elo2, nbelo2, date_last_elo2 = PlayerElo.get_elobeforematch_orcreate(
            players, name2, id2, rank2, isatp
        )
        days_since_last_elo1 = -1
        eloadj1 = 0
        days_since_last_elo2 = -1
        eloadj2 = 0
        if isadj_for_out_period:
            if date_last_elo1 >= 0:
                date_last_elo1 = PlayersElo.get_datetime(date_last_elo1)
                if elo1 > 1600:
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

            if date_last_elo2 >= 0:
                date_last_elo2 = PlayersElo.get_datetime(date_last_elo2)
                if elo2 > 1600:
                    # only check out periods for players in top 100
                    # because others might have gone to lower level rather than
                    # really being out
                    days_since_last_elo2 = calc_datediff_withoutoffseason(
                        date_match, date_last_elo2
                    )
                    eloadj2 = PlayerElo.get_adjustment_elo_when_player_was_out(
                        days_since_last_elo2
                    )
                    elo2 = elo2 + eloadj2
                else:
                    days_since_last_elo2 = max(0, (date_match - date_last_elo2).days)
        # init the 2 var in case not updated later
        elo1after = elo1
        elo2after = elo2
        proba_match1 = -1
        if is_completed:
            proba_match1 = round(PlayerElo.get_match_proba(elo2, elo1), 3)
            if issetbysetupdate:
                elo1after, elo2after = PlayerElo.get_new_elo_ratings_setbyset(
                    elo1,
                    elo2,
                    nbelo1,
                    nbelo2,
                    days_since_last_elo1,
                    days_since_last_elo2,
                    nbsets_won1,
                    nbsets_won2,
                    trn_rk == 4,
                    idround,
                )
            else:
                elo1after, elo2after = PlayerElo.get_new_elo_ratings_match(
                    elo1,
                    elo2,
                    nbelo1,
                    nbelo2,
                    days_since_last_elo1,
                    days_since_last_elo2,
                    True,
                    trn_rk == 4,
                    idround,
                )
            p1.add_rating(elo1after, date_match, nbelo1 + nbsets_won1 + nbsets_won2)
            p2.add_rating(elo2after, date_match, nbelo2 + nbsets_won1 + nbsets_won2)
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
        )

    @staticmethod
    def __get_new_elo_ratings(
        rating1: float,
        rating2: float,
        aKcoeff1: float,
        aKcoeff2: float,
        is_player1won: bool,
    ) -> Tuple[float, float]:
        """Private. Calculate the new Elo ratings for both players after the match.

        Args:
            rating1 (float): [description]
            rating2 (float): [description]
            aKcoeff1 (float): [description]
            aKcoeff2 (float): [description]
            is_player1won (bool): [description]

        Returns:
            Tuple[float, float]:
            - New rating P1
            - New rating P2
        """
        proba_match2 = PlayerElo.get_match_proba(rating1, rating2)
        proba_match1 = PlayerElo.get_match_proba(rating2, rating1)

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
        days_since_last_elo1: int,
        days_since_last_elo2: int,
        is_player1_won: bool,
        is_slam: bool,
        idround: int,
    ) -> Tuple[float, float]:
        """Calculate the new Elo ratings for both players after the match. Using MATCH method (not set_by_set)

        Args:
            rating1 (float): [description]
            rating2 (float): [description]
            nbmatches1 (int): [description]
            nbmatches2 (int): [description]
            days_since_last_elo1 (int): [description]
            days_since_last_elo2 (int): [description]
            is_player1_won (bool): [description]
            is_slam (bool): [description]
            idround (int): [description]

        Returns:
            Tuple[float, float]: [description]
        """
        if rating2 < 0 or rating1 < 0:
            return rating1, rating2
        coeffKA = PlayerElo.get_Kcoeff(
            nbmatches1, nbmatches2, days_since_last_elo1, idround, is_slam
        )
        coeffKB = PlayerElo.get_Kcoeff(
            nbmatches2, nbmatches1, days_since_last_elo2, idround, is_slam
        )
        return PlayerElo.__get_new_elo_ratings(
            rating1, rating2, coeffKA, coeffKB, is_player1_won
        )

    @staticmethod
    def get_new_elo_ratings_setbyset(
        rating1: float,
        rating2: float,
        nbmatches1: int,
        nbmatches2: int,
        days_since_last_elo1: int,
        days_since_last_elo2: int,
        nbsets_won1: int,
        nbsets_won2: int,
        is_slam: bool,
        idround: int,
    ) -> Tuple[int, int]:
        """Calculate the new Elo ratings for both players after the match. Using set_by_set method (not MATCH)

        Args:
            rating1 (float): [description]
            rating2 (float): [description]
            nbmatches1 (int): [description]
            nbmatches2 (int): [description]
            days_since_last_elo1 (int): [description]
            days_since_last_elo2 (int): [description]
            nbsets_won1 (int): [description]
            nbsets_won2 (int): [description]
            is_slam (bool): [description]
            idround (int): [description]

        Returns:
            Tuple[int, int]: [description]
        """
        # is_slam = False
        gainToRating1 = 0
        gainToRating2 = 0
        for i in range(1, nbsets_won1 + 1):
            newratings = PlayerElo.get_new_elo_ratings_match(
                rating1,
                rating2,
                nbmatches1,
                nbmatches2,
                days_since_last_elo1,
                days_since_last_elo2,
                True,
                is_slam,
                idround,
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
                days_since_last_elo1,
                days_since_last_elo2,
                False,
                is_slam,
                idround,
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
        listplayers: dict, name: str, id: str, rank: int, isatp: bool
    ):
        """
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
            initial_rating = PlayerElo.get_initial_rating(rank, isatp)
            player = PlayerElo(name=name, id=id)
            listplayers[id] = player
            return (
                player,
                round(player.get_latest_rating()[0]),
                player.get_latest_rating()[1],
                player.get_latest_rating()[2],
            )
        else:
            return (
                player,
                round(player.get_latest_rating()[0]),
                player.get_latest_rating()[1],
                player.get_latest_rating()[2],
            )

    @staticmethod
    def get_Kcoeff(
        nbmatches: int,
        nbmatchesopp: int,
        days_since_last_elo: int,
        roundid: int,
        is_slam: bool,
    ) -> float:
        """[summary]

        Args:
            nbmatches (int): [description]
            nbmatchesopp (int): set to 1000+ to ignore
            days_since_last_elo (int): [description]
            roundid (int): [description]
            is_slam (bool): [description]

        Returns:
            float: [description]
        """
        # ToDo if (days_since_last_elo)
        aCoeffK = 1
        if roundid <= 4:
            # Round 2 or -
            aCoeffK = 0.85
        if roundid == 5:
            # Round 2 or -
            aCoeffK = 0.95
        # 538 K-Factor https://www.betfair.com.au/hub/tennis-elo-modelling/
        # which is 130 at start and 20 after 250 matches
        coeffKplayer = aCoeffK * 250 / ((nbmatches + 5) ** 0.4)
        if is_slam and roundid >= 4:
            coeffKplayer *= 1.15
        if nbmatchesopp < 50:
            # if the ELO of the opponent is not really defined yet (less than 50 matches)
            # K factor is largely decreased (as the opp's ELO rating can't be trusted)
            # K is divided by (for p_KCoeff_opp=50):
            #  - 5 if 10 matches or less for opp
            #  - 2 if 25 matches
            #  - 1 if 50+ matches...
            coeffKplayer = coeffKplayer / max(
                1, PlayerElo.coeff_KCoeff_opp / min(max(nbmatchesopp, 1), 10)
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
    def get_initial_rating(rank: int, isatp: bool) -> int:
        return PlayerElo.get_elo_value_from_rank(rank, isatp)

    @staticmethod
    def get_match_proba(rating1, rating2) -> float:
        """
        Compares the two ratings of the this player and the opponent.
        @param opponent - the player to compare against.
        @returns - The expected score between the two players.
        """
        return (1 + 10 ** ((rating1 - rating2) / 400.0)) ** -1


########################################################################################
########################################################################################
########################################################################################
########################################################################################


class PlayersElo:
    @staticmethod
    def get_datetime(myelodate: int):
        return datetime.strptime(str(myelodate)[:-1], "%Y%m%d")

    @staticmethod
    def get_latest_ranking_year(players: dict):
        playersandlastelo = []
        for p in players:
            player = players[p]
            last_rating = player.get_latest_rating()
            # if int(str(last_rating[2])[0:4]) >= 2020:
            playersandlastelo.append((player.name, last_rating))
        playersandlastelo.sort(key=lambda x: x[1][0], reverse=False)
        print(*playersandlastelo, sep="\n")
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
    def serialize(ratings, filename="AllElo.json"):
        newdict = {i: j.__dict__ for i, j in ratings.items()}
        json.dump(newdict, open(filename, "w"), indent=2)

    @staticmethod
    def deserialize(filename="AllElo.json"):
        try:
            o = json.load(open(filename))
            pe = {}
            try:
                for k, v in o.items():
                    obj = PlayerElo(name="0", id="0")
                    obj.__dict__.update(v)
                    pe[int(k)] = obj
                return pe
            except:
                raise Exception("Error parsing " + filename)
        except:
            return None

    @staticmethod
    def filterplayersratings_byyear(players: dict, year: int):
        playersCopy = {}
        for p in players:
            player = players[p]
            last_rating = player.get_latest_rating()
            if int(str(last_rating[2])[0:4]) >= year and last_rating[1] > 25:
                playerCopy = PlayerElo(name=player.name, id=player.id)
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
                playerCopy.eloratings = filtered_dict
                playerCopy.elomatches = filtered_dict2
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
