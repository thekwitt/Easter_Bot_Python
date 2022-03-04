import discord,json
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'atlas')
    async def atlas_command(self, ctx, area):

        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)        
        # Check for proper input
        areas = ['coney','hulking','woodlands','oracle','ethereal','crimson','void']

        if not area in areas:
            embedVar = discord.Embed(title="⚠️  That wasn't an area in the atlas!  ⚠️", description="Do e!atlas to see what areas there are to read about! Also make sure your level is high enough!", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
            return
        
        index = areas.index(area.lower())        

        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
        purr = settings['purification_count']
        default = settings['default_server_settings']
        cor = "(Corrupted) "

        if area.lower() == "void":
            cor = ""
        elif(int(purr[index]) >= int(default[2])):
            cor = ""


        if(user['basket_level'] < self.bot.levelrequirements[index]):
            embedVar = discord.Embed(title="⚠️  Your Basket Level is too low!  ⚠️", description="You are only level " + str(user['basket_level']+1) + " while you need it to be level " + str(self.bot.levelrequirements[index]+1) + " to see this area on the atlas! To upgrade your basket, use " + self.bot.prefix + "upgrade if you have enough gold coins.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
        else:
            if area.lower() in areas:
                with open('JSON/Atlas.json') as f:
                    j = json.load(f)
                    egg_area = ["\n\nThis area is said to contain solid colored, triangle, castle and medieval eggs. If you are lucky, you can find Jethro's personal collection of eggs!","\n\nThis area is said to contain food, melted and ice cream eggs. If you are lucky, you can find authentic chocolate eggs!","\n\nThis area is said to contain dotted, swirl and diamond eggs. If you are lucky, you can find well-crafted wooden eggs!","\n\nThis area is said to contain Wavey, ZigZag, Water and Mix Designed eggs. If you are lucky, you can find the Elemental Dragon Eggs!","\n\nThis area is said to contain mysterious animal and flower eggs. If you are lucky, you can find Soul Essence Eggs!","\n\nThis area is said to contain hexigon, glass, clouds and stars eggs. If you are lucky, you can find Arcane Zombie Eggs!","\n\nThis area is said to contain void, spell and arcane fury eggs. * It does not have any rare collectible eggs!*"]
                    embedVar = discord.Embed(title="🗺️  " + cor + j[area]['name'] + "  🗺️", description="⠀\n" + j[area]['description'] + "**" + egg_area[index] + "**\n⠀", color=0xFFCC00)
                    embedVar.set_footer(text = "See the whole map with e!atlas!")
                    await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,240,"set settings function message low send")
            else:
                embedVar = discord.Embed(title="⚠️  That wasn't an area in the atlas!  ⚠️", description="Do e!atlas to see what areas there are to read about! Also make sure your level is high enough!", color=0xFFCC00)
                embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
    @atlas_command.error
    async def atlas_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embedVar = discord.Embed(title="🗺️  Coneyford  🗺️", description="The Map of Coneyford!\n\n__**Map Guide**__\ne!atlas coney - The Coney Stronghold\ne!atlas hulking - The Hulking Fields\ne!atlas woodlands - The Woodland Valley\ne!atlas oracle - The Oracle Rivers\ne!atlas ethereal - The Ethereal Garden\ne!atlas crimson - The Crimson Grove\ne!atlas void - The Arcane Void", color=0xFFCC00)
            embedVar.set_image(url = "https://media.discordapp.net/attachments/782835367085998080/832817155111780352/Coneyford_7.jpg")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,120,"set settings function message low send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","That wasn't a discord user!","Remember to do **" + self.bot.prefix + "eggard** [User Tag] or simply **" + self.bot.prefix + "eggard** to see your Egg Card",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"complement function member not found send")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Woah There!  ⚠️","You recently used this command!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after) % 60) + " seconds!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"purify function cooldown send")           
            return

    @commands.command(name = 'eggcyclopedia',aliases = ["eggbook"])
    async def eggcyclopedia_command(self, ctx, egg_id):

        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)        
        # Check for proper input
        with open('JSON/Eggs.json') as f:
            egg_dic = json.load(f)

        try:
            egg = [item for item in (egg_dic['regular_eggs'] + egg_dic['collectible_eggs']) if item['id'] == egg_id][0]
            atlasegg = ""
            if egg['type'].lower() in ["solid","triangle","coney",'castle','unique']:
                atlasegg = "**This egg can be found in the The Coney Stronghold!**"
            elif egg['type'].lower() in ['food','melted','hulking','cream']:
                atlasegg = "**This egg can be found in the The Hulking Fields!**"
            elif egg['type'].lower() in ['dotted','swirl','woodlands','diamonds']:
                atlasegg = "**This egg can be found in the The Woodland Valley!**"
            elif egg['type'].lower() in ['waves','zigzag','oracle','water','mix 1']:
                atlasegg = "**This egg can be found in the The Oracle Rivers!**"
            elif egg['type'].lower() in ['cow','zebra','tiger','reptile','giraffe','ethereal','flowers']:
                atlasegg = "**This egg can be found in the The Ethereal Rivers!**"
            elif egg['type'].lower() in ['glass','hexigons','crimson','stars','clouds']:
                atlasegg = "**This egg can be found in the The Crimson Grove!**"
            elif egg['type'].lower() in ['void','spell','fury']:
                atlasegg = "**This egg can be found in the The Crimson Grove!**"

            embedVar = discord.Embed(title="🥚    " + egg['name'] + "    🥚", description="⠀" + "\n\n" + atlasegg + "\n⠀", color=0xFFCC00) #egg['description']
            embedVar.set_image(url = self.bot.get_emoji(int(egg['emoji'][8:26])).url)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,240,"set settings function message low send")
        except:
            embedVar = discord.Embed(title="⚠️  That wasn't an egg in the eggcyclopedia!  ⚠️", description="Make sure you have the right egg id!", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,20,"set settings function message low send")
    @eggcyclopedia_command.error
    async def eggcyclopedia_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embedVar = discord.Embed(title="🗺️  Eggcyclopedia  🗺️", description="Do e!eggcyclopedia [Egg ID] to get everything about the egg!", color=0xFFCC00)
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,120,"set settings function message low send")
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","That wasn't a discord user!","Remember to do **" + self.bot.prefix + "eggard** [User Tag] or simply **" + self.bot.prefix + "eggard** to see your Egg Card",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"complement function member not found send")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Woah There!  ⚠️","You recently used this command!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after) % 60) + " seconds!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"purify function cooldown send")           
            return

    @commands.command(name = 'epilogue',aliases = ["ending"])
    async def epilogue_command(self, ctx):
        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
        counts = row['purification_count']
        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
        default = settings['default_server_settings']

        for x in range(0,5):
            if not (counts[x] >= int(default[2])):
                return

        embedVar = discord.Embed(title="📕  The Epilogue  📕", description="The People of Coneyford, the conoras, express their gratitude for the heroes of **" + ctx.guild.name + "**! Finally the evil and darkness has been sealed away and life can begin anew!\n\nJethro bows before everyone of the community. He shakes his hand with " + ctx.guild.owner.name + " and thanks them for bringing these people together to save their land. A celebration was held to captivate this special moment for not only Cracklefest but all of Coneyford!\n\n(But the Crimson Wizard has not given up just yet despite the conoras celebrating. For they not know of what will happen next...)\n\n**This is not the end of the bot but a new beginning! You can still explore all the areas and collect eggs! The title will still be rewarded to who has the most eggs and who has collected all 30 rare eggs!**\n\n⠀", color=0xFFCC00)
        embedVar.add_field(name = "__A Special Note From The Developer!__", value = "Holy smokes! You all contributed to saving Coneyford! I'm sure the conoras are happy but not as happy as I am for all of you using my bot! I have put ALOT of love into this thing and I appreciate everyone here for playing! If you enjoyed this bot, use e!support to see the next thing I am cooking and be sure to let your mods/admins/owner know that my software/bots will only get better!\n\nMake sure to spread the love and keep collecting eggs! I'll see you again hopefully soon!")
        embedVar.set_footer(text = "The story will be continued next year!")
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,999,"epilogue function message send")

    @epilogue_command.error
    async def epilogue_command_command_error(self,ctx,error):
        if isinstance(error,commands.CommandInvokeError):
            pass                

def setup(bot):
    bot.add_cog(Lore(bot))