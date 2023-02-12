import discord
import pymongo
import os
from typing import List
from bson import ObjectId, errors
from collections import deque

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


class PaginatorView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]) -> None:
        super().__init__(timeout=30)

        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self.children[0].disabled = True
        self._queue[0].set_footer(text=f"Page {self._current_page}/{self._len}")

    async def update_buttons(self, interaction: discord.Interaction) -> None:
        for i in self._queue:
            i.set_footer(text=f"Page {self._current_page}/{self._len}")
        self._queue[0].set_footer(text=f"Page {self._current_page}/{self._len}")
        if self._current_page == self._len:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        if self._current_page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        await interaction.message.ed(view=self)

    
    @discord.ui.button(label="Previous")
    async def previous(self, interaction: discord.Interaction, _):
        self._queue.rotate(-1)
        embed = self._queue[0]
        self._current_page -= 1
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Next")
    async def next(self, interaction: discord.Interaction, _):
        self._queue.rotate(1)
        embed = self._queue[0]
        self._current_page += 1
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    #DELETE & MARK COMPLETE BUTTONS

    @property
    def initial(self) -> discord.Embed:
        return self._initial


#COG CLASS
class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    
    #PING COMMAND
    #REPURPOSE AS DEVINFO COMMAND
    @app_commands.command(name="ping", description="Shows the latency of the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Ping: {0}ms'.format(round(self.bot.latency, 3)), ephemeral=False)

    #MYHOMEWORK COMMAND
    @app_commands.command(name="myhomework", description="Lists all of your homework!")
    async def myhomework(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        embeds = []
        doc={}
        idlist = []
        index = -1
        author = interaction.user.id
        key = {'author': author}

        for document in registered_ids.homework.find(key):
            index = index + 1
            idlist.append(str(document['_id']))

            doc[str(document['_id'])] = dict(
                title = document['title'],
                subject = document['subject'],
                description = document['description'],
                complete = document['complete'],
                date = document['date'],
                _id = document['_id']
            )

            embed = discord.Embed(title=f'Your Homework')
            embed.add_field(name='Title:', value=doc[f'{idlist[index]}']['title'], inline=False)
            embed.add_field(name='Subject:', value=doc[f'{idlist[index]}']['subject'], inline=False)
            embed.add_field(name='Description:', value=doc[f'{idlist[index]}']['description'], inline=False)
            embed.add_field(name='Complete:', value=doc[f'{idlist[index]}']['complete'], inline=False)
            embed.add_field(name='Date:', value=doc[f'{idlist[index]}']['date'], inline=False)
            embed.add_field(name='ID:', value=doc[f'{idlist[index]}']['_id'], inline=False)

            embeds.append(embed)
        
        view = PaginatorView(embeds)
        await interaction.followup.send(embed=view.initial, view=view)


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
            embed = discord.Embed(
                title="Oops!",
                description="You don't have homework with this ID!",
                color=0xffffff
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

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