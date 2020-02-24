import discord
client = discord.Client()
@client.event
async def on_message(message):
    to_leave = client.get_guild(587033603750494209)
    await to_leave.leave()
    print(f"Successfully left guild {to_leave.name}")
client.run("NTY3OTA3MjgzNjg2NjUzOTg3.XQAOFQ.K7C-dVPOAGXtqAKWAHno3HCzfFM")