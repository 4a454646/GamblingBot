'''
DOSCTRING HERE
'''
import random

#remember to create a table for the stats!

class Gambling():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def assemble_send(self, identi, money_won, times, curdrug, letter, curbal):
        if times > 1:
            s = "s"
        else:
            s = ""
        if money_won >= 0:
            send = f"<@{identi}>, you won ${money_won:,} from your {times} bet{s} on {letter}! Your new balance is ${curbal+money_won:,}."
        else:
            send = f"<@{identi}>, you lost ${abs(money_won):,} from your {times} bet{s} on {letter}! Your new balance is ${curbal+money_won:,}."
        if "disgusting" in curdrug:
            send += f"\nYou felt the {curdrug} greatly harm your chances."
        elif "crummy" in curdrug:
            send += f"\nYou felt the {curdrug} slightly harm your chances."
        elif "regular" in curdrug:
            send += f"\nYou felt the {curdrug} slightly help your chances."
        elif "luxurious" in curdrug:
            send += f"\nYou felt the {curdrug} greatly help your chances."
        else:
            pass
        return send
    
    def bet(self, identi, money, letter, times):
        try: times = int(times)
        except: return f"<@{identi}>, you have have one or more incorrect arguments for '/bet'. Use '/help bet' for more information on how to use it."
        self.cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';")
        curbal = self.cursor.fetchone()[0]
        try: money = int(money)
        except:
            if money == "all" or money == "max":
                money = curbal
            else:
                 return f"<@{identi}>, you have have one or more incorrect arguments for '/bet'. Use '/help bet' for more information on how to use it."
        if letter == 'd':
            if money % 10 != 0:
                return f"<@{identi}>, you can only bet multiples of 10 when betting on d."
            total_cost = int(money/10*times)
        else:
            total_cost = money*times
        if letter != 'a' and letter != 'b' and letter != 'c' and letter != 'd':
            return f"<@{identi}>, '{letter}' is an invalid letter to bet on. Use '/help bets' for more information on betting."
        elif times > 3:
            return f"<@{identi}>, you can only bet 3 times at once."
        elif times <= 0:
            return f"<@{identi}>, you can't bet 0 or less than 0 times!"
        elif total_cost <= 0:
            return f"<@{identi}>, you can't bet for 0 or negative amounts of money!"
        elif total_cost > curbal:
            return f"<@{identi}>, the total cost of those bets (${total_cost:,}) exceeds your current funds (${curbal:,})!"
        else:
            self.cursor.execute(f"SELECT current_drug FROM drugs WHERE identi='{identi}';")
            curdrug = self.cursor.fetchone()[0]
            money_won = 0
            if letter == 'a':
                if "crystalline" in curdrug:
                    num_list = []
                    for num in range(times):
                        if "disgusting" in curdrug:
                            if random.randint(1,3) == 1:
                                num_list.append((2, 1+1/3))
                        if "crummy" in curdrug:
                            if random.randint(1,6) == 1:
                                num_list.append((2, 1+1/6))
                        if "regular" in curdrug:
                            if random.randint(1,7) == 1:
                                num_list.append((1, 1+1/7))
                        if "luxurious" in curdrug:
                            if random.randint(1,4) == 1:
                                num_list.append((1, 1+1/4))
                        if len(num_list) < times:
                            for i in range(times-len(num_list)):
                                num_list.append((random.randint(1,2), 1))
                    self.cursor.execute(f"UPDATE drugs SET current_drug='None' WHERE identi='{identi}';")
                else:
                    num_list = [(random.randint(1,2), 1) for num in range(times)]
                for tuplet in num_list:
                    if tuplet[0] == 1:
                        money_won += round(money*tuplet[1])
                    else:
                        money_won -= round(money*tuplet[1])
                self.cursor.execute(f"UPDATE balances SET bal=bal+{money_won} WHERE identi='{identi}';")
                return self.assemble_send(identi, money_won, times, curdrug, letter, curbal)
            elif letter == 'b':
                num_list = [(random.randint(1,2), 1) for num in range(times)]
                for tuplet in num_list:
                    if tuplet[0] == 1:
                        money_won += round(money*tuplet[1])
                    else:
                        money_won -= round(money*tuplet[1])
                self.cursor.execute(f"UPDATE balances SET bal=bal+{money_won} WHERE identi='{identi}';")
                return self.assemble_send(identi, money_won, times, curdrug, letter, curbal)
            elif letter == 'c':
                num_list = [(random.randint(1,20), 1) for num in range(times)]
                for tuplet in num_list:
                    if tuplet[0] == 1:
                        money_won += round(money*20*tuplet[1])
                    else:
                        money_won -= round(money*tuplet[1])
                self.cursor.execute(f"UPDATE balances SET bal=bal+{money_won} WHERE identi='{identi}';")
                return self.assemble_send(identi, money_won, times, curdrug, letter, curbal)
            elif letter == 'd':
                num_list = [(random.randint(1,10), 1) for num in range(times)]
                for tuplet in num_list:
                    if tuplet[0] == 1:
                        money_won += round(money*tuplet[1])
                    else:
                        money_won -= round(money*tuplet[1]*0.1)
                self.cursor.execute(f"UPDATE balances SET bal=bal+{money_won} WHERE identi='{identi}';")
                return self.assemble_send(identi, money_won, times, curdrug, letter, curbal)