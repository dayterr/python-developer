import datetime as dt
from typing import List, Optional

DATE_PATTERN = '%d.%m.%Y'


class Record:

    def __init__(
            self,
            amount: float,
            comment: str,
            date: Optional[str] = None
    ) -> None:
        self.amount = amount
        self.comment = comment
        if date is not None:
            self.date = dt.datetime.strptime(date, DATE_PATTERN).date()
        else:
            self.date = dt.date.today()


class Calculator:

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.records: List[Record] = []

    def add_record(self, rec: Record) -> None:
        self.records.append(rec)

    def get_today_stats(self) -> float:
        today = dt.date.today()
        today_stats = sum(r.amount for r in self.records if r.date == today)
        return today_stats

    def get_week_stats(self) -> float:
        today = dt.date.today()
        week_ago = today - dt.timedelta(weeks=1)
        week_stats = sum(
            r.amount for r in self.records if week_ago < r.date <= today
        )
        return week_stats

    def get_today_remainder(self) -> float:
        remainder = self.limit - self.get_today_stats()
        return remainder


class CaloriesCalculator(Calculator):

    def get_calories_remained(self) -> str:
        to_eat = self.get_today_remainder()
        if to_eat > 0:
            msg = ('Сегодня можно съесть что-нибудь ещё,'
                   f' но с общей калорийностью не более {to_eat} кКал')
            return msg
        return 'Хватит есть!'


class CashCalculator(Calculator):
    USD_RATE = 73.4
    EURO_RATE = 87.52
    RUB_RATE = 1.0

    def get_today_cash_remained(self, currency: str) -> str:
        to_spend = self.get_today_remainder()
        if to_spend == 0:
            return 'Денег нет, держись'
        cash_rates = {'rub': (self.RUB_RATE, 'руб'),
                      'eur': (self.EURO_RATE, 'Euro'),
                      'usd': (self.USD_RATE, 'USD')}
        if currency in cash_rates:
            rate, curr = cash_rates[currency]
            to_spend = round(to_spend / rate, 2)
            if to_spend > 0:
                return f'На сегодня осталось {to_spend} {curr}'
            debt = abs(to_spend)
            return f'Денег нет, держись: твой долг - {debt} {curr}'
        return 'Данная валюта неизвестна калькулятору'
