import discord
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Join_Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        if(self.bot.ready):

            await self.bot.pg_con.execute("""INSERT INTO guild_settings (Guild_ID,Version) VALUES ($1,$2) ON CONFLICT (Guild_ID) DO NOTHING;""",guild.id,self.bot.db_version)
            await self.bot.pg_con.execute("""INSERT INTO server_stats (Guild_ID) VALUES ($1) ON CONFLICT (Guild_ID) DO NOTHING;""",guild.id)
            await self.bot.pg_con.execute("UPDATE guild_settings set message_state = $1 WHERE Guild_ID = $2;",-2,guild.id) #Update Loved
            if await self.bot.pg_con.fetchrow("SELECT 1 FROM information_schema.tables WHERE table_name = $1","g_" + str(guild.id)) == None:
                embedVar = discord.Embed(title="📕  A New Adventure Awaits!  📕", description="⠀\nLooks like you are ready for a new adventure! To begin, please do **" + self.bot.prefix + "start** anywhere to activate the bot!\n**You must have channel perms to use e!start!**\n⠀", color=0x16C326)
                embedVar.set_footer(text = "If you encounter any problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                
                channel = None
                channel = await extra_functions.check_for_main_channel(guild)
                if channel != None:
                    await extra_functions.send_embed_channel(self.bot,channel,embedVar,999,"guild join welcome message send")

            else:
                embedVar = discord.Embed(title="📕  A New Adventure Returns!  📕", description="⠀\nLooks like you brought the bot back!! We've saved your progress so you can continue! Use **" + self.bot.prefix + "start** to resume the story!\n**You must have channel perms to use e!start!**\n⠀", color=0x16C326)
                embedVar.set_footer(text = "If you encounter any problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                
                channel = None
                channel = await extra_functions.check_for_main_channel(guild)
                if channel != None:
                    await extra_functions.send_embed_channel(self.bot,channel,embedVar,999,"guild join welcome back message send")
                    
                await self.bot.pg_con.execute("UPDATE guild_settings set possible_channel_ids = '{}', message_state = '-2' WHERE Guild_ID = $1;",guild.id) #Update Loved

            await self.bot.pg_con.execute(
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
            
            extra_functions.logger_print (guild.name + " with ID: " + str(guild.id) + " has entered the database")

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        if(self.bot.ready):
            extra_functions.logger_print (guild.name + " with ID: " + str(guild.id) + " has kicked the bot!")


    @commands.Cog.listener()
    async def on_member_join(self,member):
        if(self.bot.ready):
            await self.bot.pg_con.execute("INSERT INTO " + "g_" + str(member.guild.id) + " (UserID) VALUES ($1) ON CONFLICT (UserID) DO NOTHING",member.id)

    @commands.command(name = 'start')
    @commands.has_guild_permissions(manage_channels=True) # figure out way to check either or
    async def start_command(self,ctx):
        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",ctx.message.guild.id)
        
        if settings["message_state"] == -2:            
            for r in ctx.message.guild.roles:
                if "cracklefest savior" in [r.name.lower() for r in ctx.message.guild.roles] and "cracklefest collector" in [r.name.lower() for r in ctx.message.guild.roles]:
                    pass#logger_print (ctx.message.guild.name + " - Got role")
                else:
                    extra_functions.logger_print (ctx.message.guild.name + " - no roles")
                    try:
                        role = await ctx.message.guild.create_role(name="Cracklefest Savior", colour=discord.Colour(0x16E7AF))
                        role2 = await ctx.message.guild.create_role(name="Cracklefest Collector", colour=discord.Colour(0x1ADDDD))
                    except(discord.errors.Forbidden):
                        embedVar = discord.Embed(title="Attention Server Staff!", description="⠀\nThe bot doesn't have role perms. Please make sure it has permissions to grant roles and manage chat and use e!start again.", color=0x3D310E)
                        embedVar.set_footer(text = "If you encounter any problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                        extra_functions.send_embed_ctx(self.bot,ctx,embedVar,30,"start forbidden role creation send")
                        return
                    except(discord.errors.HTTPException):
                        embedVar = discord.Embed(title="Attention Server Staff!", description="⠀\nThe servers has reach the maximum amount of roles which didn't allow the automatic role to be created. Make sure you have **two** role slots open then use e!start to activate the bot!", color=0x3D310E)
                        embedVar.set_footer(text = "If you encounter any problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                        extra_functions.send_embed_ctx(self.bot,ctx,embedVar,30,"start forbidden role creation send")
                        extra_functions.logger_print(str(ctx.message.guild.name) + " with ID: "+ str(ctx.message.guild.id) + " No Perms")
                        return
                        

            embedVar = discord.Embed(title="📖  The Cracklefest Scramble  📖", description="""In the land of Coneyford, Jethro the ruler of the land was excited to once again host a glorious event for his people, the Conoras. They call this event, Cracklefest. Every year around this time, everyone designs and crafts perfectly eggsquisite eggs to share. A holiday of genuine friendship and Renaissance.\n\nHowever, this year, the evil being known as the crimson wizard emerges from his realm and casts a mighty spell covering Coneyford! The storm caused the whole continent to morph and corrupt into terrible things! But most importantly, the storm scrambled all the eggs away from the conoras which left thousands of eggs placed all around Coneyford.\n\nWith eggs everywhere, it was uncertain that they were all able to be collected in time. Out of desperation, Jethro hired the people of """ + ctx.guild.name + """ to find all the eggs and save Cracklefest!\n\n⠀""", color=0xFF7878)
            embedVar.add_field(name="The Objective",value="**It is your job to collect as many eggs as you can before the end of the month.\n\nYou can collect eggs in six different lands that you unlock by upgrading your basket. The basket holds a special power to repel the storm, allowing people to explore that area. You can also collect collectible eggs, there are five in each land.\n\nEgg clusters can also be found spawned in the server. Usually, there are three to five eggs in it along with a slim chance to get a collectible egg.\n\nThe person with the most eggs wins a role called Cracklefest Savior! People who find all the collectible eggs win a rolled Cracklefest Collector!**")
            await self.bot.pg_con.execute("UPDATE guild_settings set message_state =  $1 WHERE Guild_ID = $2;",-1,ctx.message.guild.id) #Update Loved
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"Start command send!")

    @start_command.error
    async def start_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass
        elif isinstance(error, commands.MissingPermissions):
            embed = extra_functions.embedBuilder("⚠️  Whoops!  ⚠️","Looks like you don't have permission to manage channels!\nIn order to use this command, you need to be able to manage channels.","If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,60,"start error function send")
    
def setup(bot):
    bot.add_cog(Join_Events(bot))