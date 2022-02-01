from tennis.tennis_probas import get_match_proba_bo5, get_one_set_proba


class Test_Tennis_probas:
    def test_get_one_set_proba_1(self):
        assert round(get_one_set_proba(0.5), 2) == 0.5

    def test_get_one_set_proba_2(self):
        assert round(get_one_set_proba(0.75), 2) == 0.67

    def test_get_match_proba_bo5_1(self):
        assert round(get_match_proba_bo5(0.5), 2) == 0.5

    def test_get_match_proba_bo5_2(self):
        assert round(get_match_proba_bo5(0.7), 2) == 0.74

    def test_get_match_proba_bo5_2(self):
        assert round(get_match_proba_bo5(0.1), 2) == 0.05
