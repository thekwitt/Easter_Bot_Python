from Extras.discord_functions import extra_functions
import discord, random, asyncio, asyncpg, os, os.path

class Database_Methods:
    @staticmethod
    async def update_database(bot): # Current Version - 2
        #await bot.pg_con.execute("UPDATE guild_settings set version = $1","1") 
        settings = await bot.pg_con.fetch("SELECT * FROM guild_settings")
        for setting in settings:
            if setting["version"] == "1": # Void Update
                extra_functions.logger_print("UPDATING " + str(setting['guild_id']) + " TO VERSION 2! PLEASE WAIT!")
                #await bot.pg_con.execute("ALTER TABLE " + "g_" + str(guild.id) + " DROP COLUMN IF EXISTS incognito_mode;")
                await bot.pg_con.execute("ALTER TABLE " + "g_" + str(setting['guild_id']) + " ALTER COLUMN CD_Explorer SET DEFAULT '{0,0,0,0,0,0,0}';")
                await bot.pg_con.execute("UPDATE " + "g_" + str(setting['guild_id']) + " set CD_Explorer = '{0,0,0,0,0,0,0}';")
                await bot.pg_con.execute("ALTER TABLE server_stats ALTER COLUMN Areas_Explored SET DEFAULT '{0,0,0,0,0,0,0}';")
                stats = await bot.pg_con.fetchrow("SELECT * FROM server_stats WHERE Guild_ID = $1",setting['guild_id'])
                explore_stats = stats['areas_explored']
                explore_stats.append(0)
                await bot.pg_con.execute("UPDATE server_stats set areas_explored = $1 WHERE Guild_ID = $2;",explore_stats,setting['guild_id']) #Update Loved                    
                await bot.pg_con.execute("UPDATE guild_settings set version = $1 WHERE Guild_ID = $2;","2",setting['guild_id']) 
                extra_functions.logger_print(str(setting['guild_id']) + " UPDATED TO VERSION 2!")

    @staticmethod
    async def Insert_User(bot,guild_id,user_id):
        await bot.pg_con.execute("INSERT INTO " + "g_" + str(guild_id) + " (UserID) VALUES ($1) ON CONFLICT (UserID) DO NOTHING;",user_id)
        #await bot.pg_con.execute("ALTER TABLE guild_settings ADD COLUMN ")
