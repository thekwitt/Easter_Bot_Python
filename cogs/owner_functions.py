import discord
from collections import OrderedDict
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'flushat')
    @commands.is_owner()
    async def flushat_command(self, ctx, user: discord.User):
        #self.bot.ready = False
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)
        
        row = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id)
        await self.bot.pg_con.execute("UPDATE " + "g_" + str(ctx.guild.id) + " set collection_eggs = $1 WHERE UserID = $2;",list(OrderedDict.fromkeys(row['collection_eggs'])),ctx.message.author.id) #Update Loved
        #self.bot.ready = True

    @commands.command(name = 'flushall')
    @commands.is_owner()
    async def flushall_command(self, ctx):
        self.bot.ready = False
        for guild in self.bot.guilds:
            rows = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(guild.id))
            if rows:
                for x in range(0,len(rows)):
                    if rows[x]['collection_eggs']:
                        await self.bot.pg_con.execute("UPDATE " + "g_" + str(guild.id) + " set collection_eggs = $1 WHERE UserID = $2;",list(OrderedDict.fromkeys(rows[x]['collection_eggs'])),rows[x]['userid']) #Update Loved
        self.bot.ready = True
        await ctx.send("Done.")
    
    @flushall_command.error
    async def flushall_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            pass

def setup(bot):
    bot.add_cog(Owner(bot))