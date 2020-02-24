'''
The drug module. 
'''
import random
import math


class Drugs():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def grabbed_it(self, slotnum, identi, drug, initial, guild_id):
        self.cursor.execute(
            f"UPDATE drugs SET slot{slotnum}='{drug}', inv{slotnum}='{initial}' WHERE identi='{identi}';\nUPDATE guild_tables SET is_spawned=0, spawn_time=ADDTIME(NOW(), '00:0{random.randint(8,12)}:00') WHERE identi='{guild_id}'")
        return f"Congratulations, <@{identi}>! You were the first to grab the {initial}.\nThe drug has been added to inventory slot {slotnum}."

    def grab(self, identi, drug, initial, guild_id):
        '''
        Sees if a user can grab a drug.\n
        'identi' should be the user's id number.\n
        'drug' should be a should be the drug that spawned.\n
        'initial' should be a should be the displayed drug that spawned.\n
        'guild_id' should be the server on which the command was executed on.\n
        Returns a generated message.
        '''
        self.cursor.execute(
            f"SELECT slot1, slot2, slot3 FROM drugs WHERE identi='{identi}';")
        slots = self.cursor.fetchone()
        self.cursor.execute(
            f"SELECT is_spawned FROM guild_tables WHERE identi='{guild_id}';")
        if self.cursor.fetchone()[0] == 1:
            if slots[0] == 'None':
                return self.grabbed_it("1", identi, drug, initial, guild_id)
            elif slots[1] == 'None':
                return self.grabbed_it("2", identi, drug, initial, guild_id)
            elif slots[2] == 'None':
                return self.grabbed_it("3", identi, drug, initial, guild_id)
            else:
                return f"<@{identi}>, you have no open inventory slots and thus cannot grab a suspicious substance!"
        else:
            return f"<@{identi}>, there is no suspicious substance to grab at this time!"

    def use(self, identi, slotnum):
        '''
        Uses the drug of a user.\n
        'identi' should be the user's id number.\n
        'slotnum' should be the inventory slot they specified.\n
        Returns a generated message.
        '''
        self.cursor.execute(
            f"SELECT slot{slotnum}, bust_counter, inv{slotnum} FROM drugs WHERE identi='{identi}';")
        slot = self.cursor.fetchone()
        if slotnum != 1 and slotnum != 2 and slotnum != 3:
            return f"<@{identi}>, you can only use suspicious substances from inventory slots 1, 2, and 3."
        elif slot[0] == 'None':
            return f"<@{identi}>, you own no suspicious substance at inventory slot {slotnum}."
        else:
            cop_bust = random.randint(1, 10)
            if cop_bust >= 1 and cop_bust <= slot[1]:
                bust_amount = 0
                for i in range(40):
                    bust_amount += random.randint(0, 1)
                bust_amount /= 100
                self.cursor.execute(
                    f"SELECT bal, bank FROM balances WHERE identi='{identi}';")
                bal_bank = self.cursor.fetchone()
                if bal_bank[0] >= 0:
                    lostbal = round(bust_amount*bal_bank[0])
                else:
                    lostbal = -round(bust_amount*bal_bank[0])
                lostbank = -round(bust_amount*bal_bank[1])
                self.cursor.execute(f"UPDATE balances SET bal=bal-{lostbal}, bank=bank-{lostbank} WHERE identi='{identi}';\n"
                                    f"UPDATE drugs SET bust_counter=bust_counter+{random.randint(1,2)} WHERE identi='{identi}';")
                bal_bank = self.cursor.fetchone()
                return f'<@{identi}>, the police busted in and arrested you before you could use your suspicious substance!\nA fine of ${lostbal:,} was taken from your balance (now ${bal_bank[0]-lostbal}) and ${lostbank:,} from your bank (now ${bal_bank[1]-lostbank:,}).'
            else:
                self.cursor.execute(
                    f"UPDATE drugs SET slot{slotnum}='None', inv{slotnum}='None', current_drug='{slot[0]}', bust_counter=bust_counter+{random.randint(1,2)} WHERE identi='{identi}';")
                if "white" in slot[0]:
                    return f'<@{identi}>, you take in your {slot[2]}!\nYou can feel the {slot[2]} affecting your chances with Lootbox Zs.'
                elif "crystalline" in slot[0]:
                    return f'<@{identi}>, you take in your {slot[2]}!\nYou can feel the {slot[2]} affecting your chances with bets on a.'

    def destroy(self, identi, slotnum):
        '''
        Destroys the drug of a user.\n
        'identi' should be the user's id number.\n
        'slotnum' should be the inventory slot of to destroy.\n
        Returns a generated message.
        '''
        self.cursor.execute(
            f"SELECT slot{slotnum} FROM drugs WHERE identi='{identi}';")
        if slotnum != 1 and slotnum != 2 and slotnum != 3:
            return f"<@{identi}>, you can only destroy suspicious substances from inventory slots 1, 2, and 3."
        elif self.cursor.fetchone()[0] == 'None':
            return f"<@{identi}>, you own no suspicious substance at inventory slot {slotnum}."
        else:
            self.cursor.execute(
                f"UPDATE drugs SET bust_counter=bust_counter-{random.randint(1,2)}, slot{slotnum}='None', inv{slotnum}='None' WHERE identi='{identi}';")
            return f'<@{identi}>, you successfully destroyed your suspicious substance at inventory slot {slotnum}.'

    def inventory(self, identi):
        '''
        Gets the inventory of a user.\n
        'identi' should be the user's id number.\n
        Returns nested dictionaries.\n
        First keys are "Slot 1", "Slot 2", and "Slot 3".\n
        Nested keys are "inv1", "inv2", etc.\n
        '''
        self.cursor.execute(
            f"SELECT inv1, inv2, inv3 FROM drugs WHERE identi='{identi}';")
        inv = self.cursor.fetchone()
        return {"Slot 1": inv[0], "Slot 2": inv[1], "Slot 3": inv[2]}

    def shop(self, identi, page_num):
        '''
        Returns an enumerated version of the shop.\n
        For every tuple the items' shop number is at index 0,\n
        and the next item (another tuple at index 1) has the information on the item.\n
        User's ID is at index 0, the actual drug at index 1,\n
        the drug to display at index 2, the price at index 3,\n
        and the unique item id at index 4.
        Returns False if the length of the shop is less than 0.
        '''
        self.cursor.execute("SELECT * FROM shop;")
        shop = [item for item in enumerate(self.cursor.fetchall(), 1)]
        maxlen = math.ceil(len(shop)/25)
        if maxlen == 0:
            maxlen = 1
        if page_num > maxlen:
            return f"<@{identi}>, the page number you entered ({page_num}) is greater than the total pages in the shop ({maxlen})."
        dataset = shop[25*(page_num-1):25*page_num]
        return dataset

    def list_drug(self, identi, slotnum, price):
        '''
        Sells the drug of a user and adds it to the shop.\n
        'identi' should be the user's id number.\n
        'slotnum' should be the inventory slot of to list.\n
        'price' should be the amount the user is trying to sell it for.\n
        Returns a generated message.
        '''
        if slotnum != 1 and slotnum != 2 and slotnum != 3:
            return f"<@{identi}>, you can only list suspicious substances from inventory slots 1, 2, and 3."
        fee = round(0.1*price)
        self.cursor.execute(
            f"SELECT slot{slotnum}, inv{slotnum}, bal FROM drugs JOIN balances ON drugs.identi=balances.identi WHERE drugs.identi='{identi}';")
        slot_inv_bal = self.cursor.fetchone()
        if slot_inv_bal[0] == 'None':
            return f"<@{identi}>, you own no suspicious substance at inventory slot {slotnum}."
        elif price < 0:
            return f"<@{identi}>, you can't sell a suspicious substance for negative money!"
        elif fee > slot_inv_bal[2]:
            return f'<@{identi}>, the fee for selling that suspicious substance (${fee:,}) exceeds your current funds (${slot_inv_bal[2]:,})!'
        else:
            self.cursor.execute(f"UPDATE balances SET bal=bal-{fee} WHERE identi='{identi}';\n"
                                f"UPDATE drugs SET slot{slotnum}='None', inv{slotnum}='None' WHERE identi='{identi}';\n"
                                f"INSERT INTO shop (identi, actual_drug, displayed_drug, price) VALUES ('{identi}', '{slot_inv_bal[0]}', '{slot_inv_bal[1]}', {price});")
            return f'<@{identi}>, you have successfully listed your {slot_inv_bal[1]} at inventory slot {slotnum} for ${price:,}. A fee of ${fee:,} was deducted from your balance, which is now ${slot_inv_bal[2]:,}.'

    def unlisted_it(self, identi, item, slotnum):
        self.cursor.execute(
            f"UPDATE drugs SET slot{slotnum}='{item[1]}', inv{slotnum}='{item[2]}' WHERE identi='{identi}';")
        self.cursor.execute(f"DELETE FROM shop WHERE shop_id={item[4]}")
        return f"<@{identi}>, you successfully unlisted your {item[2]} off of the market. It is now at inventory slot {slotnum}."

    def unlist_drug(self, identi, shopnum):
        #identi (0), actual_drug (1), displayed_drug (2), price (3), shopid (4)
        '''
        Removes a drug from the shop.\n
        'identi' should be the user's id number.\n
        'shopnum' should be the shop number of the item they are unlisting.\n
        Returns a generated message.
        '''
        self.cursor.execute("SELECT * FROM shop;")
        shop = self.cursor.fetchall()
        shopnum -= 1
        try:
            item = shop[shopnum]
        except IndexError:
            return f"<@{identi}>, {shopnum+1} is not a valid shop number to unlist."
        if item[0] != identi:
            return f"<@{identi}>, the item at {shopnum+1} is not owned by you!"
        else:
            self.cursor.execute(
                f"SELECT slot1, slot2, slot3 FROM drugs WHERE identi='{identi}';")
            slots = self.cursor.fetchone()
            if slots[0] == 'None':
                return self.unlisted_it(identi, item, 1)
            elif slots[1] == 'None':
                return self.unlisted_it(identi, item, 2)
            elif slots[2] == 'None':
                return self.unlisted_it(identi, item, 3)
            else:
                return f"<@{identi}>, you have no open inventory slots and thus cannot unlist a suspicious substance!"

    def add_drug(self, identi, slotnum, item):
        self.cursor.execute(f"UPDATE drugs SET inv{slotnum}='{item[2]}', slot{slotnum}='{item[1]}' WHERE identi='{identi}';\n"
                            f"DELETE FROM shop WHERE shop_id = {item[4]};\n"
                            f"SELECT bal FROM balances WHERE identi='{identi}';")
        return f'<@{identi}>, you successfully bought {item[2]} off of the black market for ${item[3]:,}. It is now at inventory slot {slotnum}. Your balance is now ${self.cursor.fetchone()[0]:,}.'

    def buy(self, identi, itemnum):
        #identi (0), actual_drug (1), displayed_drug (2), price (3), shopid (4)
        '''
        Buys a drug off the market and gives it to the user.\n
        'identi' should be the user's id number.\n
        'itemnum' should be the shop number of the item to buy.\n
        Returns a generated message.
        '''
        self.cursor.execute(
            f"SELECT slot1, slot2, slot3, bal FROM drugs JOIN balances ON balances.identi=drugs.identi WHERE balances.identi='{identi}';")
        slots = self.cursor.fetchone()
        itemnum -= 1
        self.cursor.execute("SELECT * FROM shop;")
        shop = [item for item in self.cursor]
        try:
            item = shop[itemnum]
        except IndexError:
            return f"<@{identi}>, item {itemnum+1} does not exist in the shop."
        if item[3] > slots[3]:
            return f'<@{identi}>, the listed price of that suspicious substance (${item[3]:,}) exceeds your current balance (${slots[3]:,}).'
        elif item[0] == identi:
            return f"<@{identi}>, you cannot buy suspicious substances listed by yourself!"
        else:
            self.cursor.execute(f"UPDATE balances SET bal=bal-{item[3]} WHERE identi='{identi}';\n"
                                f"UPDATE balances SET bal=bal+{item[3]} WHERE identi='{item[0]}';")
            if slots[0] == 'None':
                return self.add_drug(identi, 1, item)
            elif slots[1] == 'None':
                return self.add_drug(identi, 2, item)
            elif slots[2] == 'None':
                return self.add_drug(identi, 3, item)
            else:
                return f"<@{identi}>, you have no open inventory slots and thus cannot buy a suspicious substance!"

    def return_inspect(self, identi):
        '''
        Returns the remaining time before the user's\n
        inspection cost is reset (in seconds) and the current price of inspection.\n
        'identi' should be the user's id number.\n
        The data are at indexes 0 and 1, respectively.
        '''
        self.cursor.execute(
            f"SELECT TIMESTAMPDIFF(SECOND, NOW(), (SELECT inspect_time FROM drugs WHERE identi = '{identi}')), inspect_counter FROM drugs WHERE identi='{identi}';")
        info = self.cursor.fetchone()
        if info[0] <= 0:
            self.cursor.execute(
                f"UPDATE drugs SET inspect_counter=0 WHERE identi='{identi}';")
            return (0, 150)
        else:
            return (info[0], 150*10**info[1])

    def inspect(self, identi, slotnum):
        '''
        Inspects the drug of a user.\n
        'identi' should be the user's id number.\n
        'slotnum' should be the inventory slot number of which the user is inspecting.\n
        Returns a generated message.
        '''
        try:
            slotnum = int(slotnum)
        except:
            return f"<@{identi}>, you have have one or more incorrect arguments for '/inspect'. Use '/help inspect' for more information on how to use it."
        if slotnum != 1 and slotnum != 2 and slotnum != 3:
            return f"<@{identi}>, '{slotnum}' is an invalid inventory slot to inspect."
        self.cursor.execute(
            f"SELECT slot{slotnum}, bal, inv{slotnum} FROM drugs JOIN balances ON drugs.identi=balances.identi WHERE drugs.identi = '{identi}';")
        info = self.cursor.fetchone()
        drug = info[2]
        time_cost = self.return_inspect(identi)
        if time_cost[0] <= 0:
            self.cursor.execute(
                f"UPDATE drugs SET inspect_time=ADDTIME(NOW(), '02:00:00'), inspect_counter=0 WHERE identi='{identi}';")
        if time_cost[1] > info[1]:
            return f"<@{identi}>, the cost of inspection (${time_cost[1]:,}) exceeds your current funds (${info[1]:,})!"
        elif drug == 'None':
            return f"<@{identi}>, you have no suspicious substance to inspect at that inventory slot!"
        elif "disgusting" in drug or "crummy" in drug or "regular" in drug or "luxurious" in drug:
            return f"<@{identi}>, you already know the quality of that drug!"
        else:
            self.cursor.execute(f"UPDATE balances SET bal=bal-{time_cost[1]} WHERE identi='{identi}';\n"
                                f"UPDATE drugs SET inv{slotnum}=slot{slotnum}, inspect_counter=inspect_counter+1 WHERE identi='{identi}';")
            return f'<@{identi}>, you successfully identified the suspicious substance at inventory slot {slotnum} for ${time_cost[1]:,}, which turned out to be a {info[0]}! Your new balance is now ${info[1]-time_cost[1]:,}.'

    def reveal(self, identi):
        '''
        Reveals the types of drugs of a user's inventory.\n
        'identi' should be the user's id number.\n
        Returns a generated message.
        '''
        self.cursor.execute(
            f"SELECT inv1, inv2, inv3, slot1, slot2, slot3 FROM drugs WHERE identi='{identi}';")
        info = self.cursor.fetchone()
        inv1 = info[0]
        inv2 = info[1]
        inv3 = info[2]
        slot1 = info[3]
        slot2 = info[4]
        slot3 = info[5]
        if slot1 == 'None' or slot2 == 'None' or slot3 == 'None':
            return f"<@{identi}>, you can only reveal drugs if all three of your inventory slots are occupied by drugs!"
        elif "disgusting" in inv1 or "crummy" in inv1 or "regular" in inv1 or "luxurious" in inv1 or "disgusting" in inv2 or "crummy" in inv2 or "regular" in inv2 or "luxurious" in inv2 or "disgusting" in inv3 or "crummy" in inv3 or "regular" in inv3 or "luxurious" in inv3:
            return f"<@{identi}>, you cannot attempt to reveal your inventory while you know the quality of a drug in your inventory!"
        else:
            disg = ['d' for drug_str in [
                slot1, slot2, slot3] if 'disg' in drug_str]
            crum = ['c' for drug_str in [
                slot1, slot2, slot3] if 'crum' in drug_str]
            reg = ['r' for drug_str in [
                slot1, slot2, slot3] if 'reg' in drug_str]
            lux = ['l' for drug_str in [
                slot1, slot2, slot3] if 'lux' in drug_str]
            return f"<@{identi}>, your inventory contains {len(disg)} disgusting, {len(crum)} crummy, {len(reg)} regular, and {len(lux)} luxurious suspicious substances."

    def calc_spawn(self, guild_id):
        '''
        Calculates if a drug should spawn for a server.\n
        'guild_id' should be the id of guild to check.\n
        Returns a boolean if you should spawn the drug.
        '''
        self.cursor.execute(
            f"SELECT TIMESTAMPDIFF(SECOND, NOW(), (SELECT spawn_time FROM guild_tables WHERE identi='{guild_id}')), is_spawned FROM guild_tables WHERE identi='{guild_id}';")
        checker = self.cursor.fetchone()
        if checker[0] < 0 and checker[1] == 0:
            return True
        else:
            return False
