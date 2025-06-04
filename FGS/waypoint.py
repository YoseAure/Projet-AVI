class Waypoint:
    def __init__(self, name: str, x, y, z, type):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.type = type

    def get_name(self):
        return self.name

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def get_z(self):
        return self.z
    
    def get_type(self):
        return self.type