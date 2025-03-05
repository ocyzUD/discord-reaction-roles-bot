import discord
from discord.ext import commands
from discord import Embed, TextChannel

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

reaction_roles = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()  

@bot.tree.command(name="setup", description="Set up reaction roles for a channel and role")
async def setup(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role, emojis: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need admin permissions to set up reaction roles.", ephemeral=True)
        return

    emoji_list = emojis.split()
    if not emoji_list:
        await interaction.response.send_message("You must provide at least one emoji.", ephemeral=True)
        return

    embed = Embed(title="Reaction Roles Setup", description="React to this message to get the role!")

    existing_message = None
    async for message in channel.history(limit=5):  
        if message.embeds and message.embeds[0].title == "Reaction Roles Setup":
            existing_message = message
            break

    if not existing_message:
        message = await channel.send(embed=embed)
    else:
        message = existing_message

    reaction_roles[message.id] = {
        "role": role,
        "emojis": emoji_list
    }

    for emoji in emoji_list:
        await message.add_reaction(emoji)

    await interaction.response.send_message(f"Reaction roles set up! React with the emojis to get the {role.name} role in {channel.mention}.", ephemeral=True)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    message_id = payload.message_id
    if message_id in reaction_roles:
        emoji = str(payload.emoji)
        role_data = reaction_roles[message_id]
        if emoji in role_data["emojis"]:
            role = role_data["role"]
            member = payload.member
            if role not in member.roles:
                await member.add_roles(role)
                await member.send(f"You've been given the {role.name} role!")

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return

    message_id = payload.message_id
    if message_id in reaction_roles:
        emoji = str(payload.emoji)
        role_data = reaction_roles[message_id]
        if emoji in role_data["emojis"]:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = role_data["role"]
            if member and role in member.roles:
                await member.remove_roles(role)
                await member.send(f"Your {role.name} role has been removed.")

bot.run("BOT_TOKEN_HERE")
