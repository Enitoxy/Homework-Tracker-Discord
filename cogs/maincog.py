import discord
import pymongo
import os
import random
from typing import List
from bson import ObjectId, errors

from discord import app_commands, ui
from discord.ext import commands

from dotenv import load_dotenv
from datetime import datetime
now = datetime.now()


#DOTENV
load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_CLUSTER = os.getenv('DB_CLUSTER')


mdbclient = pymongo.MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_CLUSTER}.mongodb.net/?retryWrites=true&w=majority")
registered_ids = mdbclient.registered_ids


#ADD MODAL CLASS
class addHW(ui.Modal, title="Add your homework!"):

    hwtitle = ui.TextInput(label="Title", style=discord.TextStyle.short, placeholder="Add a title!", required=True)
    subject = ui.TextInput(label="Subject", style=discord.TextStyle.short, placeholder="What subject?", required=True)
    description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, placeholder="Give a description (optional)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        result = registered_ids.homework.insert_one(
            {
                "title": str(self.hwtitle),
                "subject": str(self.subject),
                "description": str(self.description),
                "complete": bool(False),
                "date": str(now.strftime("%d/%m/%Y %H:%M")),
                "author": interaction.user.id
            }
        )
        id = result.inserted_id
        await interaction.response.send_message(f"Homework added successfully!\n> Unique ID: {id}", ephemeral=True)


#Pagination stuff (of which I understand absolutely nothing)
"""class PaginationView(discord.ui.View):
    def __init__(self, pages:list, timeout:None):
        super().__init__(timeout=timeout)

        self.current_page=0
        self.pages = pages
        
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1

    @discord.ui.button(label="Mark Complete", style=discord.ButtonStyle.green)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()"""


#COG CLASS
class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    #PING COMMAND
    #REPURPOSE AS DEVINFO COMMAND
    @app_commands.command(name="ping", description="Shows the latency of the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Ping: {0}ms'.format(round(self.bot.latency, 3)), ephemeral=False)

    #Needs fixing. A lot of fixing.
    """@app_commands.command(name="myhomework", description="Lists all of your homework!")
    #Has a (Mark Complete) button - DONE
    #Has a (Delete) button - DONE
    #Stuff that didn't make sense - DONE (NESTED DICTS)
    async def myhomework(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        pagination_view = PaginationView()
        pagination_view.data = idlist

        idlist = []
        author = interaction.user.id
        key = {'author': author}
        doc={}

        for document in registered_ids.homework.find(key):
            idlist.append(str(document['_id'])) #Gets author's documents' IDs

            # Adds a dict per _id (named as _id) in doc dict
            doc[str(document['_id'])] = dict(

                title = document['title'],
                subject = document['subject'],
                description = document['description'],
                complete = document['complete'],
                date = document['date'],
                _id = document['_id']

            )

        embed = discord.Embed(title='Your Homework')
        embed.add_field(name='Title:', value=doc['63dadc4c641286815985fcb5']['title'], inline=False)
        embed.add_field(name='Subject:', value=doc['subject'], inline=False)
        embed.add_field(name='Description:', value=doc['description'], inline=False)
        embed.add_field(name='Complete:', value=doc['complete'], inline=False)
        embed.add_field(name='Date:', value=doc['date'], inline=False)
        embed.add_field(name='ID:', value=doc['_id'], inline=False)
        await interaction.followup.send(embed=embed)"""


    @app_commands.command(name="add", description="Adds homework to your list!")
    async def add(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(addHW())

    @app_commands.command(name="search", description="Searches homework by ID!")
    async def search(self, interaction: discord.Interaction, id: str) -> None:
        await interaction.response.defer(ephemeral=True)
        obj = ObjectId(id)
        key = {'_id': obj}
        author = interaction.user.id

        for document in registered_ids.homework.find(key):
            title = document['title']
            subject = document['subject']
            description = document['description']
            complete = document['complete']
            date = document['date']
            authorid = document['author']
            
        if author != authorid:
            await interaction.followup.send("The ID doesn't exist or the ID isn't yours!")

        else:
            embed = discord.Embed(title=f'Your Homework - ID: {id}', color=0xffffff)
            embed.add_field(name='Title:', value=title, inline=False)
            embed.add_field(name='Subject:', value=subject, inline=False)
            embed.add_field(name='Description:', value=description, inline=False)
            embed.add_field(name='Complete:', value=complete, inline=False)
            embed.add_field(name='Date:', value=date, inline=False)
            embed.add_field(name='ID:', value=id, inline=False)
            await interaction.followup.send(embed=embed)
        
    
    @search.error
    async def search_error(self, interaction: discord.Interaction, error: errors.InvalidId):
        if isinstance(error, BaseException):
            embed = discord.Embed(
                title="Oops!",
                description="The ID you entered is invalid!",
                color=0xffffff
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MainCog(bot))