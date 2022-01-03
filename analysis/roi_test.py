from analysis.roi import apply_roi, calc_kelly_stake
import roi


class Test_Roi_Apply_roi:
    def test_apply_roi_1(self):
        res = apply_roi(3.24, 1.3, 0.4, 0)
        assert res == (2, 2 * (3.24 - 1))

    def test_apply_roi_2(self):
        res = apply_roi(3.24, 1.3, 0.4, 1)
        assert res == (2, -2)

    def test_apply_roi_3(self):
        res = apply_roi(3.5, 1.1, 0.4, 0)
        assert res == (0, 0)  # margin too big

    def test_apply_roi_4(self):
        res = apply_roi(2.06, 1.0, 0.4, 0)
        assert res == (0, 0)  # value < min odds

    def test_apply_roi_5(self):
        res = apply_roi(1.3, 3.24, 0.6, 1)
        assert res == (2, 2 * (3.24 - 1))


class Test_Roi_Calc_kelly_stake:
    def test_calc_kelly_stake_1(self):
        res = calc_kelly_stake(0.5, 2.16)
        assert res == 1.0

    def test_calc_kelly_stake_2(self):
        res = calc_kelly_stake(0.5, 2.06)
        assert res == 0

    def test_calc_kelly_stake_3(self):
        res = calc_kelly_stake(0.4, 3.24)
        assert res == 2.0

    def test_calc_kelly_stake_4(self):
        res = calc_kelly_stake(0.9, 2.16)
        assert res == 3.0
