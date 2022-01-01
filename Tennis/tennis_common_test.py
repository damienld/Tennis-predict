import tennis_common
from datetime import datetime


class Test_Tennis_common_Calc_datediff_withoutoffseason:
    def test_calc_datediff_withoutoffseason_1(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2021, 12, 26), datetime(2021, 10, 1)
        )
        assert result == 37

    def test_calc_datediff_withoutoffseason_2(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2021, 12, 26), datetime(2021, 11, 10)
        )
        assert result == tennis_common.MaxDaysOffSeasonToCheck

    def test_calc_datediff_withoutoffseason_3(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2021, 12, 26), datetime(2021, 12, 15)
        )
        assert result == 11

    def test_calc_datediff_withoutoffseason_4(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2021, 12, 10), datetime(2021, 10, 1)
        )
        assert result == 31

    def test_calc_datediff_withoutoffseason_4(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2022, 1, 15), datetime(2021, 11, 10)
        )
        assert result == 26

    def test_calc_datediff_withoutoffseason_4(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2022, 3, 15), datetime(2022, 1, 15)
        )
        assert result == 59

    def test_calc_datediff_withoutoffseason_6(self):
        result = tennis_common.calc_datediff_withoutoffseason(
            datetime(2020, 8, 30), datetime(2020, 2, 15)
        )
        assert result == 34
