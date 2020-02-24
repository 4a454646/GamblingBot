import MySQLdb
database_config = {'host': '34.94.60.13', 'db': 'discord_db', 'user': 'root', 'password': 'pHgPTpy@ycD', "autocommit": True}
connection = MySQLdb.connect(**database_config)
cursor = connection.cursor()
cursor.execute(f"SELECT TSLA_after FROM stock_prices;")
print(cursor.fetchone())