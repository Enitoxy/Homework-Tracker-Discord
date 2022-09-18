#IMPORTS
import os
import discord
import datetime
import asyncio
import sys
import pymongo


#FROM DISCORD
from discord import app_commands
from discord.ext import commands, tasks


#FROM OTHERS
from dotenv import load_dotenv
from datetime import datetime


#INTENTS
intents = discord.Intents.all()
intents.members = True


#DON'T GENERATE __PYCACHE__
sys.dont_write_bytecode = True


#DOTENV
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PASS = os.getenv('MONGODB_PASSWORD')


#TIMELESS28 GUILD ID (FOR SYNCING)
MY_GUILD = discord.Object(id=1020373328164294726)


#BOT CLASS
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", help_command=None, intents=intents)

    #ON_READY
    async def on_ready(self):
        timestamp = datetime.now()

        print("-------------------")
        print('Homework Tracker is ONLINE!')
        print(timestamp.strftime("T: %d/%m/%Y %H:%M:%S"))
        print('Ping: {0}ms'.format(round(bot.latency, 3)))

        #BOT STATUS LOOP
        bot.loop.create_task(status_task())
    
        #START MEMBER COUNT LOOP
        membercount.start()

    #LOAD COGS & SYNC SLASH COMMANDS
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.startswith("__pycache__"):
                continue
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"-------------------\nLoaded {filename}")
            else:
                print(f"-------------------\nError loading {filename}")

        await self.tree.sync()
        print("-------------------")
        print("Synced Slash Commands")
        print("-------------------")


#MEMBER COUNT CHANNEL LOOP
@tasks.loop(minutes=30)
async def membercount():
    amount = 0
    guild = bot.get_guild(1020373328164294726)
    channel = bot.get_channel(1020381747969532075)
    if amount != guild.member_count:
        await channel.edit(name=f"Members: {guild.member_count}")


@membercount.before_loop
async def before_loop_occur():
    await bot.wait_until_ready()


#DEFINE BOT
bot = Bot()


#LOAD COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.channel.send(f"Loaded **{extension}**", delete_after=1)
    await ctx.channel.purge(amount=1)


#UNLOAD COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.channel.send(f"Unloaded **{extension}**", delete_after=1)
    await ctx.channel.purge(amount=1)


#RELOAD COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await bot.load_extension(f'cogs.{extension}')
    await ctx.channel.send(content=f"Reloaded **{extension}** succesfully", delete_after=1)
    await ctx.channel.purge(amount=1)


#BOT STATUS
@bot.event
async def status_task():
    while True:
        await bot.change_presence(activity=discord.Game(name="Now in Alpha!"))
        await asyncio.sleep(120)
        await bot.change_presence(activity=discord.Game(name="Turn off the phone and study!"))
        await asyncio.sleep(120)
        await bot.change_presence(activity=discord.Game(name="beep boop"))
        await asyncio.sleep(120)
        await bot.change_presence(activity=discord.Game(name="Supports Slash Commands!"))



bot.run(TOKEN)