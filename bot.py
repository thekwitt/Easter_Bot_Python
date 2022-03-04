import discord, random, asyncio, asyncpg, os, os.path
from database.updates import Database_Methods
from glob import glob
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext.tasks import loop
from Extras.discord_functions import extra_functions


# Setting up Tokens and Passwords
TOKEN = open("token",'r').read()
PG_PW = open("PG_PW",'r').read()

# Creating Bot
prefixes = ['e!','E!']
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = prefixes,intents=intents, case_insensitive=True)
bot.ready = False
bot.prefix = 'e!'
bot.levelrequirements = [0,2,5,9,14,20,29]
bot.remove_command('help')
with open('versions.txt',encoding='utf-8', mode = 'r') as f:
    lines = f.readlines()
    bot.bot_version = lines[0].rstrip('\n')
    bot.db_version = lines[1].rstrip('\n')

bot.owner = 198305088203128832
# Create Pool for Postgresql
async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(database = "easter",user="postgres",password=PG_PW)

@bot.command(name = 'updatedb', hidden = True)
@commands.is_owner()
async def update_db(ctx):
    extra_functions.logger_print("Updating Databases")
    await Database_Methods.update_database(bot)
    extra_functions.logger_print("Updating Databases Completed!")
    
#reload cogs method
@bot.command(name = 'recog', hidden = True)
@commands.is_owner()
async def recoggers(ctx):
    bot.ready = False
    await ctx.send("Recogging In Process!")
    extra_functions.logger_print("Recogging!")
    COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")]
    for cog in COGS: 
        try:
            bot.reload_extension(f"cogs.{cog}")
            extra_functions.logger_print(f" {cog} cog loaded")
        except Exception as e:
            try:
                bot.reload_extension(f"cogs.{cog[7:]}")
                extra_functions.logger_print(f" {cog} cog loaded")
            except Exception as e:
                print(str(e), " for recoggers")
    extra_functions.logger_print("Cogs Done!")
    await ctx.send("Recogging Complete!")
    bot.ready = True

@recoggers.error
async def recoggers_command_error(ctx,error):
    if isinstance(error,discord.ext.commands.errors.NotOwner):
        return
    elif isinstance(error,discord.ext.commands.ExtensionNotFound):
        extra_functions.logger_print("Recogging Not Found!")
    elif isinstance(error,discord.ext.commands.ExtensionNotLoaded):
        extra_functions.logger_print("Recogging Done!")
    elif isinstance(error,discord.ext.commands.ExtensionFailed):
        extra_functions.logger_print("Recogging Not Found!")
    elif isinstance(error,discord.ext.commands.NoEntryPointError):
        extra_functions.logger_print("Recogging Done!")
        
    await ctx.send("Recogging Incomplete!")


# Method For Loading Cogs
def coggers():
    extra_functions.logger_print("Getting Cogs")
    COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")]

    try:
        for cog in COGS:
            bot.load_extension(f"cogs.{cog}")
            extra_functions.logger_print(f" {cog} cog loaded")
        extra_functions.logger_print("Cogs Done!")
    except Exception as e:
        try:
            for cog in COGS:
                bot.load_extension(f"cogs.{cog[7:]}")
                extra_functions.logger_print(f" {cog} cog loaded")
            extra_functions.logger_print("Cogs Done!")
        except Exception as e:
            print(str(e), " for recoggers")

def coggers_error(error):
    if isinstance(error,discord.ext.commands.ExtensionNotFound):
        extra_functions.logger_print("Recogging Not Found!")
    elif isinstance(error,discord.ext.commands.ExtensionAlreadyLoaded):
        extra_functions.logger_print("Recogging Done!")
    elif isinstance(error,discord.ext.commands.ExtensionFailed):
        extra_functions.logger_print("Recogging Not Found!")
    elif isinstance(error,discord.ext.commands.NoEntryPointError):
        extra_functions.logger_print("Recogging Done!")


