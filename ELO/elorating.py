"""
"""

from datetime import datetime
import json
from typing import Tuple

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


class PlayerElo:
    """
    A class to represent a player in the Elo Rating System
    """

    p_KCoeff_opp = 50  # try values from 1 to 100 (see Kcoeff calculation)
    p_initialrating = 1500

    def __init__(self, name: str, id: str, rating):
        self.id = id
        self.name = name
        # comment the 2 lines below in order to start with a rating associated to current player rank
        self.eloratings = {-1: PlayerElo.p_initialrating}
        self.elomatches = {-1: 0}
        self.initialrating = rating

    def __str__(self):
        rating = self.get_latest_rating()
        return ("{0} {} ({})").format(self.name, rating[0], rating[1])

    def get_latest_rating(self) -> Tuple[int, int, int]:
        """
        Returns Tuple:
        - int: value of latest Elo rating
        - int: nb matches for the calculation of this latest rating
        - int: (-1 if no previous elo) date with format(YYYYMMDDx) where X is the match id of that day (often 0)
        """
        if len(self.eloratings) <= 0:
            return self.initialrating, 0, -1
        else:
            max_date = max(self.eloratings.keys(), key=int)
            return (
                round(self.eloratings[max_date]),
                self.elomatches[max_date],
                max_date,
            )

    """
    def get_rating_before_date(self, date: datetime) -> Tuple[int, int, int]:
        # ToDo test!
        filtered_dict = {k: v for (k, v) in self.eloratings.items() if k < date}
        if len(self.eloratings.keys) <= 0:
            return self.initialrating, 0, 0
        else:
            max_date = max(self.eloratings.keys)
            return (
                round(self.eloratings[max_date]),
                self.elomatches[max_date],
                max_date,
            )
    """

    def add_rating(
        self, newrating: int, date: datetime, nr_matches_to_set: int
    ) -> None:
        """[summary]

        Args:
            newrating (int): [description]
            date (datetime): [description]
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
            # if a match has always been added for this day change the end of key to 1
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
        date: datetime,
        is_completed: bool,
        isatp: bool,
        issetbysetupdate: bool,
    ):
        """[summary]

        Args:
            players (dict): [description]
            row_name (str): [description]
            name1 (str): [description]
            id1 (str): [description]
            rank1 (int): [description]
            name2 (str): [description]
            id2 (str): [description]
            rank2 (int): [description]
            nbsets_won1 (int): [description]
            nbsets_won2 (int): [description]
            trn_rk (int): [description]
            idround (int): [description]
            date (datetime): [description]
            is_completed (bool): [description]
            isatp (bool): [description]
            issetbysetupdate (bool): [description]

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
        if date_last_elo1 >= 0:
            days_since_last_elo1 = (date - PlayersElo.get_datetime(date_last_elo1)).days
        days_since_last_elo2 = -1
        if date_last_elo2 >= 0:
            days_since_last_elo2 = (date - PlayersElo.get_datetime(date_last_elo2)).days
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
            p1.add_rating(elo1after, date, nbelo1 + nbsets_won1 + nbsets_won2)
            p2.add_rating(elo2after, date, nbelo2 + nbsets_won1 + nbsets_won2)
        print(row_name)
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
    ) -> Tuple[int, int]:
        proba_match2 = PlayerElo.get_match_proba(rating1, rating2)
        proba_match1 = PlayerElo.get_match_proba(rating2, rating1)

        if is_player1won:
            rating1 = rating1 + aKcoeff1 * (1 - proba_match1)
            rating2 = rating2 + aKcoeff2 * (0 - proba_match2)
        else:
            rating1 = rating1 + aKcoeff1 * (0 - proba_match1)
            rating2 = rating2 + aKcoeff2 * (1 - proba_match2)
        return round(rating1), round(rating2)

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
        """
        no need to extra weight slams matches because it s already taking more weight in
        get_new_elo_ratings_match as it s more sets
        """
        is_slam = False
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

        return round(rating1 + gainToRating1), round(rating2 + gainToRating2)

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
            player = PlayerElo(name, id, initial_rating)
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
        if roundid <= 5:
            # Round 2 or -
            aCoeffK = 0.85
        # 538 K-Factor https://www.betfair.com.au/hub/tennis-elo-modelling/
        # which is 130 at start and 20 after 250 matches
        coeffKplayer = aCoeffK * 250 / ((nbmatches + 5) ** 0.4)
        if is_slam and roundid >= 4:
            coeffKplayer *= 1.1
        if nbmatchesopp < 50:
            # K is divided by (for p_KCoeff_opp=50):
            #  - 5 if 10 matches or less for opp
            #  - 2 if 25 matches
            #  - 1 if 50+ matches...
            coeffKplayer = coeffKplayer / max(
                1, PlayerElo.p_KCoeff_opp / min(max(nbmatchesopp, 1), 10)
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


class PlayersElo:
    @staticmethod
    def get_datetime(myelodate: int):
        return datetime.strptime(str(myelodate)[:-1], "%Y%m%d")

    @staticmethod
    def get_ranking(players: dict):
        playersandlastelo = []
        for p in players:
            player = players[p]
            last_rating = player.get_latest_rating()
            if int(str(last_rating[2])[0:4]) >= 2020:
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
            for k, v in o.items():
                obj = PlayerElo("0", "0", 0)
                obj.__dict__.update(v)
                pe[int(k)] = obj
            return pe
        except:
            return None

    @staticmethod
    def filterplayersratings_byyear(players: dict, year: int):
        playersCopy = {}
        for p in players:
            player = players[p]
            last_rating = player.get_latest_rating()
            if int(str(last_rating[2])[0:4]) >= year:
                playerCopy = PlayerElo("", player.id, player.initialrating)
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
