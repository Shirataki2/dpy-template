import discord
from discord import app_commands
from discord.ui import TextInput
from discord.ext import commands
import src.core.bot

class Counter(discord.ui.View):
    value = 0

    @discord.ui.button(label="-", style=discord.ButtonStyle.primary)
    async def decrement(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value -= 1
        await interaction.response.edit_message(content=f"Count: {self.value}", view=self)

    @discord.ui.button(label="+", style=discord.ButtonStyle.primary)
    async def increment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value += 1
        await interaction.response.edit_message(content=f"Count: {self.value}", view=self)

class Modal(discord.ui.Modal, title="Modal Title"):
    name: TextInput = TextInput(label="Name", placeholder="Enter your name")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Hello, {self.name.value}!")

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command()
    async def greet(self, it: discord.Interaction):
        """
        Greet the user
        """
        username = it.user.name
        await it.response.send_message(f"Hello, {username}!")

    @app_commands.command()
    @app_commands.describe(
        a="The first number",
        b="The second number"
    )
    async def add(self, it: discord.Interaction, a: int, b: int):
        """
        Add two numbers
        """
        await it.response.send_message(f"{a} + {b} = {a + b}")

    @app_commands.command()
    async def count(self, it: discord.Interaction):
        """ Count """
        await it.response.send_message("Count: 0", view=Counter())

    @app_commands.command()
    async def modal(self, it: discord.Interaction):
        """ Modal """
        await it.response.send_modal(Modal())
        it.response

async def setup(bot: src.core.bot.Bot):
    @bot.tree.context_menu()
    async def join(it: discord.Interaction, member: discord.Member):
        """
        Join a user to your server
        """
        await it.response.send_message(f"Joining {member.name} to your server...")
    
    guilds = [bot.dev_server_id]
    if bot.conf.dev:
        await bot.add_cog(Test(bot), guilds=guilds) # type: ignore
    else:
        await bot.add_cog(Test(bot))
    