# Setting Up Tables to be created for new bot and new servers
async def startup_create_tables():
    await bot.pg_con.execute(
        """ 
        CREATE TABLE IF NOT EXISTS guild_settings(
            Guild_ID bigint PRIMARY KEY,
            Version TEXT,
            Purification_Count INTEGER[] DEFAULT '{0,0,0,0,0,0}',
            Default_Server_Settings text[] DEFAULT '{"3","3","500"}',
            Default_Message_Settings text[] DEFAULT '{"300","10","True","True","5"}',
            Active_Message_Settings INTEGER[] DEFAULT '{300,10}',
            Possible_Channel_IDs bigint[] DEFAULT '{}',
            Message_State integer DEFAULT -3
        );
        """
        # Guild ID -> Server ID
        # Server Settings -> Cooldown Adjuster
        # Message Settings -> Next Message, Message Amount, Outside Messages Allowed, Main Chat Mode -> Active Message Settigns, Amount of People Per Egg Cluster, Amount of Egg Clusters Per Guild
        # Version -> Database Version
    )
    # Create Table for Heart Messages
    await bot.pg_con.execute(
        """
        CREATE TABLE IF NOT EXISTS egg_messages(
            Message_ID bigint PRIMARY KEY,
            Guild_ID bigint DEFAULT 0,
            Claimed_Users bigint[] DEFAULT '{}',
            Current_Channel bigint DEFAULT 0,
            Timeout_Message bigint DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS basket_messages(
            Message_ID bigint PRIMARY KEY,
            User_ID bigint DEFAULT 0,
            Target_ID bigint DEFAULT 0,
            Guild_ID bigint DEFAULT 0,
            page INTEGER DEFAULT 0,
            Timeout_Message bigint DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS role_lb_messages(
            Message_ID bigint PRIMARY KEY,
            User_ID bigint DEFAULT 0,
            Guild_ID bigint DEFAULT 0,
            page INTEGER DEFAULT 0,
            Timeout_Message bigint DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS collection_lb_messages(
            Message_ID bigint PRIMARY KEY,
            User_ID bigint DEFAULT 0,
            Guild_ID bigint DEFAULT 0,
            page INTEGER DEFAULT 0,
            Timeout_Message bigint DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS history_lb_messages(
            Message_ID bigint PRIMARY KEY,
            User_ID bigint DEFAULT 0,
            Guild_ID bigint DEFAULT 0,
            page INTEGER DEFAULT 0,
            Timeout_Message bigint DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS trade_messages(
            Message_ID bigint PRIMARY KEY,
            Current_Channel bigint DEFAULT 0,
            User_IDs bigint[] DEFAULT '{0,0}',
            Guild_ID bigint DEFAULT 0,
            Egg_IDs text[] DEFAULT '{"0","0"}',
            Timeout_Message bigint DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS server_stats(
            Guild_ID bigint PRIMARY KEY,
            Eggs_Collected INTEGER DEFAULT 0,
            Areas_Explored INTEGER[] DEFAULT '{0,0,0,0,0,0,0}',
            Eggs_Sold INTEGER DEFAULT 0,
            Trades_Count INTEGER DEFAULT 0, 
            Lottery_Results INTEGER[] DEFAULT '{0,0}', 
            Mailbox_Openings INTEGER DEFAULT 0,
            Cluster_Spawns INTEGER DEFAULT 0,
            Upgrades INTEGER DEFAULT 0
        );
        """
    )
    
    for guild in bot.guilds:        
        await bot.pg_con.execute(
            """
            CREATE TABLE IF NOT EXISTS """ + "g_" + str(guild.id) + """(
                UserID bigint PRIMARY KEY,
                Gold_Coins INTEGER DEFAULT 0,
                Basket_Level INTEGER DEFAULT 0,
                Basket_Eggs text[] DEFAULT '{}',
                Case_Eggs text[] DEFAULT '{}',
                Collection_Eggs text[] DEFAULT '{}',
                Eggs_Collected INTEGER DEFAULT 0,
                CD_Explorer INTEGER[] DEFAULT '{0,0,0,0,0,0,0}',
                CD_Explorer_Global INTEGER DEFAULT 0,
                CD_Mailbox INTEGER DEFAULT 0,
                Clusters INTEGER DEFAULT 0
            );
            """
        )

