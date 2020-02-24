'''
DOSCTRING HERE
'''
import random

#remember to create a table for the stats!

class Lootbox():
    cost_dict = {"z1":50, "z2":75, "z3":100, "y1":25, "y2":50, "y3":75}
    drug_qualities = ["disgusting ", "disgusting ", "crummy ", "regular ", "luxurious "]
    drug_names = ["suspicious white powder", "suspicious crystalline substance"]
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def assemble_send(self, identi, money_won, number, curdrug, letter, num, curbal):
        if number > 1:
            s = "s"
        else:
            s = ""
        if money_won >= 0:
            send = f"<@{identi}>, you won ${money_won:,} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}."
        else:
            send = f"<@{identi}>, you lost ${abs(money_won):,} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}."
        if "disgusting" in curdrug:
            send += f"\nYou felt the {curdrug} greatly harm your chances."
        if "crummy" in curdrug:
            send += f"\nYou felt the {curdrug} slightly harm your chances."
        if "regular" in curdrug:
            send += f"\nYou felt the {curdrug} slightly help your chances."
        if "luxurious" in curdrug:
            send += f"\nYou felt the {curdrug} greatly help your chances."
        return send

    def lootbox_gen(self, number):
        num_list = []
        for i in range(number):
            multiplier = -10
            for i in range(25):
                multiplier += random.uniform(0, 0.8)
            if multiplier > 0: multiplier += 1
            elif multiplier < 0: multiplier -= 1
            num_list.append(multiplier)
        return num_list

    def between(self, num, a, b):
        if num >= a and num <= b:
            return True

    def add_winnings(self, identi, money_won, won_list):
        self.cursor.execute(f"UPDATE balances SET bal=bal+{money_won} WHERE identi='{identi}';")
        return_info = []
        for initial, drug in won_list:
            self.cursor.execute(f"SELECT slot1, slot2, slot3 FROM drugs WHERE identi='{identi}';")
            slots = self.cursor.fetchone()
            if slots[0] == 'None':
                self.cursor.execute(f"UPDATE drugs SET inv1='{initial}', slot1='{drug}' WHERE identi='{identi}';")
                return_info.append("(now at inventory slot 1)")
            elif slots[1] == 'None':
                self.cursor.execute(f"UPDATE drugs SET inv2='{initial}', slot2='{drug}' WHERE identi='{identi}';")
                return_info.append("(now at inventory slot 2)")
            elif slots[2] == 'None':
                self.cursor.execute(f"UPDATE drugs SET inv3='{initial}', slot3='{drug}' WHERE identi='{identi}';")
                return_info.append("(now at inventory slot 3)")
            else:
                return_info.append("(failed to add)")
        return return_info

    def y_gen(self, identi, money_won, won_list, number, letter, num, curbal, total_cost):
        if number > 1:
            s = "s"
        else:
            s = ""
        money_won -= total_cost
        add_info = self.add_winnings(identi, money_won, won_list)
        if "(failed to add)" in add_info:
            add_str = " One or more of your rewards could not be added to your inventory. It's best practice to leave some inventory slots open while opening Lootbox Ys."
        else:
            add_str = ""
        if money_won >= 0:
            if len(won_list) == 0:
                return f"<@{identi}>, you won ${money_won:,} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." + add_str
            elif len(won_list) == 1:
                return f"<@{identi}>, you won ${money_won:,} and {won_list[0][0]} {add_info[0]} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." + add_str
            elif len(won_list) == 2:
                return f"<@{identi}>, you won ${money_won:,}, {won_list[0][0]} {add_info[0]}, and {won_list[1][0]} {add_info[1]} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." 
            elif len(won_list) == 3:
                return f"<@{identi}>, you won ${money_won:,}, {won_list[0][0]} {add_info[0]}, {won_list[1][0]} {add_info[1]}, and {won_list[2][0]} {add_info[2]} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." + add_str
        else: 
            if len(won_list) == 0:
                return f"<@{identi}>, you lost ${abs(money_won):,} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." + add_str
            elif len(won_list) == 1:
                return f"<@{identi}>, you lost ${abs(money_won):,}, but won a {won_list[0][0]} {add_info[0]} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." + add_str
            elif len(won_list) == 2:
                return f"<@{identi}>, you lost ${abs(money_won):,}, but won a {won_list[0][0]} {add_info[0]} and a {won_list[1][0]} {add_info[1]} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." 
            elif len(won_list) == 3:
                return f"<@{identi}>, you lost ${abs(money_won):,}, but won a {won_list[0][0]} {add_info[0]}, a {won_list[1][0]} {add_info[1]}, and a {won_list[2][0]} {add_info[2]} from your {number} lootbox {letter+num} purchase{s}! Your new balance is ${curbal+money_won:,}." + add_str

    def lootbox(self, identi, letter, num, number):
        try: number = int(number)
        except: return f"<@{identi}>, you can only purchase integer number of lootboxes."
        self.cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';")
        curbal = self.cursor.fetchone()[0]
        if letter != "z" and letter != "y" and num != "1" and num != "2" and num != "3":
            return f"<@{identi}>, '{letter+num}' is an invalid lootbox to purchase. Use '/help lootbox' for more information on lootboxes."
        cost = self.cost_dict[letter+num]
        total_cost = cost*number
        if number > 3:
            return f"<@{identi}>, you can only purchase 3 lootboxes at a time!"
        elif number <= 0:
            return f"<@{identi}>, you can't buy 0 or less than 0 lootboxes!"
        elif total_cost > curbal:
            return f"<@{identi}>, the total cost of those purchases (${total_cost:,}) exceeds your current funds (${curbal:,})!"
        else:
            self.cursor.execute(f"SELECT current_drug FROM drugs WHERE identi='{identi}';")
            curdrug = self.cursor.fetchone()[0]
            money_won = 0
            if letter == 'z':
                if "white" in curdrug:
                    num_list = self.lootbox_gen(number)
                    for multiplier in num_list:
                        if "disgusting" in curdrug:
                            if random.randint(1,3) == 1:
                                num_list[num_list.index(multiplier)] = -abs(multiplier)*(1+1/3)
                        if "crummy" in curdrug:
                            if random.randint(1,6) == 1:
                                num_list[num_list.index(multiplier)] = -abs(multiplier)*(1+1/6)
                        if "regular" in curdrug:
                            if random.randint(1,6) == 1:
                                num_list[num_list.index(multiplier)] = abs(multiplier)*(1+1/7)
                        if "luxurious" in curdrug:
                            if random.randint(1,4) == 1:
                                num_list[num_list.index(multiplier)] = abs(multiplier)*(1+1/4)
                    self.cursor.execute(f"UPDATE drugs SET current_drug='None' WHERE identi='{identi}';")
                    for multiplier in num_list:
                        money_won += cost*multiplier
                else:
                    num_list = self.lootbox_gen(number)
                    for multiplier in num_list:
                        money_won += cost*multiplier
                money_won = round(money_won)
                self.cursor.execute(f"UPDATE balances SET bal=bal+{money_won} WHERE identi='{identi}';")
                return self.assemble_send(identi, money_won, number, curdrug, letter, num, curbal)
            elif letter == 'y':
                won_list = []
                money_won = 0
                if num == "1":
                    for i in range(number):
                        randnum = random.randint(1,10)
                        if self.between(randnum, 1, 4):
                            money_won += 50
                        elif self.between(randnum, 5, 5):
                            name = random.choice(self.drug_names)
                            won_list.append(("disgusting " + name, "disgusting " + name))
                    return self.y_gen(identi, money_won, won_list, number, letter, num, curbal, total_cost)
                elif num == "2":
                    for i in range(number):
                        randnum = random.randint(1, 20)
                        if self.between(randnum, 1, 8):
                            money_won += 75
                        elif self.between(randnum, 9, 10):
                            money_won += 150
                        elif self.between(randnum, 11, 11):
                            name = random.choice(self.drug_names)
                            won_list.append((name, random.choice(self.drug_qualities)+name))
                    return self.y_gen(identi, money_won, won_list, number, letter, num, curbal, total_cost)
                elif num == "3":
                    for i in range(number):
                        randnum = random.randint(1,20)
                        if self.between(randnum, 1, 8):
                            money_won += 100
                        elif self.between(randnum, 9, 10):
                            name = random.choice(self.drug_names)
                            won_list.append((name, random.choice(self.drug_qualities)+name))
                        elif self.between(randnum, 10, 11):
                            name = random.choice(self.drug_names)
                            won_list.append((name, "luxurious " + name))
                    return self.y_gen(identi, money_won, won_list, number, letter, num, curbal, total_cost)