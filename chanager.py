'''Written by Cael Shoop.'''

import os
import logging
from dotenv import load_dotenv
from discord import app_commands, Interaction, Intents, Client, CategoryChannel, MessageType, Message


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


@client.tree.command(name="movechannel", description="Move this channel to another category.")
@app_commands.describe(category="Category to move this channel into.")
async def movechannel_command(interaction: Interaction, category: CategoryChannel):
    logger.info(f"Received channel move request from {interaction.user.name}: {category.name} ({category.id})")
    try:
        await interaction.channel.edit(category=category)
        await interaction.response.send_message(content=f"Channel moved to {category.name}.", ephemeral=True)
    except Exception as e:
        logger.error(f"Failed to move channel: {e}")
        await interaction.response.send_message(content=f"Could not move channel: {e}", ephemeral=True)


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
