"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
import elorating


def test_getKcoeff_1():
    k = elorating.PlayerElo.get_Kcoeff(0, 9, False)
    assert round(k) == 131


def test_getKcoeff_2():
    k = elorating.PlayerElo.get_Kcoeff(300, 6, False)
    assert round(k) == 25


def test___get_new_elo_ratings_1():
    res = elorating.PlayerElo.__get_new_elo_ratings(1429.3, 1672, 131, 25, False)
    assert round(res[0]) == 1429 and round(res[1]) == 1672
