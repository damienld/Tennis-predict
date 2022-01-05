"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
from datetime import datetime, timedelta
from elo.elorating import PlayerElo
import pytest


class Test_get_idcourt_cat_from_idcourt:
    def test_get_idcourt_cat_from_idcourt_1(self):
        with pytest.raises(Exception) as e_info:
            PlayerElo.get_idcourt_cat_from_idcourt(0)

    def test_get_idcourt_cat_from_idcourt_2(self):
        assert (
            PlayerElo.get_idcourt_cat_from_idcourt(3) == 2
            and PlayerElo.get_idcourt_cat_from_idcourt(1) == 2
            and PlayerElo.get_idcourt_cat_from_idcourt(2) == 1
            and PlayerElo.get_idcourt_cat_from_idcourt(4) == 2
            and PlayerElo.get_idcourt_cat_from_idcourt(5) == 2
        )


def test_get_latest_rating_1():
    p: PlayerElo
    p = PlayerElo("name1", "1", -1)
    res = PlayerElo.get_latest_rating(p, 0)
    assert res == (PlayerElo.elo_initialrating, 0, -1)


def test_get_latest_rating_2():
    # work for PlayerElo.elo_initialrating=1500
    p: PlayerElo
    p = PlayerElo("name1", "1", -1)
    p.add_rating(1, 1550, datetime(2020, 10, 10), 2)
    nbmatches = PlayerElo.get_latest_rating(p, 1)[1]
    p.add_rating(1, 1750, datetime(2020, 10, 20), nbmatches + 3)
    res2 = PlayerElo.get_latest_rating(p, 1)
    assert res2 == (1750, 5, 202010200)


def test_getKcoeff_1():
    k = PlayerElo.get_Kcoeff(0, 1000, 6, 2, False)
    assert round(k) == 131


def test_getKcoeff_2():
    k = PlayerElo.get_Kcoeff(300, 1000, 2, 6, False)
    assert round(k) == 25


def test_getKcoeff_3():
    k = PlayerElo.get_Kcoeff(0, 10, 6, 2, False)
    assert round(k) == 26


def test_getKcoeff_4():
    k = PlayerElo.get_Kcoeff(0, 10, 5, 2, False)
    assert round(k) == 25


def test_getKcoeff_5():
    k = PlayerElo.get_Kcoeff(0, 10, 5, 1, False)
    assert round(k) == 25 * 0.85


def test___get_new_elo_ratings_1():
    res = PlayerElo._PlayerElo__get_new_elo_ratings(1429, 1672, 131, 25, False)
    assert round(res[0]) == 1403 and round(res[1]) == 1677


class Test_get_adjustment_elo_when_player_was_out:
    def test_get_adjustment_elo_when_player_was_out_1(self):
        assert PlayerElo.get_adjustment_elo_when_player_was_out(50) == 0

    def test_get_adjustment_elo_when_player_was_out_2(self):
        res = PlayerElo.get_adjustment_elo_when_player_was_out(55)
        assert res == -100

    def test_get_adjustment_elo_when_player_was_out_5(self):
        res = PlayerElo.get_adjustment_elo_when_player_was_out(100)
        assert -100 >= res >= -115

    def test_get_adjustment_elo_when_player_was_out_3(self):
        res = PlayerElo.get_adjustment_elo_when_player_was_out(250)
        assert res == -150

    def test_get_adjustment_elo_when_player_was_out_4(self):
        res = PlayerElo.get_adjustment_elo_when_player_was_out(500)
        assert res == -150
