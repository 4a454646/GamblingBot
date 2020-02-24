import random
import sys
import math
import traceback
import asyncio
from difflib import SequenceMatcher
import MySQLdb
import discord
from discord.ext import commands as cmds
import config
import main
import drugs
import gambling
import lootboxes
import stocks_file
import helper
# make sure to import all the rest of your scripts here as well

connection = MySQLdb.connect(**config.database_config)
cursor = connection.cursor()
bot = cmds.Bot(command_prefix='/', activity=discord.Game("/help"))
client = discord.Client()
main = main.Main(connection)
drugs = drugs.Drugs(connection)
gambling = gambling.Gambling(connection)
lootboxes = lootboxes.Lootbox(connection)
stock = stocks_file.Stocks(connection)
drug_qualities = ["disgusting ", "disgusting ",
                  "crummy ", "regular ", "luxurious "]
drug_names = ["suspicious white powder", "suspicious crystalline substance"]
drug_urls = ["https://imgur.com/4b6FnFg.png",
             "https://i.imgur.com/hVahtyy.png"]
table_tuple = ("drugs", "balances", "stocks", "claims")
change_dict = {'URBAD': [], 'TSLA': [], 'MNCFT': [], 'DANK': [], 'OOF': []}


def similar(a, b):
    '''
    Returns a float of how close the strings of 'a' and 'b' are.
    '''
    return SequenceMatcher(None, a, b).ratio()


async def reset_busts():
    await bot.wait_until_ready()
    # asyncio.sleep(TIME UP UNTIL MIDNIGHT)
    while True:
        cursor.execute(f"UPDATE drugs SET bust_counter=0;")
        await asyncio.sleep(86400)
change_dict = {'URBAD': [], 'TSLA': [], 'MNCFT': [], 'DANK': [], 'OOF': []}


async def run_updater():
    await asyncio.sleep(4)
    print("updater successfully ran")
    while True:
        for (key, value) in change_dict.items():
            if len(value) == 0:
                change_dict[key] = stock.rand_change()
            cursor.execute(f"SELECT {key}_after FROM stock_prices;"
                           f"UPDATE stock_prices SET {key}_before={key}_after;\n"
                           f"UPDATE stock_prices SET {key}_after={key}_after+{change_dict[key][0]};")
            curprice = cursor.fetchone()[0]+change_dict[key][0]
            change_dict[key].pop(0)
            if random.randint(1, 10080) == 1:
                # split the stock
                cursor.execute(
                    f"UPDATE stock_prices SET {key}_after={math.floor(curprice/2)};\nUPDATE stocks SET {key}={key}*2;")
                print(f"{key} has split")
            if curprice <= 0:
                cursor.execute(f"UPDATE stock_prices SET {key}_after=55;")
        await asyncio.sleep(4)
stock_helper = {"URBAD": 1, "TSLA": 3, "MNCFT": 5, "DANK": 7, "OOF": 9}


async def send_stocks():
    await bot.wait_until_ready()
    stocks_channel = bot.get_channel(583140315641151508)
    while True:
        await stocks_channel.purge(limit=1)
        stock_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
        cursor.execute(f"SELECT * FROM stock_prices;")
        stock_prices = cursor.fetchone()
        for stock_name in stock_helper:
            if stock_prices[stock_helper[stock_name]] > stock_prices[stock_helper[stock_name]-1]:
                stock_embed.add_field(name=f"{stock_name} :chart_with_upwards_trend:",
                                      value=f"${stock_prices[stock_helper[stock_name]]:,} (+${stock_prices[stock_helper[stock_name]]-stock_prices[stock_helper[stock_name]-1]:,})", inline=True)
            elif stock_prices[stock_helper[stock_name]] < stock_prices[stock_helper[stock_name]-1]:
                stock_embed.add_field(name=f"{stock_name} :chart_with_downwards_trend:",
                                      value=f"${stock_prices[stock_helper[stock_name]]:,} (-${stock_prices[stock_helper[stock_name]-1]-stock_prices[stock_helper[stock_name]]:,})", inline=True)
            else:
                stock_embed.add_field(
                    name=f"{stock_name}", value=f"${stock_prices[stock_helper[stock_name]]:,} (+$0)", inline=True)
        stock_embed.add_field(name="\u200b", value=f"\u200b", inline=True)
        await stocks_channel.send(embed=stock_embed)
        await asyncio.sleep(8)

command_counter = {}
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

blocked_list = []
@bot.check
async def block_users(ctx):
    return ctx.author.id not in blocked_list


@bot.event
async def on_ready():
    print(f"Successful log in as {bot.user}.")


@bot.event
async def on_guild_join(guild):
    memberlist = [str(member.id) for member in guild.members]
    for memberid in memberlist:
        for table in table_tuple:
            try:
                cursor.execute(
                    f"INSERT INTO {table} (identi) VALUES ('{str(memberid)}');")
            except:
                print("user failed")
    cursor.execute(
        f"INSERT INTO guild_tables (identi, spawn_type) VALUES ('{str(guild.id)}', '');")


@bot.event
async def on_member_join(member):
    # make sure to update this when you add more tables
    memberid = member.id
    for table in table_tuple:
        cursor.execute(
            f"INSERT INTO {table} (identi) VALUES ({str(memberid)});")


@bot.event
async def on_command_error(ctx, error):
    identi = ctx.message.author.id
    cmd = ctx.message.content.split()[0]
    error = getattr(error, 'original', error)
    if hasattr(ctx.command, 'on_error'):
        return
    elif isinstance(error, cmds.MissingRequiredArgument) and identi not in blocked_list:
        await ctx.send(f"<@{identi}>, you are missing one or more arguments for '{cmd}'. Use '/help {cmd[1:]}' for more information on how to use it.")
    elif isinstance(error, cmds.BadArgument) and identi not in blocked_list:
        await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '{cmd}'. Use '/help {cmd[1:]}' for more information on how to use it.")
    elif isinstance(error, cmds.CommandNotFound) and identi not in blocked_list:
        await ctx.send(f"<@{identi}>, the command '{cmd}' was not found.")
    elif isinstance(error, cmds.CommandOnCooldown) and identi not in blocked_list:
        # if ctx.command.qualified_name == 'command name'
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if round(d) == 0 and round(h) == 0 and round(m) == 0:
            await ctx.send(f"<@{identi}>, you cannot use '{cmd}' at this time! Wait {round(s)}s.")
        elif round(d) == 0 and round(h) == 0:
            await ctx.send(f"<@{identi}>, you cannot use '{cmd}' at this time! Wait {round(m)}m {round(s)}s.")
        elif round(d) == 0:
            await ctx.send(f"<@{identi}>,you cannot use '{cmd}' at this time! Wait {round(h)}h {round(m)}m {round(s)}s.")
        else:
            await ctx.send(f"<@{identi}>, you cannot use '{cmd}' at this time! Wait {round(d)}d {round(h)}h {round(m)}m {round(s)}s.")
    elif isinstance(error, cmds.NoPrivateMessage):
        pass
    elif isinstance(error, cmds.CheckFailure):
        pass
    else:
        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_command(ctx):
    author_id = ctx.author.id
    if author_id not in blocked_list:
        if author_id not in command_counter:
            command_counter[author_id] = 1
            await asyncio.sleep(2)
            command_counter.pop(author_id)
        else:
            command_counter[author_id] += 1


