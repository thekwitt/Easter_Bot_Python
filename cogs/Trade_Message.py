from os import closerange
import random, json
from datetime import datetime

import discord
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Trade_Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'trade')
    #@commands.cooldown(1, 300, commands.BucketType.member)
    async def trade_command(self,ctx,u_obj: discord.User,egg1,egg2):
        trade_row = await self.bot.pg_con.fetchrow("SELECT * FROM trade_messages WHERE Guild_ID = $1 AND User_IDs[1] = $2;",ctx.message.guild.id,ctx.message.author.id)
        if(trade_row == None):
            if(ctx.message.author.id != u_obj.id):
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) 
                target = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id)  
                if egg1 in user['basket_eggs']:
                    if egg2 in target['basket_eggs']:
                        ref_eggs = egg_dic['regular_eggs'] + egg_dic['collectible_eggs']
                        egg_obj_1 = [item for item in ref_eggs if item['id'] == egg1][0]
                        egg_obj_2 = [item for item in ref_eggs if item['id'] == egg2][0]

                        embed = extra_functions.embedBuilder(ctx.message.author.name + " made a trade with " + u_obj.name + "!","" + ctx.message.author.name + " is trading their "+ egg_obj_1['emoji'] + " for " + u_obj.name + "'s " + egg_obj_2['emoji'] + "\n\nHit the check mark reaction to accept the trade! To reject the trade, hit the X reaction to decline the trade!","This Trade has five minutes until it expires",0xB51A3A)
                        message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,360,"trade function send 1")
                        await message_obj.add_reaction('<a:yes:823787035802075156>')
                        await message_obj.add_reaction('<a:no:823787035818590228>')
                        await self.bot.pg_con.execute("INSERT INTO trade_messages (Message_ID, Current_Channel, User_IDs, Guild_ID, Egg_IDs, timeout_message) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,ctx.message.channel.id,[ctx.message.author.id,u_obj.id],ctx.guild.id,[egg1,egg2],datetime.now().timestamp() + 300) #Update Loved
                    else:
                        embedVar = extra_functions.embedBuilder("⚠️  Their egg is not in their basket!  ⚠️","To see if their basket has that egg, use " + self.bot.prefix + "basket [User Mention] and click/tap the egg to see it's id! The ID is between the colons -> :10001: !","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                else:
                    embedVar = extra_functions.embedBuilder("⚠️  Your egg is not in your basket!  ⚠️","To see if your basket has that egg, use " + self.bot.prefix + "basket and click/tap the egg to see it's id! The ID is between the colons -> :10001: !","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
            else:
                embedVar = extra_functions.embedBuilder("⚠️  You can't trade yourself!  ⚠️","Trade with someone else!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")        
        else:
            embedVar = extra_functions.embedBuilder("⚠️  You already have an active trade!  ⚠️","Either have the other person complete the trade or wait for it to expire! Every trade expires after five minutes of being made!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
    @trade_command.error
    async def trade_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "trade** [User Mention] [Your Egg ID] [Their Egg ID].","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function missing args send")
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","Remember to do **" + self.bot.prefix + "trade** [User Mention] [Your Egg ID] [Their Egg ID]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
        elif isinstance(error,commands.CommandInvokeError):
            pass

    @commands.Cog.listener("on_reaction_add")
    async def egg_message_checker(self,reaction,user):
        if self.bot.ready:
            trade_row = await self.bot.pg_con.fetchrow("SELECT * FROM trade_messages WHERE Message_ID = $1 AND User_IDs[2] = $2;",reaction.message.id,user.id)
            if(trade_row != None):
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                ref_eggs = egg_dic['regular_eggs'] + egg_dic['collectible_eggs']
                egg_obj_1 = [item for item in ref_eggs if item['id'] == trade_row['egg_ids'][0]][0]
                egg_obj_2 = [item for item in ref_eggs if item['id'] == trade_row['egg_ids'][1]][0]
                user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(reaction.message.guild.id) + " WHERE UserID = $1",trade_row['user_ids'][0])
                target = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(reaction.message.guild.id) + " WHERE UserID = $1",trade_row['user_ids'][1])
                if(reaction.emoji == self.bot.get_emoji(823787035802075156)):
                    u1_string = self.bot.get_user(trade_row['user_ids'][0]).name + " received a "
                    u2_string = self.bot.get_user(trade_row['user_ids'][1]).name + " received a "

                    # Remove Eggs
                    user_reggs = user['basket_eggs']
                    user_ceggs = user['collection_eggs']
                    target_reggs = target['basket_eggs']
                    target_ceggs = target['collection_eggs']

                    user_reggs.remove(trade_row['egg_ids'][0])
                    target_reggs.remove(trade_row['egg_ids'][1])

                    # First Egg
                    if "1" == trade_row['egg_ids'][1][0]:
                        u1_string += egg_obj_2['emoji']
                        user_reggs.append(trade_row['egg_ids'][1])
                    elif "2" == trade_row['egg_ids'][1][0]:
                        if not egg_obj_2['id'] in user['collection_eggs']:
                            u1_string += "**NEW COLLECTIBLE EGG!**: " +  egg_obj_2['emoji']
                            user_ceggs.append(trade_row['egg_ids'][1])
                        else:
                            u1_string += egg_obj_2['emoji']
                            user_reggs.append(trade_row['egg_ids'][1])
                    
                    # Second Egg
                    if "1" == trade_row['egg_ids'][0][0]:
                        u2_string += egg_obj_1['emoji']
                        target_reggs.append(trade_row['egg_ids'][0])
                    elif "2" == trade_row['egg_ids'][0][0]:
                        if not egg_obj_1['id'] in target['collection_eggs']:
                            u2_string += "**NEW COLLECTIBLE EGG!**: " +  egg_obj_1['emoji']
                            target_ceggs.append(trade_row['egg_ids'][0])
                        else:
                            u2_string += egg_obj_1['emoji']
                            target_reggs.append(trade_row['egg_ids'][0])

                    await self.bot.pg_con.execute("UPDATE " + "g_" + str(reaction.message.guild.id) + " set basket_eggs = $1, collection_eggs = $2 WHERE UserID = $3",user_reggs,user_ceggs,trade_row['user_ids'][0]) #Update Loved
                    await self.bot.pg_con.execute("UPDATE " + "g_" + str(reaction.message.guild.id) + " set basket_eggs = $1, collection_eggs = $2 WHERE UserID = $3",target_reggs,target_ceggs,trade_row['user_ids'][1]) #Update Loved
                    await self.bot.pg_con.execute("UPDATE server_stats set trades_count = trades_count + 1 WHERE Guild_ID = $1;",reaction.message.guild.id) #Update Loved                    
                    
                    embed = extra_functions.embedBuilder("🤝  The Trade Between " + self.bot.get_user(trade_row['user_ids'][0]).name + " and " + self.bot.get_user(trade_row['user_ids'][1]).name + " is complete!  🤝",u1_string + "\n\n" + u2_string,"You both can make another trade again!",0x8F0700)
                    await extra_functions.edit_embed_message(self.bot,self.bot.get_channel(trade_row["current_channel"]).get_partial_message(trade_row["message_id"]),embed,"check cluster message function edit some")
                    await self.bot.pg_con.execute("DELETE from trade_messages WHERE message_id = $1;",reaction.message.id)
                    await extra_functions.add_secondary_role(self.bot,self.bot.get_user(trade_row['user_ids'][0]),reaction.message.channel,reaction.message.guild,user_ceggs)
                    await extra_functions.add_secondary_role(self.bot,self.bot.get_user(trade_row['user_ids'][1]),reaction.message.channel,reaction.message.guild,target_ceggs)
                elif(reaction.emoji == self.bot.get_emoji(823787035818590228)):
                    embed = extra_functions.embedBuilder("👎  " + self.bot.get_user(trade_row['user_ids'][1]).name + " has rejected the trade from " + self.bot.get_user(trade_row['user_ids'][0]).name +"  👎","Looks like they weren't fond of the trade! Maybe try again after a couple minutes!","You both can make another trade again!",0x8F0700)
                    await extra_functions.edit_embed_message(self.bot,self.bot.get_channel(trade_row["current_channel"]).get_partial_message(trade_row["message_id"]),embed,"check cluster message function edit some")
                    await self.bot.pg_con.execute("DELETE from trade_messages WHERE message_id = $1;",reaction.message.id)
            

def setup(bot):
    bot.add_cog(Trade_Message(bot))
