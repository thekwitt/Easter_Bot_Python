import discord, random, json
from discord.ext.commands.errors import BadArgument
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'setlevel')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def setlevel_command(self, ctx, user: discord.User, level: int):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)

        if level > 100:
            embed = extra_functions.embedBuilder("⚠️   The Level cannot be higher than 100!  ⚠️ ","Remember to do **" + self.bot.prefix + "setlevel** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return
        elif level < 1:
            embed = extra_functions.embedBuilder("⚠️   The Level cannot be lower than 1!  ⚠️ ","Remember to do **" + self.bot.prefix + "setlevel** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return


        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_level = $1 WHERE UserID = $2;",level-1,user.id) #Update Loved                    
        embed = extra_functions.embedBuilder(user.name + " is now Level " + str(level) + "!","You can see the stats with **e!eggard** !","",0xC2D5F4)
        await extra_functions.send_embed_ctx(self.bot,ctx,embed,60,"set level function missing args send")
    
    @setlevel_command.error
    async def setlevel_command_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")
            #redo embed
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.CommandInvokeError):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + ctx.command.name + "** [User Mention] [Number 1-100]!\n\nExample: e!setlevel @MahoganyMan " + str(random.randint(1,100)),"",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function missing args send")
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","Remember to do **" + self.bot.prefix + "setlevel** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
        elif isinstance(error, BadArgument):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a number!  ⚠️ ","Remember to do **" + self.bot.prefix + "setlevel** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")

    @commands.command(name = 'setclusters')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def setclusters_command(self, ctx, user: discord.User, level: int):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)

        if level > 100:
            embed = extra_functions.embedBuilder("⚠️   The Cluster Count cannot be higher than 100!  ⚠️ ","Remember to do **" + self.bot.prefix + "setlevel** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return
        elif level < 1:
            embed = extra_functions.embedBuilder("⚠️   The Cluster Count cannot be lower than 1!  ⚠️ ","Remember to do **" + self.bot.prefix + "setlevel** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return


        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set clusters = $1 WHERE UserID = $2;",level,user.id) #Update Loved                    
        embed = extra_functions.embedBuilder(user.name + " now has " + str(level) + " clusters!","You can see the stats with **e!eggard** !","",0xC2D5F4)
        await extra_functions.send_embed_ctx(self.bot,ctx,embed,60,"set clusters function missing args send")
    
    @setclusters_command.error
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def setclusters_command_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")
            #redo embed
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.CommandInvokeError):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + ctx.command.name + "** [User Mention] [Number 1-100]!\n\nExample: e!setclusters @MahoganyMan " + str(random.randint(1,100)),"",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function missing args send")
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","Remember to do **" + self.bot.prefix + "setclusters** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
        elif isinstance(error, BadArgument):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a number!  ⚠️ ","Remember to do **" + self.bot.prefix + "setclusters** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")

    @commands.command(name = 'setcoins')
    async def setcoins_command(self, ctx, user: discord.User, level: int):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)

        if level > 10000:
            embed = extra_functions.embedBuilder("⚠️   The Gold Coins cannot be higher than 10000!  ⚠️ ","Remember to do **" + self.bot.prefix + "setcoins** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return
        elif level < 1:
            embed = extra_functions.embedBuilder("⚠️   The Gold Coins cannot be lower than 1!  ⚠️ ","Remember to do **" + self.bot.prefix + "setcoins** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return


        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set gold_coins = $1 WHERE UserID = $2;",level,user.id) #Update Loved                    
        embed = extra_functions.embedBuilder(user.name + " now has " + str(level) + " gold coins!","You can see the stats with **e!eggard** !","",0xC2D5F4)
        await extra_functions.send_embed_ctx(self.bot,ctx,embed,60,"set gold coins function missing args send")
    
    @setcoins_command.error
    async def setcoins_command_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")
            #redo embed
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.CommandInvokeError):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + ctx.command.name + "** [User Mention] [Number 1-100]!\n\nExample: e!setcoins @MahoganyMan " + str(random.randint(1,100)),"",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function missing args send")
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","Remember to do **" + self.bot.prefix + "setclusters** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
        elif isinstance(error, BadArgument):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a number!  ⚠️ ","Remember to do **" + self.bot.prefix + "setclusters** [User Mention] [Number 1-100]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")

    @commands.command(name = 'fillbasket')
    async def fillbasket_command(self, ctx, user: discord.User):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)

        u_obj = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id)        
        
        if 50 + (u_obj['basket_level'] * 25) == len(u_obj['basket_eggs']):
            embed = extra_functions.embedBuilder("⚠️   This basket is already full!  ⚠️ ","Make sure to do e!card [User Mention] **or** e!basket [User Mention] to see if the basket is full!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return
        
        limit = (50 + (u_obj['basket_level'] * 25)) - len(u_obj['basket_eggs'])
        basket = u_obj['basket_eggs']
        with open('JSON/Eggs.json') as f:
            egg_dic = json.load(f)        
            for x in range(0,limit):
                basket.append(random.choice(egg_dic['regular_eggs'])['id'])

        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set basket_eggs = $1 WHERE UserID = $2;",basket,user.id) #Update Loved   
        await extra_functions.change_roles(self.bot,ctx.message.channel,ctx.guild)
        embed = extra_functions.embedBuilder(user.name + " now has a full basket!","You can see the stats with **e!eggard** !","",0xC2D5F4)
        await extra_functions.send_embed_ctx(self.bot,ctx,embed,60,"set gold coins function missing args send")
    
    @fillbasket_command.error
    async def fillbasket_command_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")
            #redo embed
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.CommandInvokeError):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + ctx.command.name + "** [User Mention]!","",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function missing args send")
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","**" + self.bot.prefix + ctx.command.name + "** [User Mention]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
        elif isinstance(error, BadArgument):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","**" + self.bot.prefix + ctx.command.name + "** [User Mention]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")         

    @commands.command(name = 'fillcollection')
    async def fillcollection_command(self, ctx, user: discord.User):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)

        u_obj = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id)        
        
        if 30 == len(u_obj['collection_eggs']):
            embed = extra_functions.embedBuilder("⚠️   This Collection is already complete!  ⚠️ ","Make sure to do e!card [User Mention] **or** e!collection [User Mention] to see if the collection is already complete!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
            return
        
        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.message.guild.id) + " set collection_eggs = $1 WHERE UserID = $2;",['20101','20102','20103','20104','20105','20201','20202','20203','20204','20205','20301','20302','20303','20304','20305','20401','20402','20403','20404','20405','20501','20502','20503','20504','20505','20601','20602','20603','20604','20605'],user.id) #Update Loved   
        await extra_functions.add_secondary_role(self.bot,user,ctx.message.channel,ctx.guild,['20101','20102','20103','20104','20105','20201','20202','20203','20204','20205','20301','20302','20303','20304','20305','20401','20402','20403','20404','20405','20501','20502','20503','20504','20505','20601','20602','20603','20604','20605'])
        embed = extra_functions.embedBuilder(user.name + " now has a completed collection!","You can see the stats with **e!eggard** !","",0xC2D5F4)
        await extra_functions.send_embed_ctx(self.bot,ctx,embed,60,"set gold coins function missing args send")
    
    @fillcollection_command.error
    async def fillcollection_command_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedVar = discord.Embed(title="⚠️  Whoops!  ⚠️", description="Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function Missing Permissions incorrect send")
            #redo embed
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.CommandInvokeError):
            embed = extra_functions.embedBuilder(ctx.command.name + " User Guide","**" + self.bot.prefix + ctx.command.name + "** [User Mention]!","",0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"lottery function missing args send")
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","**" + self.bot.prefix + ctx.command.name + "** [User Mention]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")
        elif isinstance(error, BadArgument):
            embed = extra_functions.embedBuilder("⚠️   That wasn't a discord user!  ⚠️ ","**" + self.bot.prefix + ctx.command.name + "** [User Mention]!","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"trade function member not found send")    
def setup(bot):
    bot.add_cog(Tools(bot))