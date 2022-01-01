import elorating


class Test_Elorating_PlayerElo_Get_Kcoeff:
    def test_get_Kcoeff_1(self):
        result = elorating.PlayerElo.get_Kcoeff(True, 50, "1.0.0", 4, True)

    def test_get_Kcoeff_2(self):
        result = elorating.PlayerElo.get_Kcoeff(False, 51.0, "v1.2.4", 6, True)

    def test_get_Kcoeff_3(self):
        result = elorating.PlayerElo.get_Kcoeff(False, 50.0, "^5.0.0", 4.0, True)

    def test_get_Kcoeff_4(self):
        result = elorating.PlayerElo.get_Kcoeff(False, 49.0, "v1.2.4", 5, True)

    def test_get_Kcoeff_5(self):
        result = elorating.PlayerElo.get_Kcoeff(False, 50, "1.0.0", 4, True)

    def test_get_Kcoeff_6(self):
        result = elorating.PlayerElo.get_Kcoeff(True, 0, "", "", True)