@bot.command()
async def readd(ctx):
    if ctx.author.id == 341277715179110400:
        memberlist = [str(member.id) for member in bot.get_all_members()]
        for memberid in memberlist:
            for table in table_tuple:
                try:
                    cursor.execute(
                        f"INSERT INTO {table} (identi) VALUES ('{str(memberid)}');")
                except:
                    print('user fail')
        for guild in bot.guilds:
            try:
                cursor.execute(
                    f"INSERT INTO guild_tables (identi, spawn_type, member_count) VALUES ('{str(guild.id)}', '', {len(guild.members)});")
            except:
                print('guild fail')

#           #
#  Regular  #
#           #

@bot.command(aliases=["money", "balance"])
async def bal(ctx, *check):
    checked = ctx.guild.get_member_named(' '.join(check))
    if checked is not None:
        cursor.execute(
            f"SELECT bal FROM balances WHERE identi='{str(checked.id)}'")
        curbal = cursor.fetchone()[0]
        if curbal >= 0:
            await ctx.send(f'{str(checked)}\'s current balance is ${curbal:,}.')
        else:
            await ctx.send(f'{str(checked)}\'s current balance is -${abs(curbal):,}.')
    elif checked is None and len(check) > 0:
        await ctx.send(f"<@{str(ctx.message.author.id)}>, '{' '.join(check)}' is not a valid user. Check your spelling and capitalization.")
    else:
        identi = str(ctx.message.author.id)
        cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
        curbal = cursor.fetchone()[0]
        if curbal >= 0:
            await ctx.send(f'<@{identi}>, your current balance is ${curbal:,}.')
        else:
            await ctx.send(f'<@{identi}>, your current balance is -${abs(curbal):,}.')

@bot.command(aliases=["bankbal", "vault", "safe"])
async def bank(ctx, *check):
    checked = ctx.guild.get_member_named(' '.join(check))
    if checked is not None:
        cursor.execute(
            f"SELECT bank FROM balances WHERE identi='{str(checked.id)}'")
        await ctx.send(f'{str(checked)}\'s current bank balance is ${cursor.fetchone()[0]:,}.')
    elif checked is None and len(check) > 0:
        await ctx.send(f"<@{str(ctx.message.author.id)}>, '{' '.join(check)}' is not a valid user. Check your spelling and capitalization.")
    else:
        identi = str(ctx.message.author.id)
        cursor.execute(f"SELECT bank FROM balances WHERE identi='{identi}'")
        await ctx.send(f'<@{identi}>, your current bank balance is ${cursor.fetchone()[0]:,}.')


@bot.command()
async def total(ctx, *check):
    checked = ctx.guild.get_member_named(' '.join(check))
    if checked is not None:
        cursor.execute(
            f"SELECT bal FROM balances WHERE identi='{str(checked.id)}'")
        curbal = cursor.fetchone()[0]
        if curbal >= 0:
            await ctx.send(f'The sum of {str(checked)}\'s total assets is ${curbal:,}.')
        else:
            await ctx.send(f'The sum of {str(checked)}\'s total assets is -${abs(curbal):,}.')
    elif checked is None and len(check) > 0:
        await ctx.send(f"<@{str(ctx.message.author.id)}>, '{' '.join(check)}' is not a valid user. Check your spelling and capitalization.")
    else:
        identi = str(ctx.message.author.id)
        total = main.total(identi)
        if total >= 0:
            await ctx.send(f"<@{identi}>, the sum of your total assets is ${main.total(identi):,}.")
        else:
            await ctx.send(f"<@{identi}>, the sum of your total assets is -${abs(main.total(identi)):,}.")


@bot.command()
async def deposit(ctx, amount):
    identi = str(ctx.message.author.id)
    await ctx.send(main.deposit(identi, amount))@bot.command(aliases=["withdrawal"])


@bot.command()
async def withdraw(ctx, amount):
    identi = str(ctx.message.author.id)
    await ctx.send(main.withdraw(identi, amount))


@bot.command(aliases=["leaderboard", "loserboards", "loserboard", "rank"])
async def leaderboards(ctx, *check):
    checked = ctx.guild.get_member_named(' '.join(check))
    if checked is not None:
        identi = str(checked.id)
    elif checked is None and len(check) > 0:
        await ctx.send(f"<@{str(ctx.message.author.id)}>, '{' '.join(check)}' is not a valid user. Check your spelling and capitalization.")
    else:
        identi = str(ctx.message.author.id)
    zero = ctx.message.content.split()[0]
    if zero == "/leaderboards" or zero == "/leaderboard" or zero == "/rank":
        sortby = "DESC"
        sendstr = "Leaderboards"
    elif zero == "/loserboards" or zero == "/loserboard":
        sortby = "ASC"
        sendstr = "Loserboards"
    leaderboard_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    cursor.execute(f"SELECT * FROM stock_prices;")
    stock_prices = cursor.fetchone()
    all_list = main.sort_totals(
        sortby, stock_prices[1], stock_prices[3], stock_prices[5], stock_prices[7], stock_prices[9])
    identi_list = all_list[0]
    money_list = all_list[1]
    member_index = identi_list.index(identi)
    leaderboardstr = ""
    for i in range(5):
        if identi_list[i] != identi:
            leaderboardstr += f"#{i+1}. {str(bot.get_user(identi_list[i]))} (${money_list[i]:,})\n"
        else:
            leaderboardstr += f"__**#{i+1}. <@{identi}> (${money_list[i]:,})**__\n"
    if identi not in identi_list[0:6]:
        leaderboardstr += f"__**#{money_list.index(money_list[member_index])+1}. <@{identi}> (${money_list[member_index]:,})**__"
    leaderboard_embed.add_field(
        name=sendstr.upper(), value=leaderboardstr, inline=False)
    leaderboard_embed.set_footer(
        text=f"{sendstr} are calculated off of total assets.")
    await ctx.send(embed=leaderboard_embed)
    del all_list
    del identi_list
    del money_list


@bot.command(aliases=["send"])
async def pay(ctx, amount: int, *recipient):
    identi = str(ctx.message.author.id)
    person = ctx.guild.get_member_named(' '.join(recipient))
    if person is not None:
        await ctx.send(main.pay(identi, str(person.id), amount))
        cursor.execute(f"INSERT INTO payments (sender, receiver, amount) VALUES ('{identi}', '{person.id}', {amount});")
    else:
        await ctx.send(f"<@{identi}>, '{' '.join(recipient)}' is not a valid user of this server.")

#           #
#   Drugs   #
#           #


