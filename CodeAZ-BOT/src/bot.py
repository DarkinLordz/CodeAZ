from path import CONFIG_JSON, XP_JSON
from discord.ext import commands
import discord
import random
import json
import math
import time
import asyncio
import aiohttp
import os
import tempfile
from log import logger

# -- Constants -- #

xp_cooldowns = {}

# -- XP Save Task -- #

async def save_xp_data():
    while True:
        await asyncio.sleep(10)
        async with xp_lock:
            with tempfile.NamedTemporaryFile(mode='w', dir=os.path.dirname(XP_JSON), delete=False, suffix='.tmp', encoding='utf-8') as temp_file:
                json.dump(xp_data, temp_file, indent=4)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_file.name, XP_JSON)

# -- Configuration -- #

with open(CONFIG_JSON, "r", encoding="utf-8") as file:
    config = json.load(file)

discord_token = config["bot"].get("token")
command_prefix = config["bot"].get("prefix")

# -- XP Data Caching -- #

xp_data = {}
xp_lock = asyncio.Lock()

if os.path.exists(XP_JSON):
    with open(XP_JSON, "r", encoding="utf-8") as file:
        xp_data = json.load(file)

if config["features"]["channel"].get("enabled"):
    channel = config["features"]["channel"].get("channelID")

if config["features"]["xp"].get("enabled"):
    xp_leaderboard_command = config["features"]["xp"].get("command")
    xp_cooldown = config["features"]["xp"].get("cooldown")

if config["features"]["xp"]["send"].get("enabled"):
    xp_send_command = config["features"]["xp"]["send"].get("command")
    xp_send_role = config["features"]["xp"]["send"].get("roleID")
    xp_send_cooldown = config["features"]["xp"]["send"].get("cooldown")
    xp_send_maximum = config["features"]["xp"]["send"].get("maximum")

if config["features"]["xp"]["role"].get("enabled"):
    xp_role_treshold = config["features"]["xp"]["role"].get("treshold")
    xp_role_role = config["features"]["xp"]["role"].get("roleID")

if config["features"]["xp"]["give"].get("enabled"):
    xp_give_command = config["features"]["xp"]["give"].get("command")
    xp_give_role = config["features"]["xp"]["give"].get("roleID")
    xp_give_cooldown = config["features"]["xp"]["give"].get("cooldown")
    xp_give_maximum = config["features"]["xp"]["give"].get("maximum")

if config["features"]["xp"]["bet"].get("enabled"):
    xp_bet_command = config["features"]["xp"]["bet"].get("command")
    xp_bet_role = config["features"]["xp"]["bet"].get("roleID")
    xp_bet_cooldown = config["features"]["xp"]["bet"].get("cooldown")
    xp_bet_maximum = config["features"]["xp"]["bet"].get("maximum")

if config["features"]["xp"]["daily"].get("enabled"):
    xp_daily_command = config["features"]["xp"]["daily"].get("command")
    xp_daily_maximum = config["features"]["xp"]["daily"].get("maximum")
    xp_daily_minimum = config["features"]["xp"]["daily"].get("minimum")
    xp_daily_role = config["features"]["xp"]["daily"].get("roleID")

if config["features"]["xp"]["event"].get("enabled"):
    xp_event_start_command = config["features"]["xp"]["event"].get("start_command")
    xp_event_stop_command = config["features"]["xp"]["event"].get("stop_command")
    xp_event_min_xppm = config["features"]["xp"]["event"].get("min_xppm")
    xp_event_max_xppm = config["features"]["xp"]["event"].get("max_xppm")
    xp_event_cooldown = config["features"]["xp"]["event"].get("cooldown")
    xp_event_role = config["features"]["xp"]["event"].get("roleID")

if config["features"]["help"].get("enabled"):
    help_command = config["features"]["help"].get("command")
    help_explanation = config["features"]["help"].get("explanation")

if config["features"]["welcome"].get("enabled"):
    welcome_channel = config["features"]["welcome"].get("channelID")
    welcome_message = config["features"]["welcome"].get("message")
    welcome_role = config["features"]["welcome"]["role"].get("roleID")

if config["features"]["goodbye"].get("enabled"):
    goodbye_channel = config["features"]["goodbye"].get("channelID")
    goodbye_message = config["features"]["goodbye"].get("message")

