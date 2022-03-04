import discord
from datetime import datetime
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions

class Settings(commands.Cog):


    def __init__(self, bot):
        self.bot = bot        

    @commands.command(name = 'activespawns')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def spawns_command(self, ctx):

        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",ctx.guild.id)
        ids = list(settings["possible_channel_ids"])
        for channel in range(len(ids)-1,-1,-1):                      
            if ctx.guild.get_channel(ids[channel]) == None:
                ids.pop(channel)
        if not ids and settings["possible_channel_ids"]:
            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = '{}', message_state = $1 WHERE Guild_ID = $2;",-1,ctx.guild.id) #Update Loved
        elif ids != settings["possible_channel_ids"]:
            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = $1 WHERE Guild_ID = $1;",ids,ctx.guild.id) #Update Loved
        
        if ids:
            list_string = ""
        elif not ids:
            list_string = "You have no active spawns!"

        for channel in ids:
            list_string += ctx.guild.get_channel(channel).name + ", "
        
        embed = extra_functions.embedBuilder("⚙️  Active Channel Spawns  ⚙️",list_string[:-2],"To add channels, use e!addchannel [Channel]\nTo remove, use e!removechannel [Channel]",color=0xFF00C4)

        try:
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"settings send message")
        except discord.errors.Forbidden as e:
            extra_functions.logger_print(e)
            return




    @commands.command(name = 'settings')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def settings_command(self, ctx):

        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
        settings = row["default_message_settings"] + row["default_server_settings"]
        embed = extra_functions.embedBuilder("⚙️ Cracklefest Command Prompt ⚙️",self.setting_string(settings),"To change these settings. Do " + self.bot.prefix + "setsetting.",color=0xFF00C4)

        try:
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"settings send message")
        except discord.errors.Forbidden as e:
            extra_functions.logger_print(e)
            return

    @commands.Cog.listener("on_guild_channel_delete")
    async def check_active_channels(self,channel):
        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",channel.guild.id)
        ids = row['possible_channel_ids']
        if channel.id in ids:
            ids.remove(channel.id)
            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids =  $1 WHERE Guild_ID = $2;",ids,channel.guild.id) #Update Loved

    def setting_string(self,settings):
        string = "**Egg Command Cooldown** - The default cooldowns for users that use Egg Commands\n**Currently: " + str(self.returncdname(settings[5])) + "**\n\n"
        string += "**Mailbox Command Cooldown** - The default cooldown for the mailbox command\n**Currently: " + str(self.returncdname(settings[6])) + "**\n\n"
        string += "**Purification Limit** - The amount of eggs needed to purify an area\n**Currently: " + str(settings[7]) + " Eggs Per Area**\n\n"
        string += "**Next Cluster Interval**" + " - How long it takes for the cluster to spawn\n**Currently: " + str(settings[0]) + " seconds.**\n\n"
        string += "**Reaction Amount Requirement**" + " - How many people can react to an egg cluster\n**Currently: " + str(settings[4]) + " Reactions Per Cluster**\n\n"
        string += "**Message Amount Requirement**" + " - How many messages does it take to spawn\n**Currently: " + str(settings[1]) + " messages.**\n\n"
        string += "**Outside Channel Restrictions**" + " - Allow everything outside the current channel to trigger the bot inside the current channel.\n**Currently: " + str(settings[2]) + ".**\n\n"
        string += "**General Chat Mode**" + " - Deletes messages sent by the bot after a short period of time.\n**Currently: " + str(settings[3]) + ".**\n\n"

        return string



    @commands.command(name = "setsetting",aliases=['setsettings'])
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    #@commands.bot_has_guild_permission
    async def setting_set_command(self,ctx,setting_type,value):
        if setting_type.lower() == "interval":
            if int(value) < 60:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Next Cluster Interval must be higher than 59 seconds!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function interval high send")
            elif int(value) > 1800:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Next Cluster Interval must be lower than 30 minutes/1081 seconds!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function interval low send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_message_settings"]
                settings[0] = str(value)
                await self.bot.pg_con.execute("UPDATE guild_settings set default_message_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Next Cluster Interval has been changed to " + str(value) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function interval correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
                #resetservermessage placeholder
        elif setting_type.lower() == "message":
            if int(value) < 1:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Message Amount Requirement must be higher than 1 message!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message high send")
            elif int(value) > 1000:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Message Amount Requirement must be lower than 1001 messages!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_message_settings"]
                settings[1] = str(value)
                await self.bot.pg_con.execute("UPDATE guild_settings set default_message_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Message Amount Requirement has been changed to " + str(value) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,15,"set settings function message correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
                #resetservermessage placeholder
        elif setting_type.lower() == "purify":
            if int(value) < 100:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Purification Limit must be higher than 100 eggs!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message high send")
            elif int(value) > 10000:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Purification Limit must be lower than 10001 eggs!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_server_settings"]
                settings[2] = str(value)
                await self.bot.pg_con.execute("UPDATE guild_settings set default_server_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Purification Limit has been changed to " + str(value) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,15,"set settings function message correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
                #resetservermessage placeholder
        elif setting_type.lower() == "outside":
            if not isinstance(extra_functions.str_to_bool(value),bool):
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Outside Channel Restrictions must be either True or False!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function outside incorrect send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_message_settings"]
                settings[2] = str(extra_functions.str_to_bool(value))
                await self.bot.pg_con.execute("UPDATE guild_settings set default_message_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
        
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Outside Channel Restrictions has been changed to " + str(value.lower()) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function outside correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
                #resetservermessage placeholder
        elif setting_type.lower() == "general":
            if not isinstance(extra_functions.str_to_bool(value),bool):
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe General Chat Mode must be either True or False!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function general incorrect send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_message_settings"]
                settings[3] = str(extra_functions.str_to_bool(value))
                await self.bot.pg_con.execute("UPDATE guild_settings set default_message_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                #resetservermessage placeholder
        
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for General Chat Mode has been changed to " + str(value.lower()) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function general correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
        elif setting_type.lower() == "cooldown":
            if not value.lower() in ["quick","short","normal","long","lengthy"]:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Egg Command Cooldown Setting must be either Quick, Short, Normal, Long or Lengthy!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function cooldown incorrect send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_server_settings"]
                settings[0] = str(self.returncooldown(value))
                await self.bot.pg_con.execute("UPDATE guild_settings set default_server_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                #resetservermessage placeholder
        
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Egg Command Cooldown Setting has been changed to " + str(value) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function cooldown correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
        elif setting_type.lower() == "mailbox":
            if not value.lower() in ["quick","short","normal","long","lengthy"]:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Mailbox Cooldown Setting must be either Quick, Short, Normal, Long or Lengthy!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function cooldown incorrect send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_server_settings"]
                settings[1] = str(self.returncooldown(value))
                await self.bot.pg_con.execute("UPDATE guild_settings set default_server_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                #resetservermessage placeholder
        
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Mailbox Cooldown Setting has been changed to " + str(value) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function cooldown correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
        elif setting_type.lower() == "reactions":
            if int(value) < 1:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Reaction Amount Requirement must be higher than 1 reaction!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message high send")
            elif int(value) > 100:
                embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThe Reaction Amount Requirement must be lower than 101 reactions!\n⠀", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
            else:
                row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                settings = row["default_message_settings"]
                settings[4] = str(value)
                await self.bot.pg_con.execute("UPDATE guild_settings set default_message_settings =  $1 WHERE Guild_ID = $2;",settings,ctx.message.guild.id) #Update Loved
                
                embedVar = discord.Embed(title="New settings have been changed!", description="⠀\nThe new default for Reaction Amount Requirement has been changed to " + str(value) + "!\n⠀", color=0xFA89CD)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,15,"set settings function message correct send")
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
                #resetservermessage placeholder
        else:
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="⠀\nThat is not a correct setting! Send " + self.bot.prefix + "setsetting for how to correctly change bot settings.\n⠀", color=0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function settings incorrect send")

    @setting_set_command.error
    async def set_settings_command_error(self,ctx,error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.CommandInvokeError):
            embedVar = discord.Embed(title="⚙️ Cracklefest Command Prompt (For Changing Settings) ⚙️", description=self.set_setting_info(), color=0xFF00C4)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,60,"set settings function missing requirement send")
        elif isinstance(error, commands.BadArgument):
            try:
                await ctx.send("This is not a correct value!")
            except(discord.errors.Forbidden):
                extra_functions.logger_print(str(ctx.message.guild.name) + " with ID: "+ str(ctx.message.guild.id) + " SetSettings - No Chat") 
        elif isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")
            #redo embed
        elif isinstance(error, commands.BotMissingPermissions):
            pass

    def set_setting_info(self):

        string = "⠀\n__**Command List - For Changing Settings**__\n\n"
        string += "** " + self.bot.prefix + "setsetting** - Shows a list of all commands to change settings!\n\n"
        string += "** " + self.bot.prefix + "setsetting cooldown [value]** - Change the cooldown on commands **Quick, Short, Normal, Long, Lengthy**\n\n"
        string += "** " + self.bot.prefix + "setsetting mailbox [value]** - Change the cooldown on mailbox **Quick, Short, Normal, Long, Lengthy**\n\n"
        string += "** " + self.bot.prefix + "setsetting purify [value]** - Change the amount of eggs required to purify each individual area. **100-10000**\n\n"
        string += "** " + self.bot.prefix + "setsetting interval [value]** - Change the amount of seconds required to spawn a cluster. **60 - 600**\n\n"
        string += "** " + self.bot.prefix + "setsetting reactions [value]** - Change the amount of users that can react to a cluster. **1 - 100**\n\n"
        string += "** " + self.bot.prefix + "setsetting message [value]** - Change the amount of messages of needed to spawn a cluster. **1 - 1000**\n\n"
        string += "** " + self.bot.prefix + "setsetting outside [value]** - Change if outside channel message impact the spawning of a cluster. **True or False**\n\n"
        string += "** " + self.bot.prefix + "setsetting general [value]** - Change if you don't want messages to delete over a period of time. **True or False**\n⠀"

        return string

        

    @commands.command(name = 'whennextcluster')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def whennextcluster_command(self,ctx):
        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
        if(row["message_state"] == -1):
            embed = extra_functions.embedBuilder("You haven't added any channels yet!","Use " + self.bot.prefix + "addchannel [Channel Tag] to add a channel for clusters to appear!","You can also change the settings using " + self.bot.prefix + "setsetting",0xFF00C4)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"when next clusters function send")
        else:
            settings = row["active_message_settings"]
            embed = extra_functions.embedBuilder("When does the next clusters appear?","Time Left: " + str(settings[0] - datetime.now().timestamp()) + "\nMessages Left: " + str(settings[1]) + "\nMessage State: " + str(row["message_state"]),"",0xFF00C4)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"when next clusters function send")

    @whennextcluster_command.error
    async def whennextcluster_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass
        elif isinstance(error, commands.MissingPermissions):
            embed = extra_functions.embedBuilder("⚠️  Whoops!  ⚠️","Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"when next clusters function send")

    @commands.command(name = 'resetserver')
    @commands.has_guild_permissions(administrator = True) # figure out way to check either or
    async def reset_server_command(self,ctx):
        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
        if(row["message_state"] != -2):
            await self.bot.pg_con.execute("TRUNCATE " + "g_" + str(ctx.message.guild.id) + ";")
            await self.bot.pg_con.execute("DELETE from guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("""INSERT INTO guild_settings (Guild_ID,Version,message_state) VALUES ($1,$2,$3) ON CONFLICT (Guild_ID) DO NOTHING;""",ctx.guild.id,self.bot.db_version,-2)
            await self.bot.pg_con.execute("DELETE from egg_messages WHERE Guild_ID = $1",ctx.message.guild.id)
            await self.bot.pg_con.execute("DELETE from role_lb_messages WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("DELETE from collection_lb_messages WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("DELETE from history_lb_messages WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("DELETE from trade_messages WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("DELETE from server_stats WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("""INSERT INTO server_stats (Guild_ID) VALUES ($1) ON CONFLICT (Guild_ID) DO NOTHING;""",ctx.guild.id)
            await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE guild_id = $2",-2,ctx.guild.id)
            embed = extra_functions.embedBuilder("Database has been wiped!","You have cleared your server's database! This is **NOT UNDOABLE**.\n\nUse the **e!start** command to start the bot again!","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt! Although there is most likely nothing he can do.",0xFF00C4)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"reset server function send")

    @reset_server_command.error
    async def reset_server_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass
        elif isinstance(error, commands.MissingPermissions):
            embed = extra_functions.embedBuilder("⚠️  Whoops!  ⚠️","Looks like you don't have admin permissions!\nIn order to use this command, you need to have to be an admin!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"when reset server missing perms function send")

    @commands.command(name = 'defaultsettings')
    @commands.has_guild_permissions(administrator = True) # figure out way to check either or
    async def default_settings_command(self,ctx):
        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
        if(row["message_state"] != -2):
            await self.bot.pg_con.execute("TRUNCATE " + "g_" + str(ctx.message.guild.id) + ";")
            await self.bot.pg_con.execute("DELETE from guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
            await self.bot.pg_con.execute("""INSERT INTO guild_settings (Guild_ID,Version) VALUES ($1,$2) ON CONFLICT (Guild_ID) DO NOTHING;""",ctx.guild.id,self.bot.db_version)
            embed = extra_functions.embedBuilder("Your server's settings are now set to default!","You can see everything with e!settings","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt! Although there is most likely nothing he can do.",0xFF00C4)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"reset server function send")

    @default_settings_command.error
    async def default_server_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass
        elif isinstance(error, commands.MissingPermissions):
            embed = extra_functions.embedBuilder("⚠️  Whoops!  ⚠️","Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"when reset server missing perms function send")

    def returncooldown(self,value):
        if value.lower() == "quick":
            return 1
        elif value.lower() == "short":
            return 2
        elif value.lower() == "normal":
            return 3
        elif value.lower() == "long":
            return 4
        elif value.lower() == "lengthy":
            return 5    

    def returncdname(self,value):
        if value.lower() == "1":
            return "Quick"
        if value.lower() == "2":
            return "Short"
        elif value.lower() == "3":
            return "Normal"
        elif value.lower() == "4":
            return "Long"
        elif value.lower() == "5":
            return "Lengthy"

def setup(bot):
    bot.add_cog(Settings(bot))