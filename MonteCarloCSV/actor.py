import random

class Actor:
    def __init__(self, business_capital_start,
                 business_value_start,
                 nature_capital_start = 0,
                 nature_value_start = 0):
        self.business_value = business_value_start
        self.business_capital = business_capital_start

        self.delta_business_value = 0
        self.delta_business_capital = 0

        self.business_power = 0
        self.business_market_condition = 0

        self.nature_value = nature_value_start
        self.nature_capital = nature_capital_start

    def get_business_saldo(self):
        return self.delta_business_capital

    def calc_nature_saldo(self):
        exchange_course = 80 # 1tCo2 = 80 Euro
        nature_income = self.nature_value * exchange_course
        return nature_income
    def calc_business_capital(self):
        self.delta_business_capital = self.__calc_delta_business_capital()
        self.business_capital += self.delta_business_capital
        return self.business_capital
    def calc_business_value(self):
        self.delta_business_value = self.__calc_delta_business_value()
        self.business_value += self.delta_business_value
        return self.business_value

    def __calc_delta_business_capital(self):
        self.delta_business_capital = self.business_power * self.business_value #power and value of last year
        return self.delta_business_capital

    def __calc_delta_business_value(self):
        self.delta_business_value = self.business_market_condition * self.business_capital #condition and capital of this year
        return self.delta_business_capital