if config["features"]["meme"].get("enabled"):
    meme_command = config["features"]["meme"].get("command")
    meme_cooldown = config["features"]["meme"].get("cooldown")
    meme_nsfw = config["features"]["meme"].get("nsfw")

if config["features"]["reaction"]["role"].get("enabled"):
    reaction_role_channel = config["features"]["reaction"]["role"].get("channelID")
    reaction_role_message = config["features"]["reaction"]["role"].get("messageID")
    reaction_role = config["features"]["reaction"]["role"].get("roles")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None)

# -- Bot Events -- #

@bot.event
async def on_ready():
    logger.info(f"Bot is ready. Logged in as {bot.user}")
    # Start the XP save task
    bot.loop.create_task(save_xp_data())

# -- Functions -- #

# -- Channel -- #

if config["features"]["channel"].get("enabled"):
    @bot.check
    async def globally_check_channel(ctx):
        logger.debug(f"Checking if command is allowed in channel {ctx.channel.id}")
        return ctx.channel.id == channel
    
# -- Help -- #

if config["features"]["help"].get("enabled"):
    @bot.command(name=help_command)
    async def help(ctx, command: str = None):

        if "@" in command:
            return            
        
        default_explanation = help_explanation.get("default")

        if command is None:
            all_commands = [k for k in help_explanation.keys() if k != "default"]
            await ctx.reply("Mövcud əmrlər:\n" + "\n".join(all_commands))
        else:
            await ctx.reply(f"{command} - {help_explanation.get(command, default_explanation)}")

# -- Welcome -- #

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

# -- Goodbye -- #

if config["features"]["goodbye"].get("enabled"):
    @bot.event
    async def on_member_remove(member):
        logger.info(f"Member left: {member.name} (ID: {member.id})")
        channel = bot.get_channel(goodbye_channel)
        if channel:
            await channel.send(f"{goodbye_message}, <@{member.id}> 👋")

# -- Reaction Role -- #

if config["features"]["reaction"]["role"].get("enabled"):
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

# -- XP System -- #