# Insert Missing Data Into Database
async def Insert_Missing_Data():
    for guild in bot.guilds:
        await bot.pg_con.execute("""INSERT INTO guild_settings (Guild_ID,Version) VALUES ($1,$2) ON CONFLICT (Guild_ID) DO NOTHING;""",guild.id,bot.db_version)
        await bot.pg_con.execute("""INSERT INTO server_stats (Guild_ID) VALUES ($1) ON CONFLICT (Guild_ID) DO NOTHING;""",guild.id)
        settings = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",guild.id)
        if settings['message_state'] == -3:
            embedVar = discord.Embed(title="📕  A New Adventure Awaits!  📕", description="⠀\nLooks like you are ready for a new adventure! To begin, please use **" + bot.prefix + "start** anywhere to activate the bot!\n⠀", color=0x16C326)
            embedVar.set_footer(text = "If you encounter any problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            
            channel = None
            channel = await extra_functions.check_for_main_channel(guild)
            if channel != None:
                await extra_functions.send_embed_channel(bot,channel,embedVar,999,"guild join welcome message send")
            await bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE guild_id = $2",-2,guild.id)
        #await bot.pg_con.execute("""INSERT INTO heart_messages (Guild_ID,Version) VALUES ($1,$2) ON CONFLICT (Guild_ID) DO NOTHING;""",guild.id,bot.db_version)
        #message_row = await bot.pg_con.fetchrow("SELECT * FROM heart_messages WHERE Guild_ID = $1;",guild.id)
        #channels = message_row["possible_channel_ids"]
        """
        if(len(channels) == 0):
            await bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",-1,guild.id) #Update Loved
        else:
            await bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",0,guild.id) #Update Loved
        """
    await Database_Methods.update_database(bot)

@bot.event
async def on_command_error(ctx, error):
    pass

@bot.event
async def on_message(message):
    if bot.ready:
        # If member doesnt exist
        try:
            if await bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(message.guild.id) + " WHERE UserID = $1",message.author.id) == None and not message.author.bot:
                await Database_Methods.Insert_User(bot,message.guild.id,message.author.id)
        except asyncpg.exceptions.UndefinedTableError:
            return
        
        if "fix your bot" in message.content.lower() or "fix the bot" in message.content.lower():
            await message.add_reaction('<:nou:827055326197055530>')

        settings = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",message.guild.id)
        
        if settings["message_state"] == -2:
            if "start" in message.content.lower()[2:] or "help" in message.content.lower()[2:]:
                await bot.process_commands(message)
            elif "e!" in message.content.lower()[:2]:
                embed = extra_functions.embedBuilder("⚠️   You haven't started the bot yet!  ⚠️ ","In order to start collecting eggs, you need to use the e!start! Make sure you have channel perms too! Only Moderators who have those perms can use that command!","",0xE56A6A)
                await extra_functions.send_embed_message(bot,message,embed,60,"not started yet message send")
        else:
            await bot.process_commands(message)

# Function called when Bot is ready to be ran
@bot.event
async def on_ready():
    extra_functions.logger_print('Bot is getting ready!')

    extra_functions.logger_print('Logging into ' + bot.user.name + '!\nSetting Up Tables')
    await startup_create_tables()
    extra_functions.logger_print('Adding Missing Data')
    await Insert_Missing_Data()
    extra_functions.logger_print('Tables Successfully Setup!\nClearing Messages...')
    await clear_messages()
    extra_functions.logger_print('Cleared Messages!\nResetting Server Hearts!')
    for guild in bot.guilds:
        guild_row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",guild.id)
        if(guild_row["message_state"] >= 0):
            await extra_functions.reset_server_message(bot,guild)
    extra_functions.logger_print('Done Resettings Server Hearts!')

    extra_functions.logger_print('Fully Ready!')
    bot.ready = True
    extra_functions.logger_print('Bot is initialized for use.')

@loop(seconds=300)
async def check_active_messages():
    if bot.ready:
        for guild in bot.guilds:
            if await bot.pg_con.fetchrow("SELECT 1 FROM guild_settings WHERE Guild_ID = $1",guild.id) != None:
                guild_row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",guild.id)
                active_settings = guild_row['active_message_settings']
                default_settings = guild_row['default_message_settings']
                if active_settings[1] < int(default_settings[1]): 
                    active_settings[1] += 1
                await bot.pg_con.execute("UPDATE guild_settings set active_message_settings = $1 WHERE Guild_ID = $2",active_settings,guild.id)

@loop(seconds=10)
async def check_cluster_messages():
    if bot.ready:
        message_rows = await bot.pg_con.fetch("SELECT * FROM egg_messages")
        for message_row in message_rows:
            if message_row["timeout_message"] < int(datetime.now().timestamp()):
                guild_row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",message_row["guild_id"])
                await bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",3,message_row["guild_id"]) #Update Loved
                if guild_row["message_state"] > 0:
                    if len(message_row["claimed_users"]) == 0 or not message_row['claimed_users']:
                        embed = extra_functions.embedBuilder("🥚  The Egg Cluster disappeared! 🥚","No one collected egg clusters.","Remember to tap or click the reaction to get an egg cluster!",0x8F0700)
                        message = bot.get_channel(message_row["current_channel"]).get_partial_message(message_row["message_id"])
                        if message != None:
                            await extra_functions.edit_embed_message(bot,message,embed,"check cluster message function edit no one")
                        else:
                            extra_functions.logger_print(guild_row["guild_id"] + " - No Message 1")
                    elif len(message_row["claimed_users"]) > 0:
                        embed = extra_functions.embedBuilder("🥚  The remaining egg clusters rolled away!  🥚","Not all the egg clusters were collected!","Remember to tap or click the reaction to get an egg cluster!",0x8F0700)
                        message = bot.get_channel(message_row["current_channel"]).get_partial_message(message_row["message_id"])
                        if message != None:
                            await extra_functions.edit_embed_message(bot,message,embed,"check cluster message function edit some")
                        else:
                            extra_functions.logger_print(guild_row["guild_id"] + " - No Message 2")
                    else:
                        embed = extra_functions.embedBuilder("🥚  The Egg Cluster disappeared! 🥚","Make sure to look for the next cluster!","Remember to tap or click the reaction to get an egg cluster!",0x8F0700)
                        message = bot.get_channel(message_row["current_channel"]).get_partial_message(message_row["message_id"])
                        if message != None:
                            await extra_functions.edit_embed_message(bot,message,embed,"check cluster message function edit no one")
                        else:
                            extra_functions.logger_print(guild_row["guild_id"] + " - No Message 3")
                await extra_functions.reset_server_message(bot,bot.get_guild(message_row['guild_id']))

        
        guild_rows = await bot.pg_con.fetch("SELECT * FROM guild_settings")
        for guild_row in guild_rows:
            message_row = await bot.pg_con.fetchrow("SELECT * FROM egg_messages WHERE Guild_ID = $1",guild_row['guild_id'])
            if guild_row["message_state"] == 3 or (guild_row["message_state"] == 2 and message_row == None):
                guild = bot.get_guild(guild_row['guild_id'])
                await extra_functions.reset_server_message(bot,guild)
                




