import random


class Company:
    def __init__(self, business_value_start,
                 capital_start,
                 weight_nature):
        self.business_value = business_value_start
        self.capital = capital_start  # mrd euro
        self.capital_nature = weight_nature * self.capital
        self.capital_business = self.capital-self.capital_nature
        self.weight_business = 1- weight_nature
        self.weight_nature =  weight_nature

        self.co2_apply_free     = 0.0
        self.co2_emission       = 0.0
        self.co2_emission_idle  = 0.0
        self.co2_demand         = 0.0
        self.co2_intensity      = 0.0
        self.co2_supply         = 0.0
        self.co2_taxes          = 0.0

        #ASSUMPTION!!!!!
        random_taxable = random.randrange(0,1)
        if random_taxable > 0.2:
            self.co2_taxable = True
        else:
            self.co2_taxable = False

        self.business_power = 0.0
        self.market_influence = 0.0
        self.is_alive = True
        #self.invoice = {
        #    'free' : [(0,0)],
        #    'sale' : [(0,0)],
        #    'vcm'  : [(0,0)],
        #    'tax'  : [(0,0)]
        #}
        self.journal={
            -1: {
                'business_value': float(self.business_value),
                'capital': float(self.capital),
        #        'invoice':self.invoice
            }
        }

    def log_to_journal(self, logId):
        self.journal[logId] = {}
        self.journal[logId]['business_value'] = float(self.business_value)
        self.journal[logId]['capital'] = float(self.capital)
        #self.journal[logId]['invoice'] = self.invoice
        return self.journal