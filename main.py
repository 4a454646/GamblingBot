'''
Contains the main that will be inherited throughout the code.\n
'''


class Main():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def total(self, identi):
        '''
        Calculates the total balance of a user.\n
        This includes their balance, bank, and any investments.\n
        'identi' should be the user/guild's id number.\n
        REMEMBER TO UDPATE THIS WHEN STOCKS BECOME A THING!
        '''
        self.cursor.execute(f"SELECT bal, bank, URBAD, TSLA, MNCFT, DANK, OOF FROM balances JOIN stocks on balances.identi=stocks.identi WHERE balances.identi='{identi}';")
        info = self.cursor.fetchone()
        self.cursor.execute(f"SELECT URBAD_after, TSLA_after, MNCFT_after, DANK_after, OOF_after FROM stock_prices;")
        prices = self.cursor.fetchone()
        return info[0] + info[1] + info[2] * prices[0] + info[3] * prices[1] + info[4] * prices[2] + info[5] * prices[3] + info[6] * prices[4]

    def sort_totals(self, asc_or_desc, urbad_price, tsla_price, mncft_price, dank_price, oof_price):
        '''
        Sorts the data by total assets.\n
        'identi' should be the user/guild's id number.\n
        'limit_str' should be something like " LIMIT 5" (space included).\n
        'asc_or_desc' should be the way you want to sort it by (ascending or descending).\n
        '[stock]_price' should be the stock's current price as of now.\n
        Returns a tuplet with a list of ids at index 0 and a sum of total assets at index 1.\n
        Each id has the corresponding sum at the same index.
        '''
        self.cursor.execute(f"WITH test as (SELECT balances.identi AS identi, bal+bank+URBAD*{urbad_price}+TSLA*{tsla_price}+MNCFT*{mncft_price}+DANK*{dank_price}+OOF*{oof_price} as total FROM balances JOIN stocks ON balances.identi = stocks.identi) SELECT identi, total FROM test ORDER BY total {asc_or_desc};")
        tuplets = self.cursor.fetchall()
        return ([tuplet[0] for tuplet in tuplets], [tuplet[1] for tuplet in tuplets])

    def pay(self, identi, recipient_id, amount):
        self.cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';")
        curbal = self.cursor.fetchone()[0]
        if amount <= 0:
            return f"<@{identi}>, that is an invalid amount of money to pay. Please only enter positive integers."
        elif curbal < amount:
            return f"<@{identi}>, the amount of money that you are trying to pay (${amount:,}) exceeds your current balance (${curbal:,})"
        elif identi == recipient_id:
            return f"<@{identi}>, what's the point of sending money to yourself?"
        else:
            self.cursor.execute(f"UPDATE balances SET bal=bal-{amount} WHERE identi='{identi}';")
            self.cursor.execute(f"UPDATE balances SET bal=bal+{amount} WHERE identi='{recipient_id}';")
            self.cursor.execute(f"SELECT bal FROM balances WHERE identi='{recipient_id}';")
            return f'<@{identi}>, you successfully sent ${amount:,} to <@{recipient_id}>. Your balances are now ${curbal-amount:,} and ${self.cursor.fetchone()[0]:,}, respectively.'

    def deposit(self, identi, amount):
        self.cursor.execute(f"SELECT bal, bank FROM balances WHERE identi='{identi}';")
        bal_bank = self.cursor.fetchone()
        try: amount = int(amount)
        except:
            if amount == "all" or amount == "max": amount = bal_bank[0]
            else: return f"<@{identi}>, you passed in an incorrect argument for '/deposit'. Use '/help deposit' for more information on how to use it."
        if bal_bank[0] < amount:
            return f"<@{identi}>, the amount you are trying to deposit (${amount:,}) exceeds your current funds (${bal_bank[0]:,})!"
        elif amount <= 0:
            return f"<@{identi}>, you cannot deposit a negative or zero amount of money!"
        else:
            self.cursor.execute(f"UPDATE balances SET bal=bal-{amount}, bank=bank+{amount} WHERE identi='{identi}';")
            return f'<@{identi}>, you successfully deposited ${amount:,} into your bank account. Your balance is now ${bal_bank[0]-amount:,} and your bank balance is now ${bal_bank[1]+amount:,}.'

    def withdraw(self, identi, amount):
        self.cursor.execute(f"SELECT bal, bank FROM balances WHERE identi='{identi}';")
        bal_bank = self.cursor.fetchone()
        try: amount = int(amount)
        except:
            if amount == "all" or amount == "max": amount = bal_bank[1]
            else: return f"<@{identi}>, you passed in an incorrect argument for '/withdraw'. Use '/help withdraw' for more information on how to use it."
        if bal_bank[1] < amount:
            return f"<@{identi}>, the amount you are trying to withdraw (${amount:,}) exceeds your current funds (${bal_bank[1]:,})!"
        elif amount <= 0:
            return f"<@{identi}>, you cannot withdraw a negative or zero amount of money!"
        else:
            self.cursor.execute(f"UPDATE balances SET bank=bank-{amount}, bal=bal+{amount} WHERE identi='{identi}';")
            return f'<@{identi}>, you successfully withdrew ${amount:,} from your bank account. Your balance is now ${bal_bank[0]+amount:,} and your bank balance is now ${bal_bank[1]-amount:,}.'