@cmds.cooldown(rate=1, per=10, type=cmds.BucketType.user)
@bot.command()
async def grab(ctx):
    identi = str(ctx.message.author.id)
    guild_id = ctx.guild.id
    cursor.execute(
        f"SELECT is_spawned, actual_drug, displayed_drug, spawn_type FROM guild_tables WHERE identi='{guild_id}';")
    info = cursor.fetchone()
    if info[0] == 0:
        await ctx.send(f"<@{identi}>, there is no suspicious substance to grab at this time!")
    else:
        if info[3] == "drug":
            await ctx.send(drugs.grab(identi, info[1], info[2], guild_id))
        elif info[3] == "money":
            cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';\n"
                           f"UPDATE guild_tables SET is_spawned=0 WHERE identi='{guild_id}';\n"
                           f"UPDATE balances SET bal=bal+75 WHERE identi='{identi}';")
            curbal = cursor.fetchone()[0]
            if curbal >= 0:
                await ctx.send(f"Congratulations, <@{identi}>! You were the first to grab the $75. Your balance is now ${curbal+75:,}.")
            else:
                await ctx.send(f"Congratulations, <@{identi}>! You were the first to grab the $75. Your balance is now -${abs(curbal+75):,}.")


@bot.command()
async def use(ctx, slotnum: int):
    identi = str(ctx.message.author.id)
    await ctx.send(drugs.use(identi, slotnum))


@bot.command()
async def destroy(ctx, slotnum: int):
    identi = str(ctx.message.author.id)
    await ctx.send(drugs.destroy(identi, slotnum))


@bot.command(aliases=["inventory"])
async def inv(ctx, *check):
    checked = ctx.guild.get_member_named(' '.join(check))
    if checked is not None:
        identi = str(checked.id)
    else:
        identi = str(ctx.message.author.id)
    inv = drugs.inventory(identi)
    inv_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    inv_embed.add_field(
        name="INVENTORY", value=f"of <@{identi}>", inline=False)
    for key in inv.keys():
        inv_embed.add_field(name=key, value=inv[key], inline=True)
    await ctx.send(embed=inv_embed)


@cmds.cooldown(rate=1, per=5, type=cmds.BucketType.channel)
@bot.command(aliases=["market", "blackmarket", "drugshop"])
async def shop(ctx, *pagenum):
    try:
        num = int(pagenum[0])
    except IndexError:
        num = 1
    identi = str(ctx.message.author.id)
    shop = drugs.shop(identi, num)
    shop_embed = discord.Embed(color=0x000000)
    shop_embed.add_field(name="THE BLACK MARKET",
                         value=f"'Hey, kid. Wanna buy some suspicious substances?'", inline=False)
    if shop == False:
        shop_embed.add_field(name="The shop is current empty.",
                             value=f"\u200b", inline=False)
    elif type(shop) == str:
        await ctx.send(shop)
    else:
        if len(shop) > 0:
            for item in shop:
                shop_embed.add_field(
                    name=f"{item[0]}. {item[1][2].capitalize()} - ${item[1][3]:,}", value=f"sold by <@{item[1][0]}>", inline=True)
        else:
            shop_embed.add_field(
                name=f"There are currently no drugs for sale.", value=f"Check back later!", inline=False)
        await ctx.send(embed=shop_embed)


@bot.command(aliases=["list"])
async def list_drug(ctx, slotnum: int, price: int):
    identi = str(ctx.message.author.id)
    await ctx.send(drugs.list_drug(identi, slotnum, price))


@bot.command(aliases=["unlist"])
async def unlist_drug(ctx, shopnum: int):
    identi = str(ctx.message.author.id)
    await ctx.send(drugs.unlist_drug(identi, shopnum))


@bot.command()
async def buy(ctx, shopnum: int):
    identi = str(ctx.message.author.id)
    await ctx.send(drugs.buy(identi, shopnum))


@bot.command()
async def inspect(ctx, *args):
    identi = str(ctx.message.author.id)
    try:
        slotnum = args[0]
        await ctx.send(drugs.inspect(identi, slotnum))
    except IndexError:
        info = drugs.return_inspect(identi)
        m, s = divmod(info[0], 60)
        h, m = divmod(m, 60)
        inspect_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
        inspect_embed.add_field(
            name="INSPECTION INFORMATION", value=f"for <@{identi}>", inline=False)
        if h < 0 or m < 0 or s < 0:
            inspect_embed.add_field(
                name="Remaining time before cost reset", value=f"0h 0m 0s (already reset)", inline=True)
        else:
            inspect_embed.add_field(
                name="Remaining time before cost reset", value=f"{h}h {m}m {s}s", inline=True)
        inspect_embed.add_field(name="Current cost",
                                value=f"${info[1]:,}", inline=True)
        await ctx.send(embed=inspect_embed)


@cmds.cooldown(rate=1, per=1200, type=cmds.BucketType.user)
@bot.command()
async def reveal(ctx):
    identi = str(ctx.message.author.id)
    await ctx.send(drugs.reveal(identi))

#               #
#   Gambling    #
#               #


@cmds.cooldown(rate=1, per=1, type=cmds.BucketType.user)
@bot.command(aliases=["wager"])
async def bet(ctx, money, letter: str, *times):
    identi = str(ctx.message.author.id)
    try:
        betnum = int(times[0])
    except IndexError:
        betnum = 1
    except ValueError:
        betnum = False
        await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '/bet'. Use '/help bet' for more information on how to use it.")
    if type(betnum) == int:
        await ctx.send(gambling.bet(identi, money, letter, betnum))


@cmds.cooldown(rate=1, per=1, type=cmds.BucketType.user)
@bot.command(aliases=["lb", "box", "open"])
async def lootbox(ctx, letternum, *number):
    identi = str(ctx.message.author.id)
    try:
        number = int(number[0])
    except IndexError:
        number = 1
    except ValueError:
        number = False
        await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '/lootbox'. Use '/help lootbox' for more information on how to use it.")
    try:
        letter = letternum[0]
        num = letternum[1]
    except IndexError:
        letter = False
        num = False
        await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '/lootbox'. Use '/help lootbox' for more information on how to use it.")
    if type(number) == int and type(letter) == str and type(num) == str:
        await ctx.send(lootboxes.lootbox(identi, letter, num, number))

#                #
#   FREE MONEY   #
#                #


@cmds.cooldown(rate=1, per=10, type=cmds.BucketType.user)
@bot.command()
async def work(ctx):
    identi = str(ctx.message.author.id)
    cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';\n"
                   f"UPDATE balances SET bal=bal+4 WHERE identi='{identi}';")
    curbal = cursor.fetchone()[0]
    if curbal >= 0:
        await ctx.send(f"<@{identi}>, you worked for $4. Your balance is now ${curbal+4:,}.")
    else:
        await ctx.send(f"<@{identi}>, you worked for $4. Your balance is now -${abs(curbal+4):,}.")


def ready_to_claim(identi, pack):
    cursor.execute(
        f"SELECT TIMESTAMPDIFF(SECOND, NOW(), (SELECT {pack} FROM claims WHERE identi='{identi}'));")
    remaining_time = cursor.fetchone()[0]
    if remaining_time < 0:
        return True
    else:
        return remaining_time


time_dict = {"hourly": "01:00:00", "bankrupt": "01:30:00",
             "daily": "24:00:00", "weekly": "168:00:00"}


