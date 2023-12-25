"""
main.py
~~~~~~~~~~~~~~~~~~~
Main file.
"""

#IMPORTS
import os
import datetime
import asyncio
import sys
import platform
import logging
import discord

from typing import Final
from discord.ext import commands
from app import app
from hypercorn.config import Config
from hypercorn.asyncio import serve
from colorama import init as colorama_init
from colorama import Fore, Style
from dotenv import load_dotenv

load_dotenv()

colorama_init(autoreset=True)

#INTENTS
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True


#DON'T GENERATE __PYCACHE__
sys.dont_write_bytecode = True

#LOGGING
root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '{1}[%(asctime)s]{0} {2}[%(levelname)s]{0} {3}%(name)s{0} - %(message)s'.format(
        Style.RESET_ALL,
        Fore.LIGHTBLACK_EX,
        Fore.BLUE,
        Fore.MAGENTA,
        ),
    "%d-%m-%Y %H:%M:%S"
    )
handler.setFormatter(formatter)
root.addHandler(handler)

logging.getLogger('hypercorn.access').setLevel(logging.ERROR)

#DOTENV
TOKEN : Final[str] = os.environ['DISCORD_TOKEN']

#HYPERCORN CONFIG
config = Config()
config.bind = [f"0.0.0.0:80"]

#BOT CLASS
class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix="/", help_command=None, intents=intents)
        self.discord_version = discord.__version__
        self.platform = platform.python_version()

    #ON_READY
    async def on_ready(self):
        c = (
            Style.RESET_ALL,
            Fore.LIGHTGREEN_EX,
            Fore.LIGHTCYAN_EX,
            Fore.MAGENTA,
            Fore.LIGHTBLACK_EX
            )
        timestamp = datetime.datetime.now()
        amount = len(bot.guilds)
        shards = bot.shard_count
        print(f'{c[4]}----------------------')
        print(f'Homework Tracker is online and in {amount} servers!')
        print(f'{c[2]}Shards:{c[0]} {shards}')
        print(f'{c[2]}Ping:{c[0]} {round(bot.latency, 3)}ms')
        print(f'{c[2]}API:{c[0]} {self.discord_version}')
        print(f'{c[2]}Python:{c[0]} {self.platform}')
        print(timestamp.strftime(f"{c[3]}T: %d/%m/%Y %H:%M:%S\n{c[4]}----------------------"))

        #BOT LOOPS
        bot.loop.create_task(status_task())

    #LOAD COGS & SYNC SLASH COMMANDS
    async def setup_hook(self):
        c = (
            Style.RESET_ALL,
            Fore.LIGHTBLACK_EX,
            Fore.YELLOW,
            Fore.RED
            )
        for filename in os.listdir('./cogs'):
            if filename.startswith("__pycache__"):
                continue
            if filename.startswith("indev"):
                continue
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"{c[1]}----------------------{c[0]}\nLoaded {c[2]}{filename}")
            else:
                print(f"{c[1]}----------------------\n{c[3]}Error loading {c[2]}{filename}")

        await self.tree.sync()
        print(f"{c[1]}----------------------")
        print("Synced Slash Commands")
        print(f"{c[1]}----------------------")


#DEFINE BOT
bot = Bot()

#LOAD COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.channel.send(f"Loaded **{extension}.py** successfully!")


#UNLOAD COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.channel.send(f"Unloaded **{extension}.py** successfully!")


#RELOAD COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await bot.load_extension(f"cogs.{extension}")
    await ctx.channel.send(content=f"Reloaded **{extension}.py** successfully!")


#LOADINDEV COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def loadindev(ctx):
    for filename in os.listdir('./cogs/indev'):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.indev.{filename[:-3]}")
            await ctx.channel.send(f"Loaded **{filename}** successfully!")
            print(f"----------------------\nLoaded {filename}")
            await asyncio.sleep(1)


#UNLOADINDEV COG COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def unloadindev(ctx):
    for filename in os.listdir('./cogs/indev'):
        if filename.endswith(".py"):
            await bot.unload_extension(f"cogs.indev.{filename[:-3]}")
            await ctx.channel.send(f"Unloaded **{filename}** successfully!")
            print(f"----------------------\nLoaded {filename}")
            await asyncio.sleep(1)


#SHUTDOWN COMMAND
@bot.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await ctx.channel.send("Shutting down...")
    await bot.close()


#BOT STATUS
@bot.event
async def status_task():
    amount = len(bot.guilds)
    while True:
        await bot.change_presence(
            activity = discord.Game(name="Prefix: /")
            )
        await asyncio.sleep(120)
        await bot.change_presence(
            activity=discord.Game(name="beep boop")
            )
        await asyncio.sleep(120)
        await bot.change_presence(
            activity=discord.Game(name="Now supports Slash Commands!")
            )
        await asyncio.sleep(120)
        await bot.change_presence(
            activity=discord.Game(name=f"in {amount} servers!")
            )
        await asyncio.sleep(120)
        await bot.change_presence(
            activity=discord.Game(name="boop beep boop?")
            )
        await asyncio.sleep(120)
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="TeeTwoNot while he sleeps"
                )
            )
        await asyncio.sleep(120)

async def main():
    async with bot:
        bot.loop.create_task(serve(app, config))
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
