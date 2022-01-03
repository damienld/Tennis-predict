from datetime import datetime
from collections import namedtuple

DateDayMonth = namedtuple("DateMonthYear", ["day", "month"])
DateStartOffSeason = DateDayMonth(1, 11)  # 01/11
DateEndOffSeason = DateDayMonth(20, 12)  # 20/12
MaxDaysOffSeasonToCheck = 30


def calc_datediff_withoutoffseason(date_new: datetime, date_last: datetime) -> int:
    date_endoffseason = datetime(
        date_last.year, DateEndOffSeason.month, DateEndOffSeason.day
    )
    date_startoffseason = datetime(
        date_last.year, DateStartOffSeason.month, DateStartOffSeason.day
    )

    if date_new > date_startoffseason and date_last < date_endoffseason:
        if (date_new - date_last).days > MaxDaysOffSeasonToCheck:
            nr_days_after_endoffseason = max(0, (date_new - date_endoffseason).days)
            nr_days_before_startoffseason = max(
                0, (date_startoffseason - date_last).days
            )
            return max(
                MaxDaysOffSeasonToCheck,
                nr_days_after_endoffseason + nr_days_before_startoffseason,
            )
        else:
            return calc_datediff_withoutcovidperiod(date_new, date_last)
    else:
        return calc_datediff_withoutcovidperiod(date_new, date_last)


def calc_datediff_withoutcovidperiod(date_new: datetime, date_last: datetime) -> int:
    date_endoffseason = datetime(2020, 8, 20)
    date_startoffseason = datetime(2020, 3, 10)

    if date_new > date_startoffseason and date_last < date_endoffseason:
        if (date_new - date_last).days > MaxDaysOffSeasonToCheck:
            nr_days_after_endoffseason = max(0, (date_new - date_endoffseason).days)
            nr_days_before_startoffseason = max(
                0, (date_startoffseason - date_last).days
            )
            return max(
                MaxDaysOffSeasonToCheck,
                nr_days_after_endoffseason + nr_days_before_startoffseason,
            )
        else:
            return max(0, (date_new - date_last).days)
    else:
        return max(0, (date_new - date_last).days)
