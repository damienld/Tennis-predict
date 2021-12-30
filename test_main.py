"""
https://www.tutorialspoint.com/pytest/pytest_starting_with_basic_test.htm
Launch all test_*.py by launching 
> pytest 
"""
import main


def test_get_data():
    df = main.get_data(True, 2013, 2021)
    assert len(df) > 0
