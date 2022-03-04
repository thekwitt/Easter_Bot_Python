from os import closerange
import random
from datetime import datetime

import discord
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Cluster_Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'removechannel')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def remove_channel(self,ctx,channel: discord.TextChannel):
        message_row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
        channels = message_row["possible_channel_ids"]
        if channel.id in channels:
            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = array_remove(possible_channel_ids,$1) WHERE Guild_ID = $2;",channel.id,ctx.message.guild.id) #Update Loved
            embed = extra_functions.embedBuilder("💬  " + channel.name + " has been removed!  💬","This channel will no longer spawn an egg cluster!\nIf this was done by mistake, please use " + self.bot.prefix + "addchannel " + channel.mention + " to add the channel back.","For more moderator commands, use " + self.bot.prefix + "help mod.",0xFFA631)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,120,"remove channel function send else statement")
            if(len(channels) == 1):
                await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",-1,ctx.message.guild.id) #Update Loved
            else:
                await extra_functions.reset_server_message(self.bot,ctx.message.guild)
        else:
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","Looks like the channel was not in the list!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,20,"remove channel function send else statement")

            

    @remove_channel.error
    async def remove_channel_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","Looks like that wasn't a channel tag!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,20,"remove channel function send missing args error")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, commands.BotMissingPermissions):
            extra_functions.logger_print(error)
        elif isinstance(error, AttributeError):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","Looks like that wasn't a channel tag!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,20,"remove channel function send attribute error")
        elif isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️   Whoops!  ⚠️ !", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")




    @commands.command(name = 'addchannel')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def add_channel(self,ctx,channel: discord.TextChannel):
        message_row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
        channels = message_row["possible_channel_ids"]
        if not channel.id in channels:
            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = array_append(possible_channel_ids,$1) WHERE Guild_ID = $2;",channel.id,ctx.message.guild.id) #Update Loved
            embed = extra_functions.embedBuilder("💬  " + channel.name + " has been added!  💬","This channel has a possibility to spawn an egg cluster!\nIf this was done by mistake, please use " + self.bot.prefix + "removechannel " + channel.mention + " to remove the channel.","For more moderator commands, use " + self.bot.prefix + "help mod.",0xFFA631)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,120,"add channel function if statement")
            await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",0,ctx.message.guild.id) #Update Loved
            await extra_functions.reset_server_message(self.bot,ctx.message.guild)
        else:
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","Looks like the channel was already in the list!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,20,"add channel function send else statement")


    @add_channel.error
    async def add_channel_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","Looks like that wasn't a channel tag!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,20,"add channel function send missing args error")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, commands.BotMissingPermissions):
            extra_functions.logger_print(error)
        elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","Looks like that wasn't a channel tag!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_message(self.bot,ctx.message,embed,20,"add channel function send attribute error")
        elif isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️   Whoops!  ⚠️ !", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")

    @commands.Cog.listener("on_message")
    async def egg_handler(self,message):
        if self.bot.ready:
            try:
                settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",message.guild.id)
            except AttributeError:
                return
            if settings == None:
                return
            if settings["message_state"] != -2:
                if(len(settings["possible_channel_ids"]) == 0 and settings["message_state"] >= 0):
                    await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",-1,message.guild.id) #Update Loved
                if(settings["message_state"] >= 0):
                    channels = settings["possible_channel_ids"]
                    default_settings = settings["default_message_settings"]
                    if(settings["active_message_settings"][1] > 0 and not message.author.bot):
                        if(default_settings[2] == "True"):
                            settings["active_message_settings"][1] -= 1
                            await self.bot.pg_con.execute("UPDATE guild_settings set active_message_settings =  $1 WHERE Guild_ID = $2;",settings["active_message_settings"],message.guild.id) #Update Loved
                        elif(message.channel.id in channels):
                            settings["active_message_settings"][1] -= 1
                            await self.bot.pg_con.execute("UPDATE guild_settings set active_message_settings =  $1 WHERE Guild_ID = $2;",settings,message.guild.id) #Update Loved
                    if settings["active_message_settings"][0] < datetime.now().timestamp() and settings["active_message_settings"][1] == 0 and settings["message_state"] == 0:
                        
                        state = 1
                        await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",1,message.guild.id) #Update Loved
                        channel_id = None
                        ids = list(settings["possible_channel_ids"])
                        for channel in range(len(channels)-1,-1,-1):                      
                            if message.guild.get_channel(ids[channel]) == None:
                                ids.pop(channel)
                        if not ids and settings["possible_channel_ids"]:
                            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = '{}', message_state = $1 WHERE Guild_ID = $2;",-1,message.guild.id) #Update Loved
                            return
                        elif ids != channels:
                            await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = $1 WHERE Guild_ID = $2;",ids,message.guild.id) #Update Loved

                        channel_id = random.choice(ids)

                        embed = extra_functions.embedBuilder("🥚  An Egg Cluster has appeared!  🥚","Hit the egg reaction to collect the egg cluster!","Up to " + default_settings[4] + " people can collect this egg cluster!",0xFFA631)
                        message_obj = await extra_functions.send_embed_channel(self.bot,self.bot.get_channel(channel_id),embed,120,"egg handler function send 1")
                        if(message_obj == None):
                            await extra_functions.reset_server_message(self.bot,message.guild)
                            return
                        await message_obj.add_reaction('🥚')
                        await self.bot.pg_con.execute("UPDATE server_stats set Cluster_Spawns = Cluster_Spawns + 1 WHERE Guild_ID = $1;",message.guild.id) #Update Loved                    
                        await self.bot.pg_con.execute("INSERT INTO egg_messages (Message_ID, Guild_ID, Current_Channel, timeout_message) VALUES ($1, $2, $3, $4) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,message.guild.id,channel_id,datetime.now().timestamp() + 60) #Update Loved
                        await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",2,message.guild.id) #Update Loved

            
    @commands.Cog.listener("on_reaction_add")
    async def egg_message_checker(self,reaction,user):
        if self.bot.ready:
            guild_row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",reaction.message.guild.id)
            default_settings = guild_row["default_message_settings"]
            if(guild_row["message_state"] == 2 and not user.bot):
                if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(reaction.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
                    await Database_Methods.Insert_User(self.bot,reaction.message.guild.id,user.id)
                message_row = await self.bot.pg_con.fetchrow("SELECT * FROM egg_messages WHERE Guild_ID = $1;",reaction.message.guild.id)
                if message_row != None:
                    if(self.bot.get_channel(message_row["current_channel"]).get_partial_message(message_row["message_id"]) != None and not user.id in message_row["claimed_users"] and len(message_row["claimed_users"]) < int(default_settings[4])):
                        if(reaction.emoji == '🥚'):
                            message_row["claimed_users"].append(user.id)
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(reaction.message.guild.id) + " set Clusters = Clusters + 1 WHERE UserID = $1;",user.id) #Update Loved
                            await self.bot.pg_con.execute("UPDATE egg_messages set claimed_users = $1 WHERE Guild_ID = $2;", message_row["claimed_users"],reaction.message.guild.id) #Update Loved
                    if(len(message_row["claimed_users"]) >= int(default_settings[4])):
                        embed = extra_functions.embedBuilder("🥚  All the egg clusters are collected!  🥚","No more egg clusters are available! Make sure to use e!uncluster to get the eggs from the cluster!","Make sure to look out for the next egg cluster spawn!",0x8F0700)
                        await extra_functions.edit_embed_message(self.bot,self.bot.get_channel(message_row["current_channel"]).get_partial_message(message_row["message_id"]),embed,"check cluster message function edit some")
                        await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",3,reaction.message.guild.id) #Update Loved
                        await extra_functions.reset_server_message(self.bot,reaction.message.guild)


def EffectiveCalc(level):
    if level == 1:
        rand = random.randint(0,101)
        if rand <= 101 and rand >= 35:
            return 1
        elif rand < 35 and rand >= 15:
            return 2
        else:
            return 3
    elif level == 2:
        rand = random.randint(0,101)
        if rand <= 101 and rand >= 30:
            return 2
        elif rand < 30 and rand >= 10:
            return 4
        else:
            return 6
    elif level == 3:
        rand = random.randint(0,101)
        if rand <= 101 and rand >= 25:
            return 3
        elif rand < 25 and rand >= 8:
            return 6
        else:
            return 9

def setup(bot):
    bot.add_cog(Cluster_Message(bot))
