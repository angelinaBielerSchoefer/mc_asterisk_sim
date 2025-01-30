class Needle:
    def __init__(self, x, y):
        self.x = x
        self.y= y
        self.inCircle = 0

    def setInCircle(self, inCircle = True):
        if inCircle == True:
            self.inCircle = 1
        return self

    def to_dict(self):
        return {
            'x': float(self.x),
            'y': float(self.y),
            'inCircle': self.inCircle
        }