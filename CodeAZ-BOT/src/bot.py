from path import CONFIG_JSON, XP_JSON
from discord.ext import commands
import discord
import json
from log import logger

"""
Please make sure your code works properly and follows the existing style of the project before submitting a pull request.
I appreciate all contributions in advance, thank you for helping improve this project.
"""

with open(CONFIG_JSON, "r", encoding="utf-8") as file:
    config = json.load(file)

discord_token = config["bot"].get("token")
command_prefix = config["bot"].get("prefix")

if config["features"]["channel"].get("enabled"):
    channel = config["features"]["channel"].get("channelID")

if config["features"]["xp"]["send"].get("enabled"):
    xp_send_role = config["features"]["xp"]["send"].get("roleID")
    xp_send_cooldowon = config["features"]["xp"]["send"].get("cooldown")

if config["features"]["welcome"].get("enabled"):
    welcome_channel = config["features"]["welcome"].get("channelID")
    welcome_message = config["features"]["welcome"].get("message")
    if config["features"]["welcome"].get("roleID"):
        welcome_role = config["features"]["welcome"].get("roleID")

if config["features"]["reactionroles"].get("enabled"):
    reaction_role_channel = config["features"]["reactionroles"].get("channelID")
    reaction_role_message = config["features"]["reactionroles"].get("messageID")
    reaction_role = config["features"]["reactionroles"].get("roles")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None)

if config["features"]["channel"].get("enabled"):
    @bot.check
    async def globally_check_channel(ctx):
        logger.debug(f"Checking if command is allowed in channel {ctx.channel.id}")
        return ctx.channel.id == channel

if config["features"]["welcome"].get("enabled"):
    @bot.event
    async def on_member_join(member):
        logger.info(f"New member joined: {member.name} (ID: {member.id})")
        channel = bot.get_channel(welcome_channel)
        if channel:
            await channel.send(f"{welcome_message}, {member.mention} 🎉")
        if config["features"]["welcome"].get("roleID"):
            role = discord.utils.get(member.guild.roles, id=welcome_role)
            if role:
                await member.add_roles(role)
                logger.info(f"Assigned role '{role.name}' to {member.name}")

if config["features"]["reactionroles"].get("enabled"):
    @bot.event
    async def on_raw_reaction_add(payload):
        logger.debug(f"Reaction added: {payload.emoji} by user {payload.user_id}")
        if payload.message_id != reaction_role_message:
            return
        
        guild = bot.get_guild(payload.guild_id)
        role_id = reaction_role.get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)
                logger.info(f"Assigned role '{role.name}' to {member.name} for reaction {payload.emoji}")

    @bot.event
    async def on_raw_reaction_remove(payload):
        logger.debug(f"Reaction removed: {payload.emoji} by user {payload.user_id}")
        if payload.message_id != reaction_role_message:
            return

        guild = bot.get_guild(payload.guild_id)
        role_id = reaction_role.get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)
                logger.info(f"Removed role '{role.name}' from {member.name} for reaction {payload.emoji}")

if config["features"]["xp"].get("enabled"):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        with open(XP_JSON, "r", encoding="utf-8") as file:
            xp_data = json.load(file)

        user_id = str(message.author.id)
        xp_data[user_id] = xp_data.get(user_id, 0) + 1

        with open(XP_JSON, "w", encoding="utf-8") as file:
            json.dump(xp_data, file, indent=4)

        await bot.process_commands(message)

    @bot.command(name="xp")
    async def xp_leaderboard(ctx, member: discord.Member = None):
        with open(XP_JSON, "r", encoding="utf-8") as file:
            xp_data = json.load(file)

        if member:
            user_id = str(member.id)
            xp = xp_data.get(user_id, 0)

            sorted_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)

            rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), 0)
            await ctx.send(f"\u200b{rank}. {member.display_name} - {xp} XP")
            return

        top_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)[:10]

        leaderboard = ""
        for i, (user_id, xp) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User ID {user_id}"
            leaderboard += f"{i}. {name} — {xp} XP\n"

        await ctx.send(leaderboard)

    if config["features"]["xp"]["send"].get("enabled"):
        @bot.command(name="xpsend")
        @commands.cooldown(1, xp_send_cooldowon, commands.BucketType.user)
        async def xpsend(ctx, amount: int, *members: discord.Member):
            if xp_send_role not in [r.id for r in ctx.author.roles]:
                return

            with open(XP_JSON, "r", encoding="utf-8") as f:
                xp = json.load(f)

            for m in members:
                xp[str(m.id)] = xp.get(str(m.id), 0) + amount

            with open(XP_JSON, "w", encoding="utf-8") as f:
                json.dump(xp, f, indent=4)
                
            logger.info(f"{ctx.author.name} sent {amount} XP to {[m.name for m in members]}")

bot.run(discord_token)
