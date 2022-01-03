"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
from datetime import datetime
from elo.elorating import PlayersElo


def test_get_datetime():
    res = PlayersElo.get_datetime(202111041)
    assert res == datetime(2021, 11, 4)
