from path import CONFIG_JSON, XP_JSON
from discord.ext import commands
import discord
import random
import json
import math
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

if config["features"]["xp"]["role"].get("enabled"):
    xp_role_treshold = config["features"]["xp"]["role"].get("treshold")
    xp_role_role = config["features"]["xp"]["role"].get("roleID")

if config["features"]["xp"]["give"].get("enabled"):
    xp_give_role = config["features"]["xp"]["give"].get("roleID")
    xp_give_cooldown = config["features"]["xp"]["give"].get("cooldown")

if config["features"]["xp"]["bet"].get("enabled"):
    xp_bet_role = config["features"]["xp"]["bet"].get("roleID")
    xp_bet_cooldown = config["features"]["xp"]["bet"].get("cooldown")

if config["features"]["welcome"].get("enabled"):
    welcome_channel = config["features"]["welcome"].get("channelID")
    welcome_message = config["features"]["welcome"].get("message")
    welcome_role = config["features"]["welcome"]["role"].get("roleID")

if config["features"]["reaction"].get("role")["enabled"]:
    reaction_role_channel = config["features"]["reaction"]["role"].get("channelID")
    reaction_role_message = config["features"]["reaction"]["role"].get("messageID")
    reaction_role = config["features"]["reaction"]["role"].get("roles")

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
        if config["features"]["welcome"]["role"].get("enabled"):
            role = discord.utils.get(member.guild.roles, id=welcome_role)
            if role:
                await member.add_roles(role)
                logger.info(f"Assigned role '{role.name}' to {member.name}")

if config["features"]["reaction"].get("role")["enabled"]:
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
        current_xp = xp_data[user_id]

        with open(XP_JSON, "w", encoding="utf-8") as file:
            json.dump(xp_data, file, indent=4)

        if current_xp >= xp_role_treshold:
            guild = message.guild
            member = message.author
            role = discord.utils.get(guild.roles, id=xp_role_role)
            if role and role not in member.roles:
                await member.add_roles(role)
                logger.info(f"Assigned role '{role.name}' to {member.name} for reaching {current_xp} XP")

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
            leaderboard += f"{i}. {name} - {xp} XP\n"

        await ctx.send(leaderboard)

    if config["features"]["xp"]["send"].get("enabled"):
        @bot.command(name="xp-send")
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

            await ctx.reply(f"{amount} XP Uğurla Göndərildi!")
    
    if config["features"]["xp"]["give"].get("enabled"):
        @bot.command(name="xp-give")
        @commands.cooldown(1, xp_give_cooldown, commands.BucketType.user)
        async def xp_give(ctx, amount: int, member: discord.Member):
            if xp_give_role not in [r.id for r in ctx.author.roles]:
                return
            
            if amount <= 0:
                return
            
            with open(XP_JSON, "r", encoding="utf-8") as file:
                xp = json.load(file)

            giver = str(ctx.author.id)
            receiver = str(member.id)

            if xp.get(giver, 0) < amount:
                return

            xp[giver] -= amount
            xp[receiver] = xp.get(receiver, 0) + amount

            with open(XP_JSON, "w", encoding="utf-8") as file:
                json.dump(xp, file, indent=4)

            logger.info(f"{ctx.author.name} gave {amount} XP to {member.name}")

            await ctx.reply(f"{amount} XP Uğurla Verildi!")

    if config["features"]["xp"]["bet"].get("enabled"):
        @bot.command(name="xp-bet")
        @commands.cooldown(1, xp_bet_cooldown, commands.BucketType.user)
        async def xp_bet(ctx, amount: int):
            if xp_bet_role not in [r.id for r in ctx.author.roles]:
                return
            
            if amount <= 0:
                return

            if amount > 1000:
                ctx.reply("Maksimum mərc miqdarı 1000 XP-dir!")
                return
            
            with open(XP_JSON, "r", encoding="utf-8") as file:
                xp = json.load(file)

            bettor = str(ctx.author.id)

            if xp.get(bettor, 0) < amount:
                return
            
            logger.info(f"{ctx.author.name} bet {amount}")

            winner = random.choice([True, False])

            if winner:
                xp[bettor] += amount
            else:
                xp[bettor] -= amount

            with open(XP_JSON, "w", encoding="utf-8") as file:
                json.dump(xp, file, indent=4)
            
            if winner:
                logger.info(f"{ctx.author.name} won {amount}")
            else:
                logger.info(f"{ctx.author.name} lost {amount}")

            await ctx.reply(f"{amount} XP {'Qazandın' if winner else 'Uduzdun'}!")

    @xpsend.error
    async def xp_send_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds_left = math.ceil(error.retry_after)
            await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")

    @xp_give.error
    async def xp_give_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds_left = math.ceil(error.retry_after)
            await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")
        
    @xp_bet.error
    async def xp_bet_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds_left = math.ceil(error.retry_after)
            await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")

bot.run(discord_token)