if config["features"]["xp"].get("enabled"):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        now = time.time()

        last_xp_time = xp_cooldowns.get(user_id, 0)

        if now - last_xp_time < xp_cooldown:
            await bot.process_commands(message)
            return

        xp_cooldowns[user_id] = now

        async with xp_lock:
            xp_data[user_id] = xp_data.get(user_id, 0) + 1
            current_xp = xp_data[user_id]

        if config["features"]["xp"]["role"].get("enabled"):
            if current_xp >= xp_role_treshold:
                guild = message.guild
                member = message.author
                role = discord.utils.get(guild.roles, id=xp_role_role)
                if role and role not in member.roles:
                    await member.add_roles(role)
                    logger.info(f"Assigned role '{role.name}' to {member.name} for reaching {current_xp} XP")

        await bot.process_commands(message)

    @bot.command(name=xp_leaderboard_command)
    async def xp_leaderboard(ctx, member: discord.Member = None):
        async with xp_lock:
            if member:
                user_id = str(member.id)
                xp = xp_data.get(user_id, 0)

                sorted_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)

                rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), 0)
                await ctx.reply(f"\u200b{rank}. {member.display_name} - {xp} XP")
                return

            top_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)[:10]

        leaderboard = ""
        for i, (user_id, xp) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User ID {user_id}"
            leaderboard += f"{i}. {name} - {xp} XP\n"

        await ctx.reply(leaderboard)

    if config["features"]["xp"]["send"].get("enabled"):
        @bot.command(name=xp_send_command)
        @commands.cooldown(1, xp_send_cooldown, commands.BucketType.user)
        async def xp_send(ctx, amount: int, *members: discord.Member):
            if xp_send_role not in [r.id for r in ctx.author.roles]:
                await ctx.reply(f"Bu əmr üçün sizdə yetərli rol yoxdur!")
                xp_send.reset_cooldown(ctx)
                return

            if amount <= 0:
                await ctx.reply(f"Miqdar 0-dan çox olmalıdır.")
                xp_send.reset_cooldown(ctx)
                return

            if amount > xp_send_maximum:
                await ctx.reply(f"Miqdar {xp_send_maximum}-dan az olmalıdır.")
                xp_send.reset_cooldown(ctx)
                return

            async with xp_lock:
                for m in members:
                    xp_data[str(m.id)] = xp_data.get(str(m.id), 0) + amount
                
            logger.info(f"{ctx.author.name} sent {amount} XP to {[m.name for m in members]}")

            await ctx.reply(f"{amount} XP Göndərildi!")
        
        @xp_send.error
        async def xp_send_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                seconds_left = math.ceil(error.retry_after)
                await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")
    
    if config["features"]["xp"]["give"].get("enabled"):
        @bot.command(name=xp_give_command)
        @commands.cooldown(1, xp_give_cooldown, commands.BucketType.user)
        async def xp_give(ctx, amount: int, member: discord.Member):
            if xp_give_role not in [r.id for r in ctx.author.roles]:
                await ctx.reply(f"Bu əmr üçün sizdə yetərli rol yoxdur!")
                xp_give.reset_cooldown(ctx)
                return
            
            if amount <= 0:
                await ctx.reply(f"Miqdar 0-dan çox olmalıdır.")
                xp_give.reset_cooldown(ctx)
                return
            
            if amount > xp_give_maximum:
                await ctx.reply(f"Miqdar {xp_give_maximum}-dan az olmalıdır.")
                xp_give.reset_cooldown(ctx)
                return
            
            giver = str(ctx.author.id)
            receiver = str(member.id)

            async with xp_lock:
                if xp_data.get(giver, 0) < amount:
                    await ctx.reply(f"Sizdə kifayət qədər XP yoxdur.")
                    xp_give.reset_cooldown(ctx)
                    return

                xp_data[giver] -= amount
                xp_data[receiver] = xp_data.get(receiver, 0) + amount

            logger.info(f"{ctx.author.name} gave {amount} XP to {member.name}")

            await ctx.reply(f"{amount} XP Verildi!")

        @xp_give.error
        async def xp_give_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                seconds_left = math.ceil(error.retry_after)
                await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")

    if config["features"]["xp"]["bet"].get("enabled"):
        @bot.command(name=xp_bet_command)
        @commands.cooldown(1, xp_bet_cooldown, commands.BucketType.user)
        async def xp_bet(ctx, amount: int):
            if xp_bet_role not in [r.id for r in ctx.author.roles]:
                await ctx.reply(f"Bu əmr üçün sizdə yetərli rol yoxdur!")
                xp_bet.reset_cooldown(ctx)
                return
            
            if amount <= 0:
                await ctx.reply(f"Miqdar 0-dan çox olmalıdır")
                xp_bet.reset_cooldown(ctx)
                return

            if amount > xp_bet_maximum:
                await ctx.reply(f"Miqdar {xp_bet_maximum}-dan az olmalıdır.")
                xp_bet.reset_cooldown(ctx)
                return
            
            bettor = str(ctx.author.id)

            async with xp_lock:
                if xp_data.get(bettor, 0) < amount:
                    await ctx.reply(f"Sizdə kifayət qədər XP yoxdur.")
                    xp_bet.reset_cooldown(ctx)
                    return
                
                logger.info(f"{ctx.author.name} bet {amount}")

                winner = random.random() < 0.5

                if winner:
                    xp_data[bettor] += amount
                else:
                    xp_data[bettor] -= amount
            
            if winner:
                logger.info(f"{ctx.author.name} won {amount}")
            else:
                logger.info(f"{ctx.author.name} lost {amount}")

            await ctx.reply(f"{amount} XP {'Qazandın' if winner else 'Uduzdun'}!")
        
        @xp_bet.error
        async def xp_bet_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                seconds_left = math.ceil(error.retry_after)
                await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")

    if config["features"]["xp"]["daily"].get("enabled"):
        @bot.command(name=xp_daily_command)
        @commands.cooldown(1, 86400, commands.BucketType.user)
        async def xp_daily(ctx):
            if xp_daily_role not in [r.id for r in ctx.author.roles]:
                await ctx.reply(f"Bu əmr üçün sizdə yetərli rol yoxdur!")
                xp_daily.reset_cooldown(ctx)
                return
            
            user = str(ctx.author.id)
            amount = random.randint(xp_daily_minimum, xp_daily_maximum)

            async with xp_lock:
                xp_data[user] = xp_data.get(user, 0) + amount
            
            logger.info(f"{ctx.author.name} used daily and got {amount}")

            await ctx.reply(f"{amount} XP qazandın!")

        @xp_daily.error
        async def xp_daily_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                seconds_left = math.ceil(error.retry_after)
                await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")

    if config["features"]["xp"]["event"].get("enabled"):
        xp_event_active = False
        xp_event_vc_id = None
        xp_event_xppm = 0
        xp_event_task = None

        async def xp_event_loop(bot):
            global xp_event_active

            while xp_event_active:
                await asyncio.sleep(60)

                async with xp_lock:
                    for guild in bot.guilds:
                        vc = guild.get_channel(xp_event_vc_id)
                        if not vc:
                            continue

                        for member in vc.members:
                            if member.bot:
                                continue

                            user_id = str(member.id)
                            xp_data[user_id] = xp_data.get(user_id, 0) + xp_event_xppm

        @bot.command(name=xp_event_start_command)
        @commands.cooldown(1, xp_event_cooldown, commands.BucketType.user)
        async def xp_event_start(ctx, xppm: int, vc: int):
            if xp_event_role not in [r.id for r in ctx.author.roles]:
                await ctx.reply(f"Bu əmr üçün sizdə yetərli rol yoxdur!")
                xp_event_start.reset_cooldown(ctx)
                return

            global xp_event_active, xp_event_vc_id, xp_event_xppm, xp_event_task

            if xp_event_active:
                await ctx.reply("XP Event artıq aktivdir.")
                xp_event_start.reset_cooldown(ctx)
                return

            if not (xp_event_min_xppm <= xppm <= xp_event_max_xppm):
                await ctx.reply(f"XP / Dəqiqə {xp_event_min_xppm} ilə {xp_event_max_xppm} arasında olmalıdır.")
                xp_event_start.reset_cooldown(ctx)
                return

            channel = ctx.guild.get_channel(vc)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                await ctx.reply("Düzgün voice channel ID daxil edin.")
                xp_event_start.reset_cooldown(ctx)
                return

            xp_event_active = True
            xp_event_vc_id = vc
            xp_event_xppm = xppm

            xp_event_task = bot.loop.create_task(xp_event_loop(bot))

            logger.info(f"XP Event started by {ctx.author.name} | VC: {vc} | XPPM: {xppm}")

            await ctx.reply(f"XP Event başladı!\n" f"VC: <#{vc}>\n" f"XP / Dəqiqə: {xppm}")

        @bot.command(name=xp_event_stop_command)
        @commands.cooldown(1, xp_event_cooldown, commands.BucketType.user)
        async def xp_event_stop(ctx):
            if xp_event_role not in [r.id for r in ctx.author.roles]:
                await ctx.reply(f"Bu əmr üçün sizdə yetərli rol yoxdur!")
                xp_event_stop.reset_cooldown(ctx)
                return

            global xp_event_active, xp_event_task

            if not xp_event_active:
                await ctx.reply("Aktiv XP Event yoxdur.")
                xp_event_stop.reset_cooldown(ctx)
                return

            xp_event_active = False

            if xp_event_task:
                xp_event_task.cancel()
                xp_event_task = None

            logger.info(f"XP Event stopped by {ctx.author.name}")

            await ctx.reply("XP Event dayandırıldı.")

# -- Meme -- #

if config["features"]["meme"].get("enabled"):
    @bot.command(name=meme_command)
    @commands.cooldown(1, meme_cooldown, commands.BucketType.user)
    async def meme(ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                if resp.status != 200:
                    await ctx.reply(f"Zəhmət olmasa bir necə dəqiqə sonra təkrar cəhd edin.")
                    meme.reset_cooldown(ctx)
                    return
                data = await resp.json()
                if not meme_nsfw:
                    if data.get("nsfw") and not ctx.channel.is_nsfw():
                        return

        embed = discord.Embed(
            title=data.get("title", "Meme"),
            color=discord.Color.random()
        )
        embed.set_image(url=data.get("url"))
        embed.set_footer(text=f"r/{data.get('subreddit', 'unknown')}")

        logger.info(f"{ctx.author.name} requested a meme")

        await ctx.reply(embed=embed)

    @meme.error
    async def meme_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds_left = math.ceil(error.retry_after)
            await ctx.reply(f"Bu əmri təkrar etmək üçün {seconds_left} saniyə gözləməlisiniz!")

bot.run(discord_token)
