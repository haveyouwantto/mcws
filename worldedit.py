
class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other):
        return (1 + abs(self.x - other.x)) * (1 + abs(self.y - other.y)) * (1 + abs(self.z - other.z))

    def __str__(self):
        return "[Position x={0} y={1} z={2}]".format(self.x, self.y, self.z)
