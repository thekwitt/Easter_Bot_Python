import discord, random, asyncio, time, json, math
from Custom_Fancy import new_fancy
from datetime import datetime
from discord.ext import commands
from database.updates import Database_Methods
from Extras.discord_functions import extra_functions

class Egg_Commands(commands.Cog): 
    # Level 1: compliment, Appreciate, Listening, Share Meme, 
    # Level 2: Hug, High Five, Pat, Fist Bump
    # Level 3: Gift, Chill, Scratch, Cool Handshake, Forehead Kiss

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'explore')
    async def explore_command(self,ctx,area):
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)        
        stats = await self.bot.pg_con.fetchrow("SELECT * FROM server_stats WHERE Guild_ID = $1",ctx.guild.id)
        explore_stats = stats['areas_explored']
        # Check for proper input
        areas = ['coney','hulking','woodlands','oracle','ethereal','crimson','void']
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if area.lower() in areas:
                # Check User's CD
                if user["cd_explorer"][areas.index(area.lower())] < int(datetime.now().timestamp()):
                    if(len(user['basket_eggs']) < 50 + (user['basket_level']) * 25):

                        index = ['coney','hulking','woodlands','oracle','ethereal','crimson','void'].index(area)        

                        if(user['basket_level'] < self.bot.levelrequirements[index]):
                            embedVar = discord.Embed(title="⚠️  Your Basket Level is too low!  ⚠️", description="You are only level " + str(user['basket_level']+1) + " while you need it to be level " + str(self.bot.levelrequirements[index]+1) + " to enter this area! To upgrade your basket, use " + self.bot.prefix + "upgrade if you have enough gold coins.", color=0xFFCC00)
                            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                        else:
                            server = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set cd_explorer_global = $1 WHERE UserID = $2;",datetime.now().timestamp() + 10,ctx.message.author.id) #Update Loved
                            await self.AreaExplorer(ctx,area,ctx.message.author.name,user)
                            explore_stats[index] += 1
                            await self.bot.pg_con.execute("UPDATE server_stats set areas_explored = $1 WHERE Guild_ID = $2;",explore_stats,ctx.guild.id) #Update Loved                    
                            await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
                            await extra_functions.add_secondary_role(self.bot,ctx.message.author,ctx.message.channel,ctx.guild,user['collection_eggs'])
                    else:
                        embed = extra_functions.embedBuilder("⚠️  Your Basket is full!  ⚠️"," Please sell some eggs to upgrade your basket or put some you want to keep in the case!","For more commands about upgrading your basket, use " + self.bot.prefix + "help egg!",0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function send timeout")
                else:
                    timestamp = user["cd_explorer"][areas.index(area.lower())] - int(datetime.now().timestamp() - 1)
                    embed = extra_functions.embedBuilder("⚠️  You recently explored this area!  ⚠️","You don't want the Crimson Wizard to spot you! Explore a different area until it is safe again!","Please wait " + str(int(timestamp/60)) + " minutes, " + str(int(timestamp) % 60) + " seconds to explore it again!",0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function send timeout")
            else:
                embedVar = discord.Embed(title="⚠️  That wasn't an area you can explore!  ⚠️", description="Make sure to do " + self.bot.prefix + "help egg to find the area you are looking for", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before collecting more! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @explore_command.error
    async def explore_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "explore** [Area]\n\n**__Areas__**\nThe Coney Stronghold - [coney] (Level 1)\nThe Hulking Fields - [hulking] (Level 3)\nThe Woodland Valley - [woodlands] (Level 6)\nThe Oracle River - [oracle] (Level 10)\nThe Ethereal Gardens - [ethereal] (Level 15)\nThe Crimson Grove - [crimson] (Level 21)\nThe Arcane Void - [void] (Level 30)","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"explore function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"explore function cooldown send")           
            return

    def nth(self,level):
        first = 1
        second = 0
        for x in range(1,level+1):
            first = first + second
            second += 1

        return first

    

    @commands.command(name = 'uncluster')
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def uncluster_command(self,ctx):
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)    
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if(user['clusters'] != 0):
                # Check User's CD
                if(len(user['basket_eggs']) < (50 + (user['basket_level']) * 25)):
                    embed = extra_functions.embedBuilder("🔨  The Eggsmith is working on your egg cluster!  🔨",random.choice(["\"I can tell that this cluster will be legendary!\"","\"I have a good feeling about this cluster!\"","\"My lord! This is a tough cluster!\"","\"How many eggs have you collected so far hero?\"","\"All this unclustering is making me hungry haha!\""]),"We don't want to break your cluster now!",0xFFFFE0)
                    message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"uncluster explore send 1")
                    await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set cd_explorer_global = $1 WHERE UserID = $2;",datetime.now().timestamp() + 10,ctx.message.author.id) #Update Loved
                    await asyncio.sleep(3)

                    settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
                    purr = settings['purification_count']
                    default = settings['default_server_settings']

                    buff = 1

                    

                    eggs = self.GetEggs(6,user['basket_level'],buff,len(user['basket_eggs']))
                    description_string = random.choice(["\"Now this is a fine cluster you have here! Enjoy the eggs!\"","\"I've never seen a cluster quite like this before!\"","\"I am glad the King hired you to save Cracklefest!\"","\"Phew! Almost broke this one!\"","\"Wow! What a rare find!\""])
                    description_string += "\n\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•\n"


                    egg_ids = []
                    unique_ids = []

                    egg_reg = []
                    egg_rare = []

                    if "1" in [item['id'][0] for item in eggs]:
                        for egg in [item for item in eggs if item['id'][0] == "1"]:
                            egg_reg.append(egg)
                            egg_ids.append(str(egg['id']))
                            

                    if "2" in [item['id'][0] for item in eggs]:
                        for egg in [item for item in eggs if item['id'][0] == "2"]:
                            if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                                unique_ids.append(str(egg['id']))
                                egg_rare.append(egg)
                            else:
                                egg_ids.append(str(egg['id']))
                                egg_rare.append(egg)


                    fields = self.Egg_String_Printer(egg_reg,egg_rare)

                    await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), clusters = clusters - 1, collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3 WHERE UserID = $4;",egg_ids,unique_ids,len(eggs),ctx.message.author.id) #Update Loved
                    await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    
                    
                    embed = extra_functions.embedBuilder("🥚  The Eggsmith has unclustered " + ctx.message.author.name + "'s cluster!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
                    
                    if fields[0] != "":
                        embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
                    if fields[1] != "":
                        embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
                    
                    await extra_functions.edit_embed_message(self.bot,message_obj,embed,"uncluster explore send 2")
                    await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
                    await extra_functions.add_secondary_role(self.bot,ctx.message.author,ctx.message.channel,ctx.guild,user['collection_eggs'])
                
                else:
                    embed = extra_functions.embedBuilder("⚠️  Your basket is full!  ⚠️","Your Basket has too many eggs! Just incase you have to make sure you have enough eggs when the cluster splits apart! You need to have atmost " + str((50 + (user['basket_level']) * 25) - (6 + (user['basket_level'])*2)) +  " eggs! Please sell some eggs to upgrade your basket or put some you want to keep in the case!","For more commands about upgrading your basket, use " + self.bot.prefix + "help egg!",0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function send timeout")
            else:
                embedVar = extra_functions.embedBuilder("⚠️  You don't have anymore clusters!  ⚠️","Make sure you have clusters by using " + self.bot.prefix + "eggard! You can collect egg clusters by reacting to any egg cluster messages that pop up on your server!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before collecting more! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @uncluster_command.error
    async def uncluster_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "uncluster**. Make sure you have an egg cluster in your inventory!","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  The Eggsmith is cleaning his tools!  ⚠️","Someone just unclustered an egg cluster!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return            

    @commands.command(name = 'mailbox')
    async def mailbox_command(self,ctx):
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)  
        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
        if user['cd_mailbox'] < int(datetime.now().timestamp()):
            cooldown = [14400,28800,43200,64800,86400]
            rando = random.randint(0,101)
            dialogue = random.choice(["Jethro!*\n\n\"**I wanted to send you something special! So take this gift as a token for your hard work!**\"\n\n*It contains a gift with a post card of his pet bear!*","Harn, one of the younglings!*\"\n\n**Hello! I appreciate everything you do for us! You are such a good person! I spent a few days collecting this for you! I hope it helps! :D**\"\n\n*It contains a gift and horribly sketched drawing of you made out of color sticks.*","Garth!*\n\n\"**Greetings Savior! It must not be easy to deal with collecting the eggs by yourself! Here a little small gift to keep you going!**\"\n\n*It contains a gift with a violet flower!*","Whitney!*\n\n\"**HELLO I AM GLAD YOU ARE GIVING OUR PEOPLE HOPE AND ENLIGHTENMENT! PLEASE ACCEPT THIS! THANK YOU!**\"\n\n*It contains a gift with an AURA OF HAPPINESS AHHH!*",])
            if(rando <= 100 and rando > 30): #Gold Coins
                coins = random.randint(1,4)
                await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set gold_coins = gold_coins + $1, cd_mailbox = $2 WHERE UserID = $3;",coins,datetime.now().timestamp() + cooldown[int(settings['default_server_settings'][1])-1],ctx.message.author.id) #Update Loved
                embed = extra_functions.embedBuilder("📭  " + ctx.message.author.name + " just opened the mail!  📭","*They got a piece of mail from "+dialogue+"\n\nThe gift was **" + str(coins) + " gold coins!**","Come back in " + str(cooldown[int(settings['default_server_settings'][1])-1]/3600) + " Hours!",0xFFFFE0)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"mailbox send 1")
            else: #Clusters
                clusters = random.randint(1,6)
                await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set clusters = clusters + $1, cd_mailbox = $2 WHERE UserID = $3;",clusters,datetime.now().timestamp() + cooldown[int(settings['default_server_settings'][1])-1],ctx.message.author.id) #Update Loved
                embed = extra_functions.embedBuilder("📭  " + ctx.message.author.name + " just opened the mail!  📭","*They got a piece of mail from "+dialogue+"\n\nThe gift was **" + str(clusters) + " clusters!**","Come back in " + str(cooldown[int(settings['default_server_settings'][1])-1]/3600) + " Hours!",0xFFFFE0)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"mailbox send 2")
            await self.bot.pg_con.execute("UPDATE server_stats set mailbox_openings = mailbox_openings + 1 WHERE Guild_ID = $1;",ctx.guild.id) #Update Loved                    
        else:
            timestamp = user["cd_mailbox"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  There isn't any new mail yet!  ⚠️", "You recently got the mail from your mailbox! New mail will arrive in **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @mailbox_command.error
    async def mailbox_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "mailbox**\nGet mail from the locals of The Coney Stronghold.","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return            

    @commands.command(name = 'toss',aliases = ["throw","chuck","yeet"])
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def toss_command(self,ctx,u_obj: discord.User):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)
        
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id) == None and not u_obj.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,u_obj.id)

        if u_obj.bot:
            embedVar = extra_functions.embedBuilder("⚠️  You can't throw eggs at bots! ⚠️","Bots work hard for you! Don't do that!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"toss bot function message send")
            self.toss_command.reset_cooldown(ctx)
            return
        
        if(ctx.message.author.id != u_obj.id):
            user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) 
            target = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id)  
            if len(user['basket_eggs']) != 0:
                if len(target['basket_eggs']) != 0:
                    if(len(target['basket_eggs']) < 50 + (target['basket_level']) * 25):
                        num = random.randint(1,100)
                        if num >= 50: # does nothing
                            basket = user['basket_eggs']
                            egg = random.randrange(len(basket))
                            basket.pop(egg)
                            embed = extra_functions.embedBuilder(ctx.message.author.name + " threw an egg at " + u_obj.name + "!","They stand there confused as the egg punts their face.",ctx.message.author.name + " loses a random egg from their basket.",0xFFA631)
                            await extra_functions.send_embed_ctx(self.bot,ctx,embed,360,"toss function send 1")
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set basket_eggs = $1 WHERE UserID = $2;",basket,ctx.message.author.id) #Update Loved
                        elif num >= 25: # Catch Egg
                            basket = user['basket_eggs']
                            t_basket = target['basket_eggs']
                            t_collect = target['collection_eggs']
                            egg = random.randrange(len(basket))
                            egg_id = basket[egg]
                            basket.pop(egg)
                            embed = extra_functions.embedBuilder(ctx.message.author.name + " threw an egg at " + u_obj.name + "!",u_obj.name + " catches the egg! What an act of reflexes!",ctx.message.author.name + " loses a random egg from their basket and " + u_obj.name + " keeps the egg for themselves!",0xFFA631)
                            await extra_functions.send_embed_ctx(self.bot,ctx,embed,360,"toss function send 1")
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set basket_eggs = $1 WHERE UserID = $2;",basket,ctx.message.author.id) #Update Loved
                            if "1" == egg_id[0]:
                                t_basket.append(egg_id)
                            elif "2" == egg_id[0]:
                                if egg_id in target['collection_eggs']:
                                    t_basket.append(egg_id)
                                else:
                                    t_collect.append(egg_id)
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set basket_eggs = $1, collection_eggs = $2 WHERE UserID = $3;",t_basket,t_collect,u_obj.id) #Update Loved

                        elif num < 25: # Lose Eggs
                            basket = user['basket_eggs']
                            t_basket = target['basket_eggs']
                            egg = random.randrange(len(basket))
                            basket.pop(egg)
                            lose_num = math.floor(0.05 * len(t_basket))
                            for x in range(0,lose_num):
                                t_basket.pop(random.randrange(len(t_basket)))
                            embed = extra_functions.embedBuilder(ctx.message.author.name + " threw an egg at " + u_obj.name + "!","At the impact of the egg hitting their face, some eggs spill out of their basket! What a mess!",ctx.message.author.name + " loses a random egg from their basket and " + u_obj.name + " loses 5% of their basket!",0xFFA631)
                            await extra_functions.send_embed_ctx(self.bot,ctx,embed,360,"toss function send 1")
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set basket_eggs = $1 WHERE UserID = $2;",basket,ctx.message.author.id) #Update Loved
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set basket_eggs = $1 WHERE UserID = $2;",t_basket,u_obj.id) #Update Loved
                    else:
                        embedVar = extra_functions.embedBuilder("⚠️  Their basket is full! ⚠️","Check their baskets by using " + self.bot.prefix + "basket [User Mention]!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                        self.toss_command.reset_cooldown(ctx)
                else:
                    embedVar = extra_functions.embedBuilder("⚠️  They don't have any eggs!  ⚠️","Check their basket by using " + self.bot.prefix + "basket [User Mention]!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                    self.toss_command.reset_cooldown(ctx)
            else:
                embedVar = extra_functions.embedBuilder("⚠️  You don't have any eggs!  ⚠️","Check your basket by using " + self.bot.prefix + "basket!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                self.toss_command.reset_cooldown(ctx)
        else:
            embedVar = extra_functions.embedBuilder("⚠️  You can't toss eggs at yourself!  ⚠️","Toss them at someone else!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")  
            self.toss_command.reset_cooldown(ctx)
    @toss_command.error
    async def toss_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "toss** [User Mention].\n\nExample: e!" + random.choice(["toss","throw","chuck","yeet"]) + " @EggCollector#1234","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function missing args send")
            self.toss_command.reset_cooldown(ctx)
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","Remember to do **" + self.bot.prefix + "toss** [User Mention].\n\nExample: " + random.choice("toss","throw","chuck","yeet") + "@EggCollector#1234","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            self.toss_command.reset_cooldown(ctx)
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let your arm rest!  ⚠️","Give your muscles some time to readjust after that throw you just did!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return            
        elif isinstance(error,commands.CommandInvokeError):
            self.toss_command.reset_cooldown(ctx)

    @commands.command(name = 'sell')
    async def sell_command(self,ctx):       
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if len(user['basket_eggs']) >= 10:
                list = user['basket_eggs']
                for x in range(0,10):
                    list.pop(random.randrange(len(user['basket_eggs'])))
                await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1, gold_coins = gold_coins + 1 WHERE UserID = $2;",list,ctx.message.author.id) #Update Loved                    
                await self.bot.pg_con.execute("UPDATE server_stats set eggs_sold = eggs_sold + 10 WHERE Guild_ID = $1;",ctx.guild.id) #Update Loved                    
                embed = extra_functions.embedBuilder("🛒   You sold ten eggs to the egg seller and got a gold coin!   🛒","You have **" + str(len(user['basket_eggs'])) + " eggs left** and now have **" + str(user['gold_coins'] + 1) + " gold coins**! Explore to get more eggs or open up any clusters you may have! I'll see you soon!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send ")
                await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
            else:
                embed = extra_functions.embedBuilder("⚠️  Your basket doesn't have enough eggs!!  ⚠️","You only have **" + str(len(user['basket_eggs'])) + " eggs!** You can only sell 10 eggs at one time for a gold coin!\nExplore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before selling eggs! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @sell_command.error
    async def sell_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "sell** Sell ten eggs for a gold coin","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return   

    @commands.command(name = 'megasell')
    async def megasell_command(self,ctx):       
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if len(user['basket_eggs']) >= 10:
                list = user['basket_eggs']
                num = 10*int(len(user['basket_eggs'])/10)
                for x in range(0,num):
                    list.pop(random.randrange(len(user['basket_eggs'])))
                await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1, gold_coins = gold_coins + $2 WHERE UserID = $3;",list,int(num/10),ctx.message.author.id) #Update Loved                    
                await self.bot.pg_con.execute("UPDATE server_stats set eggs_sold = eggs_sold + $1 WHERE Guild_ID = $2;",num,ctx.guild.id) #Update Loved                    
                embed = extra_functions.embedBuilder("💰   You sold " + str(num) + " eggs and got " + str(int(num/10)) + " gold coins!  💰","You have **" + str(len(user['basket_eggs'])) + " eggs left** and now have **" + str(int(num/10)+user['gold_coins']) + " gold coins**! Explore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send ")
                await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
            else:
                embed = extra_functions.embedBuilder("⚠️  Your basket doesn't have enough eggs!!  ⚠️","You only have **" + str(len(user['basket_eggs'])) + " eggs!** You can only sell multiples of 10 for gold coins!\nExplore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before selling eggs! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @megasell_command.error
    async def megasell_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "megasell\nSell as many eggs as you can for alot of gold coins.","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return   


    @commands.command(name = 'donate')
    async def donate_command(self,ctx,area,eggs):       
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)
        try:
            eggs = int(eggs)
        except:
            embed = extra_functions.embedBuilder("⚠️  That isn't a number!  ⚠️","Please refer to e!donate [Area] [Egg Amount]!","",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
            return
        
        if area.lower() == "void":
            embed = extra_functions.embedBuilder("⚠️  The Arcane Void cannot be purified!  ⚠️","This area is the entity of corruption and magic! Trying to purify 1% of it would take 1,000,000,000,000 eggs! Try another zone!","",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
            return
        
        areas = ['coney','hulking','woodlands','oracle','ethereal','crimson']
        index = areas.index(area.lower())        
        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
        counts = row['purification_count']
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if len(user['basket_eggs']) != 0:
                if len(user['basket_eggs']) >= eggs:
                    if(user['basket_level'] < self.bot.levelrequirements[index]):
                        embedVar = discord.Embed(title="⚠️  Your Basket Level is too low!  ⚠️", description="You are only level " + str(user['basket_level']+1) + " while you need it to be level " + str(self.bot.levelrequirements[index]+1) + " to contribute to the purification! To upgrade your basket, use " + self.bot.prefix + "upgrade if you have enough gold coins.", color=0xFFCC00)
                        embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                    else:
                        if area.lower() in areas:
                            list = random.sample(user['basket_eggs'],len(user['basket_eggs']) - eggs)
                            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1 WHERE UserID = $2;",list,ctx.message.author.id) #Update Loved                    
                            counts[index] += eggs
                            await self.bot.pg_con.execute("UPDATE guild_settings set purification_count = $1 WHERE Guild_ID = $2;",counts,ctx.guild.id) #Update Loved
                            purr = row['purification_count']
                            default = row['default_server_settings']
                            embed = extra_functions.embedBuilder("✨  " + ctx.message.author.name + " donated " + str(eggs) + " eggs!  ✨","You have " + str(len(user['basket_eggs']) - eggs) + " eggs left! **|** The donation for this area is **" + str(purr[index]) + "/" + default[2] + "!**\n\nExplore to get more eggs or open up any clusters you may have!\n\n**If you meet the donation goal, you can get double the eggs from here!**","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send ")
                            await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)

                            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
                            default = settings['default_server_settings']
                            multiplier = 1
                            
                            if(counts[index] >= int(default[2]) and counts[index] - eggs < int(default[2])):
                                dialogues=["The villages have been restored and the corrupted coronas have been purified. The air finally thins and becomes clearer to breathe. Jethro the King is forever grateful to see his people thrive once again.","The damaged fields and terrain have been filled and restored back to full health! While the float islands are still held by magic, everyone can grow crop to feed 10x their size!","The trees suddenly become fuller and thicker! They bloom with life once more and resources can finally be acquired without harm!","The rivers suddenly triple in width and the water flows faster and stronger! The drought is no more!","The conoras trapped within the gardens suddenly feel different. They can walk outside the boundaries once again! It has been ages since the last time they saw their family and friends!","Using the minerals and arcane coating from the eggs, The eggsmith melted them into a royal sceptre of arcane light for Jethro The King! He stands alone to the boundaries of the grove and casts a mighty forcefield around the entire area! Not even the Crimson Wizard, the mightiest being alive, couldn't break the spell! Anything corrupted with arcane energy was trapped helplessly! Jethro sighs in relief. Finally the war is over."]
                                names = ["The Coney Stronghold","The Hulking Fields","The Woodland Valley","The Oracle Rivers","The Ethereal Garden","The Crimson Grove"]
                                embedVar = discord.Embed(title="☀️  " + names[index] + " has been purified!  ☀️", description=dialogues[index] + "\n\nIf you explore this area, you will now get double the eggs!", color=0xFFCC00)
                                embedVar.set_footer(text = "Check out the purification process with e!serverstats!")
                                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,120,"set settings function message low send")
                            
                                for x in range(0,5):
                                    if not (counts[x] >= int(default[2])):
                                        return
                                names = ["The Coney Stronghold","The Hulking Fields","The Woodland Valley","The Oracle Rivers","The Ethereal Garden","The Crimson Grove"]
                                embedVar = discord.Embed(title="☀️  All of Coneyford has been purified!  ☀️", description="If you explore any area (except The Arcane Void), you will now get triple the eggs!\n\n**(A new command has been unlocked! Try e!epilogue)**", color=0xFFCC00)
                                embedVar.set_footer(text = "Check out the purification process with e!serverstats!")
                                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"set settings function message low send")

                            
                        else:
                            embedVar = discord.Embed(title="⚠️  That isn't an area!  ⚠️", description="Make sure to do coney,hulking,woodlands,oracle,ethereal or crimson for [Area]!", color=0xFFCC00)
                            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
                else:
                    embed = extra_functions.embedBuilder("⚠️  Your basket doesn't have enough eggs!!  ⚠️","You only have **" + str(len(user['basket_eggs'])) + " eggs!** Explore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
            else:
                embed = extra_functions.embedBuilder("⚠️  Your basket is empty!  ⚠️","Explore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before collecting more! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @donate_command.error
    async def donate_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "donate** [Area] [Egg Amount]\n Areas: coney,hulking,woodlands,oracle,ethereal,crimson","If this was a mistake, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"donate function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"donate function cooldown send")           
            return   


    @commands.command(name = 'lottery')
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def lottery_command(self,ctx,money: int):       
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)
        stats = await self.bot.pg_con.fetchrow("SELECT * FROM server_stats WHERE Guild_ID = $1",ctx.guild.id)
        lottery_stats = stats['lottery_results']

        if money > user['gold_coins']:
            embed = extra_functions.embedBuilder("⚠️  You don't have that much gold coins!  ⚠️","You only have " + str(user['gold_coins']) + " gold coins!","" + self.bot.prefix + "lottery [Money]",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
            self.lottery_command.reset_cooldown(ctx)
            return
        
        if money > 100:
            embed = extra_functions.embedBuilder("⚠️  That is too much money for the lottery!  ⚠️","Make sure you enter between 1-5 for your gold coins!","" + self.bot.prefix + "lottery [Money]",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
            self.lottery_command.reset_cooldown(ctx)
            return

        if money < 1:
            embed = extra_functions.embedBuilder("⚠️  You need to enter atleast one gold coin!  ⚠️","Make sure you enter between 1-5 for your gold coins!","" + self.bot.prefix + "lottery [Money]",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
            self.lottery_command.reset_cooldown(ctx)
            return

        rando = random.randint(0,101)

        if rando > 95:
            lottery_stats[1] += 1
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set gold_coins = gold_coins + $1 WHERE UserID = $2;",money*3,ctx.message.author.id) #Update Loved                    
            embed = extra_functions.embedBuilder("⠀⠀  ⠀💰    U  L  T  R  A     W  I  N  N  E  R    💰⠀⠀  ⠀","```   YOU WON " + str(money*3).zfill(3) + " GOLD COINS\n" + self.lottery_cards(3) + "```","You won triple your money! You have " + str(user['gold_coins'] + ((money * 3))) + " gold coins now!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function lottery send 1")
        elif rando > 80:
            lottery_stats[1] += 1
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set gold_coins = gold_coins + $1 WHERE UserID = $2;",money*2,ctx.message.author.id) #Update Loved                    
            embed = extra_functions.embedBuilder("⠀⠀  ⠀💰    M  E  G  A     W  I  N  N  E  R    💰⠀⠀  ⠀","```   YOU WON " + str(money*2).zfill(3) + " GOLD COINS\n" + self.lottery_cards(2) + "```","You won double your money!! You have " + str(user['gold_coins'] + ((money * 2))) + " gold coins now!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function lottery send 1")
        elif rando > 50:
            lottery_stats[1] += 1
            embed = extra_functions.embedBuilder("⠀⠀  ⠀💰    W  I  N  N  E  R    💰⠀⠀  ⠀","```   YOU WON " + str(money*1).zfill(3) + " GOLD COINS\n" + self.lottery_cards(1) + "```","You won your money back! You have " + str(user['gold_coins']) + " gold coins now!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function lottery send 1")
        else:
            lottery_stats[0] += 1
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set gold_coins = gold_coins - $1 WHERE UserID = $2;",money,ctx.message.author.id) #Update Loved                    
            embed = extra_functions.embedBuilder("⠀     ⠀⠀🔥    L  O  S  E  R    🔥⠀⠀  ⠀","```   YOU LOST " + str(money).zfill(3) + " GOLD COINS\n" + self.lottery_cards(0) + "```","You lost the lottery! You have " + str(user['gold_coins'] - money) + " gold coins left!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function lottery send 1")
            

        await self.bot.pg_con.execute("UPDATE server_stats set Lottery_Results = $1 WHERE Guild_ID = $2;",lottery_stats,ctx.guild.id) #Update Loved                    
            
        #if()
        #    list.pop(random.randrange(len(user['basket_eggs'])))
        #await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1, gold_coins = gold_coins + 1 WHERE UserID = $2;",list,ctx.message.author.id) #Update Loved                    
        #embed = extra_functions.embedBuilder("You sold ten eggs and got a gold coin!","You have " + str(len(user['basket_eggs'])) + " eggs left! Explore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
        #await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send ")

    @lottery_command.error
    async def lottery_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "lottery** [Money]\nMake sure money is between 1-5!","",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function missing args send")
        elif isinstance(error,TypeError):
            embed = extra_functions.embedBuilder("⚠️  That isn't money!  ⚠️","Make sure you enter between 1-100 for your gold coins!","**" + self.bot.prefix + "lottery** [Money]",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function sell send timeout")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  The Lottery Machine is Reloading!  ⚠️","Someone recently bought lottery!","Please wait " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function cooldown send")           
            return   
        self.lottery_command.reset_cooldown(ctx)

    def level_calc(self,level):
        if level < 49:
            return 10 + (5*level) + int(0.1 * (level ** 2))
            #return 10 + (5 * level)
        else:
            level -= 49
            return 520 +(50*level) + ((10*(self.nth(level+1)))-10)
            #return 300 + (50 * (level - 49))
        

    @commands.command(name = 'upgrade')
    #@commands.cooldown(1, 60, commands.BucketType.member)
    async def upgrade_command(self,ctx):
        # Check for Null User
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)        
        if user['gold_coins'] >= self.level_calc(user["basket_level"]):
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set gold_coins = gold_coins - $1, basket_level = basket_level + 1 WHERE UserID = $2;",self.level_calc(user["basket_level"]),ctx.message.author.id) #Update Loved                    
            await self.bot.pg_con.execute("UPDATE server_stats set upgrades = upgrades + 1 WHERE Guild_ID = $1;",ctx.guild.id) #Update Loved                    
            embed = extra_functions.embedBuilder("🔺  "+ctx.message.author.name + " upgraded their basket to Level " + str(user['basket_level']+2) + " with " + str(self.level_calc(user["basket_level"])) + " gold coins!   🔺","You have **" + str(user['gold_coins'] - (self.level_calc(user["basket_level"]))) + " coins left**! **This time you need " + str(self.level_calc(user["basket_level"]+1)) + " gold coins to level up!**\nExplore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
            if(self.upgrade_unlock_dialogue(user['basket_level']+2) != ""):
                embed.add_field(name = "New Area!", value= self.upgrade_unlock_dialogue(user['basket_level']+2))
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,90,ctx.command.name + " function upgrade send ")

        else:
            embed = extra_functions.embedBuilder("⚠️  You don't have enough gold coins!  ⚠️","You only have **" + str(user['gold_coins']) + " gold coins!** You need a total of " + str(self.level_calc(user["basket_level"])) + " gold coins!","For more commands about getting gold coins, use " + self.bot.prefix + "help egg!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function upgrade send timeout")

    @upgrade_command.error
    async def upgrade_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "upgrade**\n\nUse this command to upgrade your basket!","e!help egg",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  You just upgraded your basket!  ⚠️","The basket will fall apart if you upgrade again too soon!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return

    def upgrade_unlock_dialogue(self,level):
        if(level == 3):
            return "*The misty clouds fade away as your basket clears the path towards the next area.*\n\n**You now have access to explore The Area known as The Hulking Fields!***\n\nYou can explore this area by using **" + self.bot.prefix + "explore** hulking!\nOr you can use **" + self.bot.prefix + "atlas** hulking to learn about the lore of the land!"
        elif(level == 6):
            return "*The misty clouds fade away as your basket clears the path towards the next area.*\n\n***You now have access to explore The Area known as The Woodland Valley!***\n\nYou can explore this area by using **" + self.bot.prefix + "explore** woodlands!\nOr you can use **" + self.bot.prefix + "atlas** woodlands to learn about the lore of the land!"
        elif(level == 10):
            return "*The misty clouds fade away as your basket clears the path towards the next area.*\n\n***You now have access to explore The Area known as The Oracle Rivers!***\n\nYou can explore this area by using **" + self.bot.prefix + "explore** oracle!\nOr you can use **" + self.bot.prefix + "atlas** oracle to learn about the lore of the land!"
        elif(level == 15):
            return "*The misty clouds fade away as your basket clears the path towards the next area.*\n\n***You now have access to explore The Area known as The Ethereal Gardens!***\n\nYou can explore this area by using **" + self.bot.prefix + "explore** ethereal!\nOr you can use **" + self.bot.prefix + "atlas** ethereal to learn about the lore of the land!"
        elif(level == 21):
            return "*The misty clouds fade away as your basket clears the path towards the next area.*\n\n***You now have access to explore The Area known as The Crimson Grove!***\n\nYou can explore this area by using **" + self.bot.prefix + "explore** crimson!\nOr you can use **" + self.bot.prefix + "atlas** crimson to learn about the lore of the land!"
        return ""

    @commands.command(name = 'incase')
    async def incase_command(self,ctx,egg_id):
        # Check for Null User
        author = ctx.message.author
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)
        
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)        
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if len(user['basket_eggs']) != 0:
                user_case = user['case_eggs']
                user_basket = user['basket_eggs']
                if egg_id in user_basket:
                    if len(user_case) < 20:
                        user_basket.remove(egg_id)
                        user_case.append(egg_id)
                        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1, case_eggs = $2 WHERE UserID = $3;",user_basket,user_case,ctx.message.author.id) #Update Loved                    
                        
                        with open('JSON/Eggs.json') as f:
                            egg_dic = json.load(f)
                        egg_obj = [item for item in (egg_dic['regular_eggs'] + egg_dic['collectible_eggs']) if item['id'] == egg_id][0]
                        
                        embed = extra_functions.embedBuilder(author.name + " has added a " + egg_obj['name'] + " to their display case!",egg_obj['emoji'] + " will no longer be sold while in the display case! You can see all your eggs in the display case with " + self.bot.prefix + "case!","If this was a mistake, use " + self.bot.prefix + "outcase [Egg ID] to put the egg back in the basket!",0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function incase send ")
                        await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
                    else:
                        embed = extra_functions.embedBuilder("⚠️  Your display case is full!  ⚠️","Looks like you don't anymore room in your display case! Your max is 20 Eggs! Make sure to use " + self.bot.prefix + "outcase [Egg ID] to make some room if you really want that egg in your display case.","To see egg ids in your case, use " + self.bot.prefix + "case and click/tap the egg to see it's id! The ID is between the colons -> :10001: !",0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function incase send timeout")
                else:
                    embed = extra_functions.embedBuilder("⚠️  You don't have that egg!  ⚠️","Looks like you don't have that egg in your basket!","To see if your basket has that egg, use " + self.bot.prefix + "basket and click/tap the egg to see it's id! The ID is between the colons -> :10001: !",0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function incase send timeout")
            else:
                embed = extra_functions.embedBuilder("⚠️  Your basket is empty!!  ⚠️","Looks like you don't have any eggs in your basket! Explore to get more eggs or open up any clusters you may have!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function incase send timeout")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before collecting more! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")

    @incase_command.error
    async def incase_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "incase ** [Egg ID]\nExample: " + self.bot.prefix + "incase 10001","If you need more help, make sure to use " + self.bot.prefix + "manual or " + self.bot.prefix + "help egg!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return   

    @commands.command(name = 'outcase')
    async def outcase_command(self,ctx,egg_id):
        # Check for Null User
        author = ctx.message.author
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)        
        if user['cd_explorer_global'] < int(datetime.now().timestamp()):
            if len(user['case_eggs']) != 0:
                user_case = user['case_eggs']
                user_basket = user['basket_eggs']
                if egg_id in user_case:
                    if len(user_basket) < (50 + (25 * user['basket_level'])):
                        user_case.remove(egg_id)
                        user_basket.append(egg_id)
                        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1, case_eggs = $2 WHERE UserID = $3;",user_basket,user_case,ctx.message.author.id) #Update Loved                    
                        
                        with open('JSON/Eggs.json') as f:
                            egg_dic = json.load(f)
                        egg_obj = [item for item in (egg_dic['regular_eggs'] + egg_dic['collectible_eggs']) if item['id'] == egg_id][0]
                        
                        embed = extra_functions.embedBuilder(author.name + " has removed a " + egg_obj['name'] + " from their display case!",egg_obj['emoji'] + " will no longer be displayed in your display case! You can see all your eggs in the display case with " + self.bot.prefix + "case!","If this was a mistake, use " + self.bot.prefix + "incase [Egg ID] to put the egg back in the display case!",0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function outcase send ")
                        await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
                    else:
                        embed = extra_functions.embedBuilder("⚠️  Your basket is full!  ⚠️","Looks like you don't anymore room in your basket! Your max is " + str((50 + (25 * user['basket_level']))) + " Eggs! Make sure to use " + self.bot.prefix + "incase [Egg ID] to make some room if you really want that egg in your basket.","To see egg ids in your case, use " + self.bot.prefix + "basket and click/tap the egg to see it's id! The ID is between the colons -> :10001: !",0xFFCC00)
                        await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function outcase send timeout")
                else:
                    embed = extra_functions.embedBuilder("⚠️  You don't have that egg!  ⚠️","Looks like you don't have that egg in your basket!","To see if your basket has that egg, use " + self.bot.prefix + "basket and click/tap the egg to see it's id! The ID is between the colons -> :10001: !",0xFFCC00)
                    await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function outcase send timeout")
            else:
                embed = extra_functions.embedBuilder("⚠️  Your display case is empty!  ⚠️","Looks like you don't have any eggs in your display case! Explore to get more eggs or open up any clusters you may have and put them in your display case using " + self.bot.prefix + "incase [Egg ID]!","For more commands about getting eggs, use " + self.bot.prefix + "help egg!",0xFFCC00)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,35,ctx.command.name + " function outcase send timeout")
        else:
            timestamp = user["cd_explorer_global"] - int(datetime.now().timestamp() - 1)
            embedVar = extra_functions.embedBuilder("⚠️  You recently got new eggs!  ⚠️", "Let yourself reorganize your basket before collecting more! It'll only take **" + extra_functions.time_to_string(timestamp) + "**!","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!", 0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"outcase function message low send")

    @outcase_command.error
    async def outcase_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + "outcase ** [Egg ID]\nExample: " + self.bot.prefix + "outcase 10001","If you need more help, make sure to use " + self.bot.prefix + "manual or " + self.bot.prefix + "help egg!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function missing args send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Let yourself rest first!  ⚠️","You recently explored somewhere and need to rest!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after+1) % 60) + " seconds!",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name + " function cooldown send")           
            return   

    async def AreaExplorer(self,ctx,area,name,user): #Pushing Eggs into User
        # Get Index
        area = area.lower()
        cooldowns = [120,240,300,480,600] # 2 min, 4 min, 5 min , 10 min, 30 min
        index = ['coney','hulking','woodlands','oracle','ethereal','crimson','void'].index(area)        

        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
        purr = settings['purification_count']
        default = settings['default_server_settings']
        multiplier = 1

        if index != 6:
            if(purr[0] >= int(default[2]) and purr[1] >= int(default[2]) and purr[2] >= int(default[2]) and purr[3] >= int(default[2]) and purr[4] >= int(default[2]) and purr[5] >= int(default[2])):
                multiplier = 3
            elif(purr[index] >= int(default[2])):
                multiplier = 2
        

        if(index == 0): # Coney
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]

            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring the Coney Stronghold!  🔎",str("*" + random.choice(dialogue['prologue'])).replace("[User]",name) + "*",random.choice(["They have a good feeling about this exploration!","Nothing can stop them this time!","They smell a collectible egg!"]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"coney explore send 1")
            eggs = self.GetEggs(index,user['basket_level'],multiplier,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"

            egg_ids = []
            unique_ids = []

            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)


            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    

            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Coney Stronghold!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"coney explore send 2")
        elif index == 1: # Hulking
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]

            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring the The Hulking Fields!  🔎",str("*" + random.choice(dialogue['prologue'])).replace("[User]",name) + "*",random.choice(["They have a good feeling about this exploration!","Nothing can stop them this time!","They smell a collectible egg!"]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"hulking explore send 1")
            eggs = self.GetEggs(index,user['basket_level'],multiplier,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"


            egg_ids = []
            unique_ids = []
        
            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)

            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    
            
            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Hulking Fields!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"hulking explore send 2")
        elif index == 2: # Woodlands
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]

            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring the The Woodland Valley!  🔎",str("*" + random.choice(dialogue['prologue'])).replace("[User]",name) + "*",random.choice(["They have a good feeling about this exploration!","Nothing can stop them this time!","They smell a collectible egg!"]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"woodlands explore send 1")
            eggs = self.GetEggs(index,user['basket_level'],multiplier,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            
            egg_ids = []
            unique_ids = []

            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)


            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    
            
            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Woodland Valley!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"woodlands explore send 2")  
        elif index == 3: # Oracle
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]

            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring the The Oracle Rivers!  🔎",str("*" + random.choice(dialogue['prologue'])).replace("[User]",name) + "*",random.choice(["They have a good feeling about this exploration!","Nothing can stop them this time!","They smell a collectible egg!"]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"oracle explore send 1")
            eggs = self.GetEggs(index,user['basket_level'],multiplier,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            
            egg_ids = []
            unique_ids = []

            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)


            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    

            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Oracle Rivers!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"oracle explore send 2")    
        elif index == 4: # Ethereal
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]

            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring the The Ethereal Gardens!  🔎",str("*" + random.choice(dialogue['prologue'])).replace("[User]",name) + "*",random.choice(["They have a good feeling about this exploration!","Nothing can stop them this time!","They smell a collectible egg!"]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"ethereal explore send 1")
            eggs = self.GetEggs(index,user['basket_level'],multiplier,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            
            egg_ids = []
            unique_ids = []

            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)

            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    
            
            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Ethereal Gardens!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"ethereal explore send 2")    
        elif index == 5: # Crimson
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]
            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring the The Crimson Grove!  🔎",str("*" + random.choice(dialogue['prologue'])).replace("[User]",name) + "*",random.choice(["They have a good feeling about this exploration!","Nothing can stop them this time!","They smell a collectible egg!"]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"crimson explore send 1")
            eggs = self.GetEggs(index,user['basket_level'],multiplier,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            
            egg_ids = []
            unique_ids = []

            egg_reg = []
            egg_rare = []

            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)


            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    
            
            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Crimson Grove!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"crimson explore send 2")    
        if(index == 6): # Void
            with open('JSON/Dialogue.json') as f:
                j = json.load(f)
            dialogue = j[area]

            embed = extra_functions.embedBuilder("🔎  " + name + " is exploring The Arcane Void!" + "  🔎",str("*" + random.choice(dialogue['prologue']).replace("[User]",name)) + "*",random.choice(["What is this place?","They seem scared..","Hopefully something good comes out of this."]),0xFFFFE0)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"coney explore send 1")
            eggs = self.GetEggs(8,user['basket_level'],1,len(user['basket_eggs']))
            await asyncio.sleep(3)
            description_string = ""
            if len(eggs) == 1:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","an egg").replace("[Pro1]","it").replace("[Pro2]","it's") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            elif len(eggs) == 2:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","a couple eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"
            else:
                description_string += str("*" + random.choice(dialogue['dialogue'])).replace("[User]",name).replace("[Egg]","some eggs").replace("[Pro1]","them").replace("[Pro2]","their") + "*\n⠀\n⠀\n__**Here are the eggs they collected!**__\n\n•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•´¨•.¸¸.•"

            egg_ids = []
            unique_ids = []

            egg_reg = []
            egg_rare = []

            if "1" in [item['id'][0] for item in eggs]:
                description_string += "\n"
                for egg in [item for item in eggs if item['id'][0] == "1"]:
                    egg_reg.append(egg)
                    egg_ids.append(str(egg['id']))
                    

            if "2" in [item['id'][0] for item in eggs]:
                for egg in [item for item in eggs if item['id'][0] == "2"]:
                    if not egg['id'] in user['collection_eggs'] and not egg['id'] in unique_ids:
                        unique_ids.append(str(egg['id']))
                        egg_rare.append(egg)
                    else:
                        egg_ids.append(str(egg['id']))
                        egg_rare.append(egg)


            fields = self.Egg_String_Printer(egg_reg,egg_rare)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
            cds = user['cd_explorer']
            cds[index] = int(datetime.now().timestamp()) + int(cooldowns[int(settings["default_server_settings"][0])-1])
            await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set Basket_Eggs = array_cat(Basket_Eggs,$1), collection_eggs = array_cat(collection_eggs,$2), eggs_collected = eggs_collected + $3, cd_explorer = $4 WHERE UserID = $5;",egg_ids,unique_ids,len(eggs),cds,ctx.message.author.id) #Update Loved
            await self.bot.pg_con.execute("UPDATE server_stats set eggs_collected = eggs_collected + $1 WHERE Guild_ID = $2;",len(eggs),ctx.guild.id) #Update Loved                    

            embed = extra_functions.embedBuilder("🥚  " + name + " has finished exploring The Arcane Void!  🥚",description_string,"Click/tap the egg to see their ids and use e!eggcyclopedia [Egg ID] To learn about them!",0xFFFFE0)
            if fields[0] != "":
                embed.add_field(name ="Regular Eggs", value = fields[0], inline = False)
            if fields[1] != "":
                embed.add_field(name ="Collectible Eggs", value = fields[1], inline = False)
            await extra_functions.edit_embed_message(self.bot,message_obj,embed,"coney explore send 2")

    def GetEggs(self,area,level,multi,max): # Calculate if reg or collect egg
        count = random.randint(1,multi*(5+int(level/3)))
        basket_max = 50 + (level) * 25
        if max + count > basket_max:
            count = basket_max - max
        eggs = []
        if area == 0:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 5:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(["Solid","Triangle","Castle","Unique"]),egg_dic['regular_eggs']))))
                else:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == "Coney",egg_dic['collectible_eggs']))))
            return eggs
        elif area == 1:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 5:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(['Food','Melted','Cream'] ),egg_dic['regular_eggs']))))
                else:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == "Hulking",egg_dic['collectible_eggs']))))
            return eggs
        elif area == 2:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 7:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(['Dotted','Swirl','Diamonds']),egg_dic['regular_eggs']))))
                else:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == "Woodlands",egg_dic['collectible_eggs']))))
            return eggs
        elif area == 3:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 5:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(['Waves','ZigZag','Water','Mix 1']),egg_dic['regular_eggs']))))
                else:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == "Oracle",egg_dic['collectible_eggs']))))
            return eggs
        elif area == 4:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 5:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(['Cow','Zebra','Tiger','Reptile','Giraffe',"Flowers"]),egg_dic['regular_eggs']))))
                else:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == "Ethereal",egg_dic['collectible_eggs']))))
            return eggs
        elif area == 5:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 5:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(['Glass','Hexigons','Clouds','Stars']),egg_dic['regular_eggs']))))
                else:
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == "Crimson",egg_dic['collectible_eggs']))))
            return eggs
        elif area == 6:
            for x in range(0,count):
                rand = random.randint(0,101)
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                if rand <= 101 and rand >= 2:
                    eggs.append(random.choice(egg_dic['regular_eggs']))
                else:
                    eggs.append(random.choice(egg_dic['collectible_eggs']))
            return eggs
        elif area == 7:
            with open('JSON/Eggs.json') as f:
                egg_dic = json.load(f)
            eggs.append(random.choice(egg_dic['collectible_eggs']))
            return eggs
        elif area == 8: # Void
            with open('JSON/Eggs.json') as f:
                egg_dic = json.load(f)
                count = random.randint(1,int(level/3))
                for x in range(0,count):
                    eggs.append(random.choice(list(filter(lambda item: item['type'] == random.choice(['Void','Spell','Fury']),egg_dic['regular_eggs']))))
            return eggs

    def Egg_String_Printer(self,eggs,rare):
        fields = ["",""]
        if len(eggs) > 0:
            if len(eggs) <= 25:
                brackets = extra_functions.bracket_array(1)
                string = "⠀\n"
                #string += str(brackets[0][0]) + str(brackets[0][1]*(len(eggs))) + str(brackets[0][2]) +"\n" + str(brackets[2][0])
                for egg in eggs:
                    string += egg['emoji']
                #string += "\n" + str(brackets[1][0]) + str(brackets[1][1]*(len(eggs))) + str(brackets[1][2]) +"\n"
                fields[0] = string + "\n⠀"
            else:
                string = "⠀\n"
                #string += str(brackets[0][0]) + str(brackets[0][1]*(len(eggs))) + str(brackets[0][2]) +"\n" + str(brackets[2][0])
                for x in range (0,25):
                    string += eggs[x]['emoji']
                #string += "\n" + str(brackets[1][0]) + str(brackets[1][1]*(len(eggs))) + str(brackets[1][2]) +"\n"
                fields[0] = string + "\n**And " + str(len(eggs)-25) + " more eggs!**\n⠀"

        if len(rare) > 0:
            brackets = extra_functions.bracket_array(2)
            string = "⠀\n"
            #string += brackets[0][0] + str(brackets[0][1]*(len(rare))) + brackets[0][2] +"\n" + brackets[2][0]
            for egg in rare:
                string += egg['emoji']
            #string += "\n"+brackets[1][0] + str(brackets[1][1]*(len(rare))) + brackets[1][2] +"\n"
            fields[1] = string + "\n⠀"

        return fields

    def lottery_cards(self,type):
        if type == 0: # Bad Cards
            with open('lottery/bad_cards.txt',encoding='utf-8', mode = 'r') as f:
                bad = " ".join(line for line in f).split(',')
            return random.choice(bad)
        if type == 1: # Good Cards
            with open('lottery/good_cards.txt',encoding='utf-8', mode = 'r') as f:
                good = " ".join(line for line in f).split(',')
            return random.choice(good)
        if type == 2: # Great Cards
            with open('lottery/great_cards.txt',encoding='utf-8', mode = 'r') as f:
                good = " ".join(line for line in f).split(',')
            return random.choice(good)
        if type == 3: # Amazing Cards
            with open('lottery/amazing_cards.txt',encoding='utf-8', mode = 'r') as f:
                good = " ".join(line for line in f).split(',')
            return random.choice(good)

def setup(bot):
    bot.add_cog(Egg_Commands(bot))