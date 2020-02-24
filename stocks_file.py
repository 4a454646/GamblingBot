import random


class Stocks():
    change_counter = 0
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def super_decrease(self):
        return [random.randint(25,50) if random.randint(1,3)==1 else random.randint(-100, -50) for i in range(random.randint(3,5))]

    def slight_decrease(self):
        return [random.randint(-10,10) if random.randint(1,3)==1 else random.randint(-50, -25) for i in range(random.randint(3,5))]

    def stable(self):
        return [random.randint(-10,10) for i in range(random.randint(3,5))]

    def slight_increase(self):
        return [random.randint(-10,10) if random.randint(1,3)==1 else random.randint(25, 50) for i in range(random.randint(3,5))]

    def super_increase(self):
        return [random.randint(-50,-25) if random.randint(1,3)==1 else random.randint(50,100) for i in range(random.randint(3,5))]

    change_list = [super_decrease, super_decrease, slight_decrease, slight_decrease, slight_decrease, stable, stable, slight_increase, slight_increase, slight_increase, super_increase, super_increase]

    def rand_change(self):
        return random.choice(self.change_list)(self)