def claim_pack(ctx, pack, amount, time):
    identi = str(ctx.message.author.id)
    remaining_time = ready_to_claim(identi, pack)
    if remaining_time == True:
        cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';\n"
                       f"UPDATE balances SET bal=bal+{amount} WHERE identi='{identi}';\n"
                       f"UPDATE claims SET {pack}=ADDTIME(NOW(), '{time_dict[pack]}') WHERE identi='{identi}'")
        curbal = cursor.fetchone()[0]
        if curbal >= 0:
            return f"<@{identi}>, you have claimed your {pack} pack for ${amount:,}. Your balance is now ${curbal+amount:,}. You will be able to claim this pack again in {time}."
        else:
            return f"<@{identi}>, you have claimed your {pack} pack for ${amount:,}. Your balance is now -${abs(curbal+amount):,}. You will be able to claim this pack again in {time}."
    else:
        m, s = divmod(remaining_time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 0 and h == 0 and m == 0:
            return f"<@{identi}>, you cannot claim your {claim} pack at this time! Wait {s}s."
        elif d == 0 and h == 0:
            return f"<@{identi}>, you cannot claim your {claim} pack at this time! Wait {m}m {s}s."
        elif d == 0:
            return f"<@{identi}>, you cannot claim your {claim} pack at this time! Wait {h}h {m}m {s}s."
        else:
            return f"<@{identi}>, you cannot claim your {claim} pack at this time! Wait {d}d {h}h {m}m {s}s."


@bot.command()
async def hourly(ctx):
    await ctx.send(claim_pack(ctx, "hourly", 75, "1 hour"))


@bot.command()
async def daily(ctx):
    await ctx.send(claim_pack(ctx, "daily", 125, "24 hours"))


@bot.command()
async def weekly(ctx):
    await ctx.send(claim_pack(ctx, "weekly", 500, "7 days"))


@bot.command()
async def bankrupt(ctx):
    identi = str(ctx.message.author.id)
    cursor.execute(f"SELECT bal, bank FROM balances WHERE identi='{identi}';")
    bal_bank = cursor.fetchone()
    cursor.execute(
        f"SELECT URBAD, TSLA, MNCFT, DANK, OOF FROM stocks WHERE identi='{identi}';")
    stocks = cursor.fetchone()
    if bal_bank[0] >= 0:
        await ctx.send(f"<@{identi}>, since your balance (${bal_bank[0]}) is not negative, you cannot claim the bankrupt pack!")
    elif bal_bank[1] > 0:
        await ctx.send(f"<@{identi}>, since your bank balance (${bal_bank[1]}) is not $0, you cannot claim the bankrupt pack!")
    elif stocks != (0, 0, 0, 0, 0):
        await ctx.send(f"<@{identi}>, since you have shares of stocks, you cannot claim the bankrupt pack!")
    else:
        refund = abs(round(random.uniform(0.7, 1.3)*bal_bank[0]))
        cursor.execute(
            f"UPDATE balances SET bal=bal+{refund} WHERE identi='{identi}';")
        if bal_bank[0] + refund >= 0:
            await ctx.send(f"<@{identi}>, you have claimed your bankrupt pack for ${refund:,}. Your balance is now ${bal_bank[0]+refund:,}. You will be able to claim this pack again in 90 minutes.")
        else:
            await ctx.send(f"<@{identi}>, you have claimed your bankrupt pack for ${refund:,}. Your balance is now -${abs(bal_bank[0]+refund):,}. You will be able to claim this pack again in 90 minutes.")


def quick_calc(cd_embed, pack, seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d == 0 and h == 0 and m == 0:
        cd_embed.add_field(name=pack, value=f"{s}s", inline=True)
    elif d == 0 and h == 0:
        cd_embed.add_field(name=pack, value=f"{m}m {s}s", inline=True)
    elif d == 0:
        cd_embed.add_field(name=pack, value=f"{h}h {m}m {s}s", inline=True)
    else:
        cd_embed.add_field(
            name=pack, value=f"{d}d {h}h {m}m {s}s", inline=True)


packs = ("hourly", "daily", "weekly", "bankrupt")
@bot.command()
async def cooldowns(ctx):
    identi = str(ctx.message.author.id)
    cd_embed = discord.Embed(color=int('0x%02X%02X%02X' % (random.randint(
        0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    cd_embed.add_field(name=f"Claim Cooldowns",
                       value=f"of <@{identi}>", inline=False)
    for pack in packs:
        cursor.execute(
            f"SELECT TIMESTAMPDIFF(SECOND, NOW(), (SELECT {pack} FROM claims WHERE identi='{identi}'));")
        time = cursor.fetchone()[0]
        if time <= 0:
            cd_embed.add_field(name=pack.capitalize(),
                               value=f'Ready!', inline=True)
        else:
            quick_calc(cd_embed, pack.capitalize(), time)
    await ctx.send(embed=cd_embed)


@bot.command()
async def claim(ctx):
    identi = str(ctx.message.author.id)
    await ctx.send(f"<@{identi}>, claim commands have been changed so that you no longer need to enter the claim. Now you simply do '/<pack>', for example '/hourly'.\nTo see your claim cooldowns, use '/cooldowns'.")

#             #
#   STOCKS    #
#             #


@bot.command()
async def stocks(ctx):
    stock_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    cursor.execute(f"SELECT * FROM stock_prices;")
    stock_prices = cursor.fetchone()
    for stock_name in stock_helper:
        if stock_prices[stock_helper[stock_name]] > stock_prices[stock_helper[stock_name]-1]:
            stock_embed.add_field(name=f"{stock_name} :chart_with_upwards_trend:",
                                  value=f"${stock_prices[stock_helper[stock_name]]:,} (+${stock_prices[stock_helper[stock_name]]-stock_prices[stock_helper[stock_name]-1]:,})", inline=True)
        elif stock_prices[stock_helper[stock_name]] < stock_prices[stock_helper[stock_name]-1]:
            stock_embed.add_field(name=f"{stock_name} :chart_with_downwards_trend:",
                                  value=f"${stock_prices[stock_helper[stock_name]]:,} (-${stock_prices[stock_helper[stock_name]-1]-stock_prices[stock_helper[stock_name]]:,})", inline=True)
        else:
            stock_embed.add_field(
                name=f"{stock_name}", value=f"${stock_prices[stock_helper[stock_name]]:,} (+$0)", inline=True)
    stock_embed.add_field(name="\u200b", value=f"\u200b", inline=True)
    await ctx.send(embed=stock_embed)


@bot.command(aliases=["invest"])
async def purchase(ctx, amount, stock: str):
    identi = str(ctx.message.author.id)
    stock = stock.upper()
    cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}';")
    curbal = cursor.fetchone()[0]
    cursor.execute(f"SELECT * FROM stock_prices;")
    stock_prices = cursor.fetchone()
    if stock not in stock_helper:
        await ctx.send(f"<@{identi}>, '{stock}' is not a valid stock!")
        return
    if amount == "max" or amount == "all":
        amount = math.floor(curbal/stock_prices[stock_helper[stock]])
    else:
        try:
            amount = int(amount)
        except:
            await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '/purchase'. Use '/help purchase' for more information on how to use it.")
            return
    total_cost = amount*stock_prices[stock_helper[stock]]
    if total_cost > curbal:
        await ctx.send(f"<@{identi}>, you do not have enough money to purchase {amount} share(s) of {stock}! Each stock costs ${stock_prices[stock_helper[stock]]:,}, and purchasing {amount:,} shares would cost ${total_cost:,}, which is more than your current balance (${curbal:,}).")
    elif total_cost < 0:
        await ctx.send(f"<@{identi}>, the cost of those shares is below $0, and thus you cannot purchase them.")
    elif amount <= 0:
        ctx.send(
            f"<@{identi}>, you cannot purchase 0 or less than 0 shares of a stock!")
    else:
        cursor.execute(f"SELECT {stock} FROM stocks WHERE identi='{identi}';\n"
                       f"UPDATE balances SET bal=bal-{total_cost} WHERE identi='{identi}';\n"
                       f"UPDATE stocks SET {stock}={stock}+{amount} WHERE identi='{identi}';")
        await ctx.send(f"<@{identi}>, you have successfully purchased {amount:,} share(s) of {stock}, which is currently worth a total of ${total_cost:,}. You now have {cursor.fetchone()[0]+amount:,} {stock} share(s). Your new balance is ${curbal-total_cost:,}.")


@bot.command()
async def sell(ctx, amount, stock: str):
    identi = str(ctx.message.author.id)
    stock = stock.upper()
    if stock not in stock_helper:
        await ctx.send(f"<@{identi}>, '{stock}' is an invalid stock to sell.")
        return
    cursor.execute(
        f"SELECT {stock}, bal FROM stocks JOIN balances ON stocks.identi=balances.identi WHERE stocks.identi='{identi}';")
    stock_bal = cursor.fetchone()
    stock_amount = stock_bal[0]
    curbal = stock_bal[1]
    cursor.execute(f"SELECT * FROM stock_prices;")
    stock_prices = cursor.fetchone()
    if amount == "all" or amount == "max":
        sell_amount = stock_amount
    else:
        try:
            sell_amount = int(amount)
        except:
            await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '/sell'. Use '/help sell' for more information on how to use it.")
            return
    if sell_amount > stock_amount:
        await ctx.send(f"<@{identi}>, you do not have that many shares to sell! You currently have {stock_amount:,} {stock} shares.")
    elif sell_amount <= 0:
        await ctx.send(f"<@{identi}>, you cannot sell 0 or less than 0 shares of a stock!")
    else:
        sell_money = sell_amount*stock_prices[stock_helper[stock]]
        cursor.execute(f"UPDATE balances SET bal=bal+{sell_money} WHERE identi='{identi}';\n"
                       f"UPDATE stocks SET {stock}={stock}-{sell_amount} WHERE identi='{identi}';")
        if curbal+sell_money >= 0:
            await ctx.send(f"<@{identi}>, have successfully sold {sell_amount:,} share(s) of {stock} for a total of ${sell_money:,}. You now have {stock_amount-sell_amount:,} {stock} share(s). Your new balance is ${curbal+sell_money:,}.")
        else:
            await ctx.send(f"<@{identi}>, have successfully sold {sell_amount:,} share(s) of {stock} for a total of ${sell_money:,}. You now have {stock_amount-sell_amount:,} {stock} share(s). Your new balance is -${abs(curbal+sell_money):,}.")


@bot.command(aliases=["invests", "investments"])
async def shares(ctx):
    identi = str(ctx.message.author.id)
    cursor.execute(
        f"SELECT URBAD, TSLA, MNCFT, DANK, OOF FROM stocks WHERE identi='{identi}';")
    shares = cursor.fetchone()
    cursor.execute(f"SELECT * FROM stock_prices;")
    stock_prices = cursor.fetchone()
    share_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    share_embed.add_field(name=f"INVESTMENTS",
                          value=f"of <@{identi}>", inline=False)
    share_embed.add_field(
        name=f"URBAD Shares", value=f'{shares[0]:,} (${stock_prices[stock_helper["URBAD"]]*shares[0]:,})', inline=True)
    share_embed.add_field(
        name=f"TSLA Shares", value=f'{shares[1]:,} (${stock_prices[stock_helper["TSLA"]]*shares[1]:,})', inline=True)
    share_embed.add_field(
        name=f"MNCFT Shares", value=f'{shares[2]:,} (${stock_prices[stock_helper["MNCFT"]]*shares[2]:,})', inline=True)
    share_embed.add_field(
        name=f"DANK Shares", value=f'{shares[3]:,} (${stock_prices[stock_helper["DANK"]]*shares[3]:,})', inline=True)
    share_embed.add_field(
        name=f"OOF Shares", value=f'{shares[4]:,} (${stock_prices[stock_helper["OOF"]]*shares[4]:,})', inline=True)
    share_embed.add_field(name="\u200b", value=f"\u200b", inline=True)
    await ctx.send(embed=share_embed)

#                       #
#   SLOT AND ROULETTE   #
#                       #


def win_check3(board):
    return_list = []
    if board[1] == board[2] == board[3]:
        return_list.append(board[1])
    if board[4] == board[5] == board[6]:
        return_list.append(board[4])
    if board[7] == board[8] == board[9]:
        return_list.append(board[7])
    if board[1] == board[5] == board[9]:
        return_list.append(board[1])
    if board[2] == board[5] == board[8]:
        return_list.append(board[2])
    if board[3] == board[6] == board[9]:
        return_list.append(board[3])
    if board[1] == board[4] == board[7]:
        return_list.append(board[1])
    if board[7] == board[5] == board[3]:
        return_list.append(board[7])
    return return_list


multipliers = {":small_red_triangle_down:": 3, ":small_orange_diamond:": 3.5, ":small_blue_diamond:": 4,
               ":large_orange_diamond:": 4.5, ":large_blue_diamond:": 5, ":small_red_triangle:": 5.5}


@cmds.cooldown(rate=1, per=15, type=cmds.BucketType.user)
@bot.command(aliases=["slotmachine", "slot"])
async def slots(ctx):
    identi = str(ctx.message.author.id)
    cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
    curbal = cursor.fetchone()[0]
    if curbal < 200:
        await ctx.send(f"<@{identi}>, you cannot afford to roll a slotmachine ($200), as your balance is only ${curbal:,}.")
    else:
        slotmachine_embed = discord.Embed(color=0x009b04)
        board = [random.choice([key for key in multipliers])
                 for i in range(10)]
        slotmachine_embed.add_field(
            name=f"{board[1]} | {board[2]} | {board[3]}", value="\u200b", inline=False)
        slotmachine_embed.add_field(
            name=f"{board[4]} | {board[5]} | {board[6]}", value="\u200b", inline=False)
        win_list = win_check3(board)
        if len(win_list) >= 1:
            total_won = 0
            s = ''
            if len(win_list) != 1:
                s = 's'
            for winning_emoji in win_list:
                total_won += int(multipliers[winning_emoji]*200)
            cursor.execute(
                f"UPDATE balances SET bal=bal+{total_won} WHERE identi='{identi}';")
            cursor.execute(
                f"SELECT bal FROM balances WHERE identi='{identi}';")
            slotmachine_embed.add_field(name=f"{board[7]} | {board[8]} | {board[9]}",
                                        value=f"You won ${total_won:,} from forming {len(win_list)} line{s} of 3 emotes! Your new balance is ${cursor.fetchone()[0]:,}.", inline=False)
        else:
            cursor.execute(
                f"UPDATE balances SET bal=bal-200 WHERE identi='{identi}';")
            cursor.execute(
                f"SELECT bal FROM balances WHERE identi='{identi}';")
            slotmachine_embed.add_field(name=f"{board[7]} | {board[8]} | {board[9]}",
                                        value=f"You lost $200 from failing to form any lines in a 3-row slot machine!\nYour new balance is ${cursor.fetchone()[0]:,}.", inline=False)
        await ctx.send(embed=slotmachine_embed)
roulette_list = ["🔺", "🔷", "🔷", "🔶", "🔶", "🔶", "🔹", "🔹", "🔹",
                 "🔹", "🔸", "🔸", "🔸", "🔸", "🔸", "🔻", "🔻", "🔻", "🔻", "🔻", "🔻"]
roulette_winners = {"🔻": 3.5, "🔸": 4.2, "🔹": 5.25, "🔶": 7, "🔷": 10.5, "🔺": 21}
@cmds.cooldown(rate=1, per=15, type=cmds.BucketType.user)
@bot.command()
async def roulette(ctx, money: int, emoji: str):
    identi = str(ctx.message.author.id)
    cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
    curbal = cursor.fetchone()[0]
    if emoji not in roulette_list:
        await ctx.send(f"<@{identi}>, that emoji is not a valid emoji to bet on! Please use one of the following: 🔻 🔸 🔹 🔶 🔷 🔺")
    elif money > curbal:
        await ctx.send(f"<@{identi}>, the amount you are trying to bet (${money:,}) exceeds your current balance (${curbal:,})!")
    elif money <= 0:
        await ctx.send(f"<@{identi}>, you cannot bet 0 or negative money!")
    else:
        send_list = random.choices(roulette_list, k=11)
        roulette_embed = discord.Embed(color=0x009b04)
        roulette_embed.add_field(name=f"=----------------------------|----------------------------=",
                                 value=f"{' '.join(send_list)}", inline=False)
        if send_list[5] == emoji:
            win_amount = int(money*roulette_winners[emoji])
            cursor.execute(
                f"UPDATE balances SET bal=bal+{win_amount} WHERE identi='{identi}';")
            roulette_embed.add_field(name=f"=----------------------------|----------------------------=",
                                     value=f"The emoji you bet on matched the winning emoji! Since you bet ${money:,} on {emoji}, you won ${win_amount:,}. Your new balance is ${curbal+win_amount}.", inline=False)
        else:
            cursor.execute(
                f"UPDATE balances SET bal=bal-{money} WHERE identi='{identi}';")
            roulette_embed.add_field(name=f"=----------------------------|----------------------------=",
                                     value=f"Your bet on {emoji} did not match the winning emoji, {send_list[5]}. You lost ${money:,} and your new balance is ${curbal-money:,}.", inline=False)
        await ctx.send(embed=roulette_embed)

#               #
#   STEALING    #
#               #


@cmds.cooldown(rate=1, per=60, type=cmds.BucketType.user)
@bot.command()
async def mug(ctx, amount: int, *user):
    identi = str(ctx.message.author.id)
    cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
    curbal = cursor.fetchone()[0]
    mugged = ctx.guild.get_member_named(' '.join(user))
    if mugged is not None:
        cursor.execute(
            f"SELECT bal FROM balances WHERE identi='{str(mugged.id)}'")
        mugged_curbal = cursor.fetchone()[0]
        if len(user) == 0:
            await ctx.send(f"<@{identi}>, you have have one or more incorrect arguments for '/mug'. Use '/help mug' for more information on how to use it.")
        elif amount <= 0:
            await ctx.send(f"<@{identi}>, you cannot try to mug someone for 0 or negative amounts of money!")
        elif amount > curbal:
            await ctx.send(f"<@{identi}>, the amount you are trying to mug for (${amount:,}) exceeds your current funds (${curbal:,})!")
        elif amount > mugged_curbal/3:
            await ctx.send(f"<@{identi}>, ${amount:,} is too much to rob from {mugged}, whose balance is ${mugged_curbal:,}. The maximum amount that you can rob them for at this time is ${math.floor(mugged_curbal/3):,}.")
        elif str(mugged.id) == str(identi):
            await ctx.send(f"<@{identi}>, you cannot mug yourself!")
        else:
            mug_list = [curbal, mugged_curbal]
            mug_check = random.randint(
                1, round(max(mug_list)/min(mug_list)+1, 2)*100)
            if mug_check >= 1 and mug_check <= 100:
                # success
                cursor.execute(
                    f"UPDATE balances SET bal=bal+{amount} WHERE identi='{identi}';\nUPDATE balances SET bal=bal-{amount} WHERE identi='{str(mugged.id)}';")
                await ctx.send(f"<@{identi}>, you have successfully mugged <@{mugged.id}> for ${amount:,}! Your balances are now ${curbal+amount:,} and ${mugged_curbal-amount:,}, respectively.")
            else:
                # fail
                cursor.execute(
                    f"UPDATE balances SET bal=bal-{amount} WHERE identi='{identi}';\nUPDATE balances SET bal=bal+{amount} WHERE identi='{str(mugged.id)}';")
                await ctx.send(f"<@{identi}>, you have failed in mugging <@{mugged.id}> for ${amount:,}! Your balances are now ${curbal-amount:,} and ${mugged_curbal+amount:,}, respectively.")
    else:
        await ctx.send(f"<@{identi}>, '{' '.join(user)}' is not a valid user of this server. Check spelling and capitalization,")

#          #
#   HELP   #
#          #


@bot.command()
async def feedback(ctx, *info):
    elon = ctx.guild.get_member(341277715179110400)
    await elon.send(f"<@{str(ctx.message.author.id)}> from {ctx.guild.name}: {' '.join(info)}")
bot.help_command = None
@bot.command()
async def help(ctx, *cmd):
    identi = str(ctx.message.author.id)
    try:
        cmd = cmd[0]
    except IndexError:
        cmd = "general"
    returned_msg = helper.help_func(identi, cmd)
    if type(returned_msg) == str:
        await ctx.send(returned_msg)
    else:
        help_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
        for help_msg in returned_msg:
            help_embed.add_field(name=help_msg[:help_msg.index(
                '|')], value=help_msg[help_msg.index('|')+1:], inline=False)
        if cmd == "drugs":
            help_embed.add_field(name="More info", value="Drugs can have 4 qualities: disgusting, crummy, regular, and luxurious. Depending on the quality of the drug, you win chance and win/loss money will be affected. The current types of drugs in the game are suspicious white powder (affects lootbox Zs) and suspicious crystalline susbstance (affects bets on a). Although most drugs' quality will be unknown, some will spawn with their quality on display.", inline=False)
        elif cmd == "misc":
            help_embed.add_field(
                name="Spawns", value="Either money ($75) or a randomly generated drug will spawn every 3-7 minutes on a server, as long as there is a message sent after the cooldown is 0. Use the grab command to claim it.", inline=False)
        del returned_msg
        await ctx.send(embed=help_embed)


@bot.command()
async def commands(ctx):
    await ctx.send(f"Available commands: {', '.join([command.name for command in bot.commands])}.")

@bot.event
async def on_message(message):
    channel = message.channel
    author_id = message.author.id
    if author_id in command_counter and command_counter[author_id] >= 3:
        if author_id not in blocked_list:
            blocked_list.append(author_id)
            await asyncio.sleep(20)
            try:
                blocked_list.remove(author_id)
            except:
                pass
    try:
        guild_id = message.guild.id
    except:
        guild_id = False
    if guild_id != False:
        if drugs.calc_spawn(guild_id) and message.author.id != 567907283686653987 and message.author.id != 566039033944342547:
            if random.randint(1, 2) == 1:
                qual = random.choice(drug_qualities)
                rand = random.randint(0, len(drug_names)-1)
                name = drug_names[rand]
                try:
                    spawn_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
                        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
                    spawn_embed.add_field(
                        name=f'You spot {qual+name}!', value="Use '/grab' to claim it before anyone else!", inline=False)
                    spawn_embed.set_image(url=drug_urls[rand])
                    await channel.send(embed=spawn_embed)
                except:
                    pass
                else:
                    quickrand = random.randint(1, 16)
                    if quickrand >= 1 and quickrand <= 5:
                        cursor.execute(f"UPDATE guild_tables SET is_spawned=1, spawn_type='drug' WHERE identi='{guild_id}';\n"
                                    f"UPDATE guild_tables SET actual_drug='{qual+name}', displayed_drug='{qual+name}' WHERE identi='{guild_id}';")
                    else:
                        cursor.execute(f"UPDATE guild_tables SET is_spawned=1, spawn_type='drug' WHERE identi='{guild_id}';\n"
                                    f"UPDATE guild_tables SET actual_drug='{qual+name}', displayed_drug='{name}' WHERE identi='{guild_id}';")
            else:
                try:
                    spawn_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
                        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
                    spawn_embed.add_field(
                        name=f'You spot $75!', value="Use '/grab' to claim it before anyone else!", inline=False)
                    spawn_embed.set_image(url="https://i.imgur.com/GqkOmvq.png")
                    await channel.send(embed=spawn_embed)
                except:
                    pass
                else:
                    cursor.execute(
                        f"UPDATE guild_tables SET spawn_time=ADDTIME(NOW(), '00:{random.randint(3,7)}:00'), is_spawned=1, spawn_type='money' WHERE identi='{guild_id}';")

    await bot.process_commands(message)

#               #
#   BLACKJACK   #
#               #


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return self.rank+self.suit


suits = ("\♠", "\♣", "\♥", "\♦")
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
ranks_and_values = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
                    "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}
deck = [Card(rank, suit) for suit in suits for rank in ranks]
blackjack_info = {}


def is_playing(ctx):
    return ctx.message.author.id in blackjack_info


def calc_player(player_deck):
    player_value = 0
    for card in player_deck:
        player_value += ranks_and_values[card.rank]
    if player_value > 21:
        aces = len(["A" for card in player_deck if card.rank == "A"])
        for i in range(aces):
            player_value -= 10
            if player_value <= 21:
                break
    return player_value


def calc_dealer(dealer_deck):
    dealer_value = 0
    for card in dealer_deck:
        dealer_value += ranks_and_values[card.rank]
    if dealer_value > 21:
        aces = len(["A" for card in dealer_deck if card.rank == "A"])
        for i in range(aces):
            dealer_value -= 10
            if dealer_value <= 21:
                break
    return dealer_value


def dealer_hidden(dealer_deck):
    dealer_value = 0
    for card in dealer_deck[1:]:
        dealer_value += ranks_and_values[card.rank]
    returned = [str(dealer_value)]
    aces = len(["A" for card in dealer_deck[1:] if card.rank == "A"])
    for i in range(aces):
        returned.append(str(dealer_value-(i+1)*10))
    return returned


def rand_card(deckparam):
    return deckparam.pop(deckparam.index(random.choice(deckparam)))


def checks(identi, curbal, amount, end_turn=False):
    player_sum = calc_dealer(blackjack_info[identi]["player"])
    dealer_sum = calc_dealer(blackjack_info[identi]["dealer"])
    if end_turn:
        if player_sum > dealer_sum:
            cursor.execute(
                f"UPDATE balances SET bal=bal+{amount} WHERE identi='{identi}';")
            return (True, f"**You won the game of blackjack and gained ${amount:,}! Your balance is now ${curbal+amount:,}.**")
        elif dealer_sum > player_sum:
            cursor.execute(
                f"UPDATE balances SET bal=bal+{-amount} WHERE identi='{identi}';")
            return (True, f"You have lost the hand of blackjack and with it your bet of ${amount:,}! Your balance is now ${curbal-amount:,}.")
        elif player_sum == dealer_sum:
            return (True, f"The game of blackjack was a tie and thus you didn't win anything.")
    if player_sum == 21:
        cursor.execute(
            f"UPDATE balances SET bal=bal+{math.floor(amount*1.5)} WHERE identi='{identi}';")
        return (True, f"**You won with a blackjack! You won ${math.floor(amount*1.5):,}, and your balance is now ${curbal+math.floor(amount*1.5):,}.**")
    elif dealer_sum == 21:
        cursor.execute(
            f"UPDATE balances SET bal=bal+{-amount} WHERE identi='{identi}';")
        return (True, f"The dealer wins with a blackjack! You lost ${amount:,}, and your balance is now ${curbal-amount:,}.")
    elif dealer_sum > 21:
        cursor.execute(
            f"UPDATE balances SET bal=bal+{amount} WHERE identi='{identi}';")
        return (True, f"**The dealer busts and you win ${amount:,}! Your balance is now ${curbal+amount:,}.**")
    elif player_sum > 21:
        cursor.execute(
            f"UPDATE balances SET bal=bal+{-amount} WHERE identi='{identi}';")
        return (True, f"You bust and lose ${amount:,}! Your balance is now ${curbal-amount:,}.")
    else:
        return (False, '')


def gen_embed(identi, curbal, amount, reshow=False, dealer_str='', player_str=''):
    if player_str == '':
        temp_deck = deck.copy()
        dealer = [rand_card(temp_deck), rand_card(temp_deck)]
        player = [rand_card(temp_deck), rand_card(temp_deck)]
        blackjack_info[identi] = {"deck": temp_deck, "dealer": dealer,
                                  "player": player, "amount": amount, "moveable": True}
        del temp_deck
        del dealer
        del player
    blackjack_embed = discord.Embed(color=int('0x%02X%02X%02X' % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    if "stay" in dealer_str and "stay" in player_str:
        checkwin = checks(identi, curbal, amount, True)
    else:
        checkwin = checks(identi, curbal, amount)
    if checkwin[0] == False:
        # game hasn't ended yet
        if reshow == True:
            blackjack_embed.add_field(name=f"**| {random.choice(deck)} | BLACKJACK | {random.choice(deck)} |**",
                                      value=f'Player: <@{identi}> | Current bet: ${amount:,}\nSince you were in a game, the game is being continued.\n⠀', inline=False)
        else:
            blackjack_embed.add_field(name=f"**| {random.choice(deck)} | BLACKJACK | {random.choice(deck)} |**",
                                      value=f'Player: <@{identi}> | Current bet: ${amount:,}\n⠀', inline=False)
        blackjack_embed.add_field(name=f'Dealer ( ?+{"/".join(sorted(dealer_hidden(blackjack_info[identi]["dealer"])))} )',
                                  value=f'\n{dealer_str}\n**| ?? | |{"| | ".join([str(card) for card in blackjack_info[identi]["dealer"][1:]])} |**\n⠀', inline=False)
        blackjack_embed.add_field(name=f'Player ( {calc_player(blackjack_info[identi]["player"])} )',
                                  value=f'{player_str}\n**| {" | | ".join([str(card) for card in blackjack_info[identi]["player"]])} |**\n⠀', inline=False)
        blackjack_embed.set_footer(
            text=f"Use '/hit' to hit, '/double' to double your bet and draw a card,\n/stay' to stay, or '/ff' to surrender and refund half your bet.")
    else:
        # game has ended
        if reshow == True:
            blackjack_embed.add_field(name=f"**| {random.choice(deck)} | BLACKJACK | {random.choice(deck)} |**",
                                      value=f'Player: <@{identi}> | Current bet: ${amount:,}\nSince you were in a game, the game is being continued.\n⠀', inline=False)
        else:
            blackjack_embed.add_field(name=f"**| {random.choice(deck)} | BLACKJACK | {random.choice(deck)} |**",
                                      value=f'Player: <@{identi}> | Current bet: ${amount:,}\n⠀', inline=False)
        blackjack_embed.add_field(name=f'Dealer ( {calc_player(blackjack_info[identi]["dealer"])} )',
                                  value=f'{dealer_str}\n**| {" | | ".join([str(card) for card in blackjack_info[identi]["dealer"]])} |**\n⠀', inline=False)
        blackjack_embed.add_field(name=f'Player ( {calc_player(blackjack_info[identi]["player"])} )',
                                  value=f'{player_str}\n**| {" | | ".join([str(card) for card in blackjack_info[identi]["player"]])} |**\n⠀\n{checkwin[1]}', inline=False)
        del blackjack_info[identi]
    return blackjack_embed


@bot.command()
async def blackjack(ctx, amount: int):
    identi = str(ctx.message.author.id)
    cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
    curbal = cursor.fetchone()[0]
    if amount <= 0:
        await ctx.send(f"<@{identi}>, you cannot bet 0 or negative amounts of money!")
    elif amount > curbal:
        await ctx.send(f"<@{identi}>, the amount you are trying to bet (${amount:,}) exceeds your current funds (${curbal:,})!")
    elif identi in blackjack_info:
        await ctx.send(embed=gen_embed(identi, curbal, amount, True))
    else:
        await ctx.send(embed=gen_embed(identi, curbal, amount))


@bot.command(aliases=["surrender"])
async def ff(ctx):
    identi = str(ctx.message.author.id)
    if identi not in blackjack_info:
        await ctx.send(f"<@{identi}>, you are not currently in a game of blackjack!")
    else:
        cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
        curbal = cursor.fetchone()[0]
        halfbet = math.floor(blackjack_info[identi]["amount"]/2)
        cursor.execute(f"UPDATE balances SET bal=bal-{halfbet} WHERE identi='{identi}';")
        await ctx.send(f"<@{identi}>, you have forfeit your match of blackjack. Half (${halfbet:,}) of your bet was refunded. Your balance is now ${curbal-halfbet:,}.")
        del blackjack_info[identi]

def dealer_move(identi):
    dealer_sum = calc_dealer(blackjack_info[identi]["dealer"])
    if dealer_sum < 17:
        card = rand_card(blackjack_info[identi]["deck"])
        blackjack_info[identi]["dealer"].append(card)
        return f"The dealer draws **| {str(card)} |**."
    else:
        return f"The dealer stays."

@bot.command(aliases=['draw'])
async def hit(ctx):
    identi = str(ctx.message.author.id)
    if identi not in blackjack_info:
        await ctx.send(f"<@{identi}>, you are not currently in a game of blackjack!")
    elif blackjack_info[identi]["moveable"] == False:
        await ctx.send(f"<@{identi}>, you cannot hit because you doubled your bet!")
    else:
        cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
        curbal = cursor.fetchone()[0]
        amount = blackjack_info[identi]["amount"]
        card = rand_card(blackjack_info[identi]["deck"])
        blackjack_info[identi]["player"].append(card)
        await ctx.send(embed=gen_embed(identi, curbal, amount, dealer_str=dealer_move(identi), player_str=f"You draw **| {str(card)} |**."))


@bot.command()
async def double(ctx):
    identi = str(ctx.message.author.id)
    if identi not in blackjack_info:
        await ctx.send(f"<@{identi}>, you are not currently in a game of blackjack!")
    else:
        cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
        curbal = cursor.fetchone()[0]
        if blackjack_info[identi]["amount"]*2 > curbal:
            await ctx.send(f'<@{identi}>, the doubled price of that bet (${blackjack_info[identi]["amount"]*2:,}) exceeds your funds (${curbal:,})!')
        else:
            blackjack_info[identi]["amount"] *= 2
            blackjack_info[identi]["moveable"] = False
            card = rand_card(blackjack_info[identi]["deck"])
            blackjack_info[identi]["player"].append(card)
            await ctx.send(embed=gen_embed(identi, curbal, blackjack_info[identi]["amount"], dealer_str=dealer_move(identi), player_str=f'You double your bet to ${blackjack_info[identi]["amount"]:,} and draw **| {str(card)} |**.'))


@bot.command()
async def stay(ctx):
    identi = str(ctx.message.author.id)
    if identi not in blackjack_info:
        await ctx.send(f"<@{identi}>, you are not currently in a game of blackjack!")
    else:
        cursor.execute(f"SELECT bal FROM balances WHERE identi='{identi}'")
        curbal = cursor.fetchone()[0]
        amount = blackjack_info[identi]["amount"]
        await ctx.send(embed=gen_embed(identi, curbal, amount, dealer_str=dealer_move(identi), player_str=f"You stay."))

bot.loop.create_task(run_updater())
bot.loop.create_task(send_stocks())
bot.loop.create_task(reset_busts())
bot.run("NTY3OTA3MjgzNjg2NjUzOTg3.XR19NQ.hey8kK6lFIEcriDvTMHDskZA5WU")
# IF COMMANDS AREN'T WORKING, MAKE SURE YOU ARE ON THE RIGHT SERVER