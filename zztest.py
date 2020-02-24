import random
def bell_creator():
    num = -100
    for i in range(40):
        num += random.randint(0,5)
    return num
nums = [bell_creator() for i in range(100000)]
print("Finished")