@loop(seconds=10)
async def check_leaderboard_messages():
    if bot.ready:
        lb_row = await bot.pg_con.fetch("SELECT * FROM role_lb_messages")
        for row in lb_row:
            if row["timeout_message"] < datetime.now().timestamp():
                await bot.pg_con.execute("DELETE FROM role_lb_messages WHERE Message_ID = $1",row["message_id"])
        lb_row = await bot.pg_con.fetch("SELECT * FROM collection_lb_messages")
        for row in lb_row:
            if row["timeout_message"] < datetime.now().timestamp():
                await bot.pg_con.execute("DELETE FROM collection_lb_messages WHERE Message_ID = $1",row["message_id"])
        lb_row = await bot.pg_con.fetch("SELECT * FROM basket_messages")
        for row in lb_row:
            if row["timeout_message"] < datetime.now().timestamp():
                await bot.pg_con.execute("DELETE FROM basket_messages WHERE Message_ID = $1",row["message_id"])
        lb_row = await bot.pg_con.fetch("SELECT * FROM history_lb_messages")
        for row in lb_row:
            if row["timeout_message"] < datetime.now().timestamp():
                await bot.pg_con.execute("DELETE FROM history_lb_messages WHERE Message_ID = $1",row["message_id"])
        lb_row = await bot.pg_con.fetch("SELECT * FROM trade_messages")
        for row in lb_row:
            if row["timeout_message"] < datetime.now().timestamp():
                await bot.pg_con.execute("DELETE FROM trade_messages WHERE Message_ID = $1",row["message_id"])
                embed = extra_functions.embedBuilder("🕛  The Trade Expired Between " + bot.get_user(row['user_ids'][0]).name + " and " + bot.get_user(row['user_ids'][1]).name + "  🕛","Looks like the five minute window went by fast! The trade is not valid anymore!","Make another trade to replace this one!",0x8F0700)
                await extra_functions.edit_embed_message(bot,bot.get_channel(row["current_channel"]).get_partial_message(row["message_id"]),embed,"check trade message function edit explire")                
@loop(seconds=60)
async def change_presense():
    if bot.ready:
        sum = await bot.pg_con.fetch("SELECT SUM(eggs_collected) as total FROM server_stats;")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name= "" + bot.prefix  + "help | Currently giving " + str(point_rpg_string(int(sum[0]['total']))) + " eggs to " + str(len(bot.guilds)) + " Servers!"))

def point_rpg_string(points):
    p_string = str(points)
    if(points > 100000000):
        return p_string[:3] + "." + p_string[3:4] + "M"
    elif(points > 10000000):
        return p_string[:2] + "." + p_string[2:3] + "M"
    elif(points > 1000000):
        return p_string[:1] + "." + p_string[1:3] + "M"
    elif(points > 100000):
        return p_string[:3] + "." + p_string[3:4] + "K"
    elif(points > 10000):
        return p_string[:2] + "." + p_string[2:3] + "K"
    return p_string            

async def clear_messages():
    await bot.pg_con.execute("TRUNCATE egg_messages")
    await bot.pg_con.execute("TRUNCATE basket_messages")
    await bot.pg_con.execute("TRUNCATE role_lb_messages")
    await bot.pg_con.execute("TRUNCATE collection_lb_messages")
    await bot.pg_con.execute("TRUNCATE history_lb_messages")
    await bot.pg_con.execute("TRUNCATE trade_messages")



#Finishing __init__
coggers()
bot.loop.run_until_complete(create_db_pool())
change_presense.start()
check_active_messages.start()
check_cluster_messages.start()
check_leaderboard_messages.start()
bot.run(TOKEN, bot = True, reconnect = True)
    