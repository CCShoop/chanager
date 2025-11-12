'''Written by Cael Shoop.'''

import os
import logging
from dotenv import load_dotenv
from discord import app_commands, Interaction, Intents, Client, TextChannel, Guild, SelectOption, MessageType, Message
from discord.ui import View, Select


# .env
load_dotenv()

# Logger setup
logger = logging.getLogger("Chanager")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="[Chanager] [%(asctime)s] [%(levelname)s\t] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("chanager.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class CategoriesSelect(Select):
    def __init__(self, channel: TextChannel, guild: Guild):
        self.channel = channel
        self.guild = guild
        options = [SelectOption(label=category.name, value=str(category.id)) for category in self.guild.categories]
        super().__init__(placeholder='Category', options=options)

    async def callback(self, interaction: Interaction):
        try:
            selected_category_id = int(self.values[0])
            logger.info(f"Category selected by {interaction.user}: {selected_category_id}")
            selected_category = self.guild.get_channel(selected_category_id)
            await self.channel.edit(category=selected_category)
            await interaction.response.send_message(f"Channel moved to {selected_category.name}.", ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to move channel: {e}")
            await interaction.response.send_message(content=f"Could not move channel: {e}", ephemeral=True)


class CategoriesSelectView(View):
    def __init__(self, channel: TextChannel, guild: Guild):
        super().__init__()
        self.add_item(CategoriesSelect(channel, guild))


class ChanagerClient(Client):
    def __init__(self, intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
client = ChanagerClient(intents=Intents.all())


@client.event
async def on_ready():
    logger.info(f"{client.user} is ready!")


@client.event
async def on_message(message: Message):
    if message.type == MessageType.pins_add:
        await message.delete()


@client.tree.command(name="move", description="Move this channel to another category.")
async def move_command(interaction: Interaction):
    logger.info(f"Received channel move request from {interaction.user.name}")
    await interaction.response.send_message(content="Select a category for the channel to be moved into from the dropdown.", view=CategoriesSelectView(interaction.channel, interaction.guild), ephemeral=True)


@client.tree.command(name="edit", description="Edit the name or topic of this channel.")
@app_commands.describe(name="New name for the channel.")
@app_commands.describe(topic="New topic for the channel.")
async def edit_command(interaction: Interaction, name: str = "", topic: str = ""):
    logger.info(f'Received channel edit request from {interaction.user.name}')
    if name == "" and topic == "":
        await interaction.response.send_message(content="You must provide a new name or topic for the channel.", ephemeral=True)
        return

    content = ""
    if name == "":
        name = interaction.channel.name
    else:
        content += "Channel name updated!\n"
    if topic == "":
        topic = interaction.channel.topic
    else:
        content += "Channel topic updated!\n"

    try:
        await interaction.channel.edit(name=name, topic=topic)
        await interaction.response.send_message(content=content, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(content=f"Channel edit failed: {e}", ephemeral=True)


client.run(DISCORD_TOKEN)
