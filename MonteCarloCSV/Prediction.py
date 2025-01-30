class Prediction:
    def __init__(self, index, stdev, mean, perc50, perc70, perc85, perc95):
        self.index = index
        self.stdev = stdev
        self.mean = mean
        self.perc50 = perc50
        self.perc70 = perc70
        self.perc85 = perc85
        self.perc95 = perc95


    def to_dict(self):
        return {
            'index': int(self.index),
            'stdev': float(self.stdev),
            'mean': float(self.mean),
            'perc50': float(self.perc50),
            'perc70': float(self.perc70),
            'perc85': float(self.perc85),
            'perc95': float(self.perc95),
        }