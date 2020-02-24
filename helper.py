help_dict = {'bal': "/bal [<user>]|Displays the balance of a user. Defaults to yourself, but passing in a username will allow you to see their balance. Include the user's discriminant to further refine your search.", 
'work':"/work|A command a usable every 10 seconds that grants you $4.", 
'bank':"/bal [<user>]|Displays the bank balance of a user. Defaults to yourself, but passing in a username will allow you to see their bank balance. Include the user's discriminant to further refine your search.", 
'total':"/total [<user>]|Displays the sum of all of a user's assets (balance, bank, stocks). Defaults to yourself, but passing in a username will allow you to see their total assets. Include the user's discriminant to further refine your search.", 
'hourly':"/hourly|A command usable every hour that adds $75 to your balance.", 
'daily':"/daily|A command usable every day that adds $125 to your balance.", 
'weekly':"/weekly|A command usable every day that adds $500 to your balance.", 
'bankrupt':"/bankrupt|A command usable every 90 minutes that pays you 70-130% of your current debt. Can only be used if you are truly in debt.", 
'deposit':"/deposit <amount>|Deposits money into your bank account from your balance.", 
'withdraw':"/withdraw <amount>|Withdraws money from your bank account into your balance.", 
'leaderboards':"/leaderboards (or loserboards)|Shows you the top 5 users with highest total assets, depending on the command entered.", 
'pay':"/pay <amount> <username>|Sends money to a specified user. Include the user's discriminant to further refine your pay.", 
'stocks':"/stocks|Displays the current price per share of all of the stocks.", 
'grab':"/grab|Allows you to grab the money/suspicious substances that occasionally spawn in the server.", 
'use':"/use <slot>|Uses a suspicious substance from a specified inventory slot. Each use of a suspicious substance increases your chance that your next use will result in a police bust (read more by using '/help suspicious substances'), but the chance resets at around midnight.", 
'purchase':"/purchase <amount> <stockname>| Purchases a specified amount of a stock's shares. Amount can be 'all' or 'max' to purchase as many shares as possible with your current funds.", 
'sell':"/sell <amount> <stock>|Sells a specific amount of shares of a stock. The amount can be 'all' or 'max' to sell all of your shares.", 
'destroy':"/destroy <slot>|Destroys a suspicious substance from a specified inventory slot, decreasing your chances of being busted by the police (read more by using '/help suspicious substances').", 
'help':"/help <command or category>|Gives you help on a category of gambling or a specific command.", 
'shares':"/shares|Shows you the amount of shares you have in each stock and the total monetary sum of each.", 
'inv':"/inv|Displays your inventory to you.", 
'slots':"/slots|Rolls a 3x3 slotmachine for a cost of $200. Creating any row of 3 emojis brings a reward, and each emoji gives a different amount of money\n(🔻<🔸<🔹<🔶<🔷<🔺).", 
'shop':"/shop|Shows you the black market from which you can buy suspicious substances.", 
'roulette':"/roulette <amount> <emoji>|Bets a certain amount of money on a specific emoji. If correct, you will get a monetary reward depending on the rarity of the emoji\n(🔻<🔸<🔹<🔶<🔷<🔺).", 
'list_drug':"/list <slot> <price>|Lists a suspicious substance onto the black market from a specific inventory slot. Listing a suspicious substance on the market incurs a fee a 10% of the price.", 
'mug':"/mug <username> <amount>|Attempts to mug a user for a certain amount of money, usable every 60 seconds. Enter the user's discriminant to refine your mugging. The more your balances differ, the lower the chance of a successful mugging. You can only mug up to 1/3 of  a user's current balance. A successful mugging takes the amount from them and adds it to you, while a failed mugging does the opposite.", 
'unlist_drug':"/unlist <shopnum>|Takes a suspicious substance off of the black market at a specific shop number. This does not refund the fee you paid to list it.", 
'feedback':"/feedback <message>|Sends the message to the bot's creator. Most commonly will be a bug report, but you can also request new features or feature changes through this.", 
'buy':"/buy <shopnum>|Buys a suspicious substance off of the black market.", 
'inspect':"/inspect [<slotnum>]|Inspects a drug from your inventory, revealing its quality, for a price. The price resets every 2 hours. You can see your current inspection timer and current cost by using '/inspect' with no parameters.", 
'reveal':"/reveal|Reveals the quality of suspicious substances in your inventory. This is only usable if all three of your inventory slots are occupied and you don't know their qualities.", 
'bet':"/bet <amount> <letter> [<times>]|Bets on money on a letter a number of times (max 3, default 1). a and b both have a 50% chance of success and will double the bet money. c has a 5% chance of a win but will return 20x the money put in. d has a 10% chance of winning but you only lose 10% of the money you put in.", 
'lootbox':"/lootbox <letterqual> [<number>]|Purchases and opens lootboxes of the desired letter and quality, up to a maximum of 3 at once (default 1). Lootbox Zs take in the price of the lootbox, which is multiplied by a multiplier between -10 and 10 (bell curved) and given to the player. A z1 lootbox costs $50, a z2 $75, and a z3 $100. Lootbox Ys have a chance at giving you money, drugs, or nothing, with the prizes getting better depending on the tier. A y1 lootbox costs $25, a y2 $50, and a y3 $75.",
'blackjack':'Blackjack|/blackjack <amount>\nBets an amount of money on a blackjack game.\n/hit\nDraw a card. Only usable during a game of blackjack.\n/blackjack <amount>\nDraw a card and double the bet. Using this command will prevent you from any actions except for staying in the following moves. Only usable during a game of blackjack.\n/stay\nPerform no action for your move. Only usable during a blackjack game.\n/ff\nSurrender a game of blackjack. This refunds half of your money. Only usable during a game of blackjack.',
"commands": "/commands|Shows you all of the currently available commands that can be used.",
"cooldowns": "/cooldowns|Shows you the remaining times before you can claim the various packs.",
"general":"General|'/help gambling' to learn the basics of this bot.\n'/help types' to learn about the types of gambling.\n'/help drugs' for information on drugs.\n'/help misc' for other information about gambling.\n'/help <command>' for help on a specific command.",
"gambling": "gambling| bal bank total deposit withdraw leaderboards pay",
"types": "types| bet lootbox slots roulette stocks purchase sell shares blackjack",
"drugs": "drugs| grab use destroy inv list_drug unlist_drug buy inspect reveal",
"misc": "misc| cooldowns hourly daily weekly bankrupt mug feedback help commands"}

blackjack_str = "/blackjack <amount>|Bets an amount of money on a blackjack game."
#add ghelp for categories as well as blackjack and whatnot

def help_func(identi, asked_help):
    if asked_help not in help_dict:
        return f"<@{identi}>, '{asked_help}' is not a valid command or category to get help for."
    if asked_help == "gambling" or asked_help == "types" or asked_help == "drugs" or asked_help == "misc":
        return [help_dict[help_name] for help_name in help_dict[asked_help].split()[1:]]
    else:
        return [help_dict[asked_help]]