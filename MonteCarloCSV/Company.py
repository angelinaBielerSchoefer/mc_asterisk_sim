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

        #self.weight_nature      = self.capital_nature/self.capital
        self.capital_business   = self.capital-self.capital_nature
        #self.weight_business    = 1 - self.weight_nature
        self.saldo_nature       = 0.0

        self.co2_apply_free     = 0.0
        self.co2_consumption    = 0.0
        self.co2_emission       = 0.0
        self.co2_emission_idle  = 0.0
        self.co2_demand         = 0.0
        self.co2_intensity      = 0.0
        self.co2_correlation_factor = 0.0
        self.co2_remaining_stock= 0.0
        self.co2_subvention     = 0.0
        self.co2_supply         = 0.0
        self.co2_taxes          = 0.0

        self.nature_power             = 0.0
        self.market_influence_nature  = 0.0

        #ASSUMPTION!!!!!
        random_taxable = random.randrange(0,1)
        if random_taxable > 0.2:
            self.is_co2_taxable = True
        else:
            self.is_co2_taxable = False

        self.business_power = 0.0
        self.market_influence = 0.0

        self.is_alive = True
        self.is_applying = True

        self.budget_to_improve =   ( 0.0, #business_power
                                     0.0, #nature_power
                                     0.0, #co2_emission_idle
                                     0.0, #apply_free
                                     0.0) #buy_allowances

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