"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
from datetime import datetime, timedelta
from ELO.elorating import PlayerElo


def test_get_latest_rating_1():
    p: PlayerElo
    p = PlayerElo("name1", "1", 1500)
    res = PlayerElo.get_latest_rating(p)
    assert res == (1500, 0, -1)


def test_get_latest_rating_2():
    p: PlayerElo
    p = PlayerElo("name1", "1", 1500)
    p.add_rating(1550, datetime(2020, 10, 10), 2)
    nbmatches = PlayerElo.get_latest_rating(p)[1]
    p.add_rating(1750, datetime(2020, 10, 20), nbmatches + 3)
    res2 = PlayerElo.get_latest_rating(p)
    assert res2 == (1750, 5, 202010200)


def test_getKcoeff_1():
    k = PlayerElo.get_Kcoeff(0, 1000, 1, 9, False)
    assert round(k) == 131


def test_getKcoeff_2():
    k = PlayerElo.get_Kcoeff(300, 1000, 1, 6, False)
    assert round(k) == 25


def test_getKcoeff_3():
    k = PlayerElo.get_Kcoeff(0, 10, 1, 9, False)
    assert round(k) == 26


def test___get_new_elo_ratings_1():
    res = PlayerElo.__get_new_elo_ratings(1429, 1672, 131, 25, False)
    assert round(res[0]) == 1429 and round(res[1]) == 1672
