import random


class Company:
    def __init__(self, business_value_start,
                 capital_start,
                 capital_nature_start,
                 delta_business_value_start = 0):
        self.business_value     = business_value_start
        self.delta_business_value= delta_business_value_start
        self.capital            = capital_start  # mrd euro
        self.capital_nature     = capital_nature_start
        self.capital_business   = self.capital-self.capital_nature
        self.saldo_nature       = 0.0
        self.co2_consumption    = 0.0
        self.co2_intensity      = 0.0
        self.delta_co2_intensity = 0.0
        self.delta_co2_intensity_history = []
        self.nature_power             = 0.1
        self.market_influence_nature  = 0.0

        self.is_co2_taxable = True
        if random.random() < 0.2:
            self.is_co2_taxable = False
        self.business_power = 0.0
        self.market_influence = 0.0
        self.delta_business_power = 0.0
        self.delta_market_influence = 0.0

        self.is_alive = True
        self.delta_capital = 0.0


        #self.is_applying = True

        self.budget_to_improve =   ( 0.0, #technology
                                     0.0  #marketing
                                     )

        self.journal={
            -1: {
                'business_value': float(self.business_value),
                'capital': float(self.capital),
            }
        }

    def log_to_journal(self, logId):
        self.journal[logId] = {}
        self.journal[logId]['business_value'] = float(self.business_value)
        self.journal[logId]['capital'] = float(self.capital)
        return self.journal