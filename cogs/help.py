import discord
from database.updates import Database_Methods
from discord.ext import commands
from Extras.discord_functions import extra_functions


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'help')
    async def help_command(self, ctx, help_type):

        embed = None

        if(help_type.lower() == "settings" ):
            embed = extra_functions.embedBuilder("⚙️ Moderator Settings Command Line ⚙️","Use " + self.bot.prefix + "help [type] to find a specifically what you are looking for.\n**All commands below require the user to have manage channel perms to use unless specified specifically!**","For any questions/concerns please visit the official TheKWitt server!\nhttps://discord.gg/ZNpCNyNubU",color=0xFF00C4)
            embed.add_field(name = "" + self.bot.prefix + "start",value = "Activates the bot! **You must have channel perms to use this command!**")
            embed.add_field(name = "" + self.bot.prefix + "settings",value = "Shows a list of your server's bot settings!")
            embed.add_field(name = "" + self.bot.prefix + "defaultsettings",value = "Resets all the settings for the bot on this server to default!")
            embed.add_field(name = "" + self.bot.prefix + "setsetting",value = "Set any of the values for your server's bot settings!")
            embed.add_field(name = "" + self.bot.prefix + "whennextcluster",value = "Get info on when the next message will be spawned!")
            embed.add_field(name = "" + self.bot.prefix + "removechannel [Channel Tag]", value = "Remove the channel from the spawn list")
            embed.add_field(name = "" + self.bot.prefix + "addchannel [Channel Tag]",value = "Add the channel to the spawn list")
            embed.add_field(name = "" + self.bot.prefix + "activespawns",value = "Get a list of all the active spawn channels")
            embed.add_field(name = "" + self.bot.prefix + "resetserver",value = "Resets the server's database. **REQUIRES USER TO HAVE ADMIN PERMS** ***CANNOT BE UNDONE***\n")
            embed.add_field(name = "⠀",value = "⠀",inline = False)

        elif(help_type.lower() == "tools" ):
            embed = extra_functions.embedBuilder("⚙️ Moderator Tool Command Line ⚙️","Use " + self.bot.prefix + "help [type] to find a specifically what you are looking for.\n**All commands below require the user to have manage channel perms to use unless specified specifically!**","For any questions/concerns please visit the official TheKWitt server!\nhttps://discord.gg/ZNpCNyNubU",color=0xFF00C4)
            embed.add_field(name = "" + self.bot.prefix + "setlevel [User Mention] [Number 1-100]",value = "Set the level of the User")
            embed.add_field(name = "" + self.bot.prefix + "setclusters [User Mention] [Number 1-100]",value = "Set the clusters of the User")
            embed.add_field(name = "" + self.bot.prefix + "setcoins [User Mention] [Number 1-10000]",value = "Set the coins of the User")
            #embed.add_field(name = "" + self.bot.prefix + "addegg [User Mention] [Egg ID]",value = "Adds an egg to the User")
            #embed.add_field(name = "" + self.bot.prefix + "removeegg [User Mention] [Egg ID]",value = "Removes an egg to the User")
            embed.add_field(name = "" + self.bot.prefix + "fillbasket [User Mention]",value = "Fills the basket of the user to completely full!")
            embed.add_field(name = "" + self.bot.prefix + "fillcollection [User Mention]",value = "Sets the collection of the user to completed!")

        elif(help_type.lower() == "eggs" or help_type.lower() == "egg"):
            embed = extra_functions.embedBuilder("⚙️ Egg Command Line ⚙️","All the commands have guides on how to use them! Just do that command with or without the requirements to get details!","For any questions/concerns please visit the official TheKWitt server!\nhttps://discord.gg/ZNpCNyNubU",color=0xFF00C4)
            embed.add_field(name = "" + self.bot.prefix + "explore [Area]",value = "The Coney Stronghold - [coney] (Level 1)\nThe Hulking Fields - [hulking] (Level 3)\nThe Woodland Valley - [woodlands] (Level 6)\nThe Oracle River - [oracle] (Level 10)\nThe Ethereal Gardens - [ethereal] (Level 15)\nThe Crimson Grove - [crimson] (Level 21)\nThe Arcane Void - [void] (Level 30)",inline = False)
            embed.add_field(name = "" + self.bot.prefix + "trade [User Mention] [Your Egg ID] [Their Egg ID]", value = "Trade an egg for another egg from another user!",inline = False)
            embed.add_field(name = "" + self.bot.prefix + "uncluster", value = "Break up an egg cluster to get more eggs! Check " + self.bot.prefix + "eggard to see if you have any!")
            embed.add_field(name = "" + self.bot.prefix + "lottery [Gold Coin Amount]", value = "Wager 1 to 100 gold coins for a chance to triple it!")
            embed.add_field(name = "" + self.bot.prefix + "mailbox", value = "Check your mailbox for an extra set of clusters and gold coins sent by the locals in Coneyford!")
            embed.add_field(name = "" + self.bot.prefix + "sell", value = "Sell 10 of your eggs for a gold coin! Gold coins can be used to upgrade your basket.")
            embed.add_field(name = "" + self.bot.prefix + "megasell", value = "Sell as many of your eggs as you can for gold coins! Gold coins can be used to upgrade your basket.")
            embed.add_field(name = "" + self.bot.prefix + "upgrade", value = "Upgrade your basket to hold more eggs and have the ability to explore new areas and find more eggs!")
            embed.add_field(name = "" + self.bot.prefix + "incase [Egg ID]", value = "Put an egg in a display case for you to show off to your friends! Eggs in the display case won't get sold!")
            embed.add_field(name = "" + self.bot.prefix + "outcase [Egg ID]", value = "Take an egg from your display case back into your basket!")
            embed.add_field(name = "" + self.bot.prefix + "toss [User Mention]", value = "Throw an egg at someone for a chance to make them drop their own eggs!")
            embed.add_field(name = "" + self.bot.prefix + "donate [Area] [Egg Amount]", value = "Donate eggs to help stop the corruption in Coneyford! Purified Areas will give you double the eggs when exploring.")
        elif(help_type.lower() == "stats"):
            embed = extra_functions.embedBuilder("⚙️ Stats Command Line ⚙️","Use " + self.bot.prefix + "help [type] to find a specifically what you are looking for.","For any questions/concerns please visit the official TheKWitt server!\nhttps://discord.gg/ZNpCNyNubU",color=0xFF00C4)
            embed.add_field(name = "" + self.bot.prefix + "eggard\n" + self.bot.prefix + "card [User Mention]",value = "Brings up the Cracklefest ID Card and Stats!")
            embed.add_field(name = "" + self.bot.prefix + "basket",value = "Displays all the eggs in your basket!")
            embed.add_field(name = "" + self.bot.prefix + "collection",value = "Displays all the eggs in your collection!")
            embed.add_field(name = "" + self.bot.prefix + "case",value = "Displays all the eggs in your case!")
            embed.add_field(name = "" + self.bot.prefix + "leaderboard",value = "Displays a leaderboard of all the members' baskets on the server!")
            embed.add_field(name = "" + self.bot.prefix + "collectionboard",value = "Displays a leaderboard of all the members' collections on the server!")
            embed.add_field(name = "" + self.bot.prefix + "historyboard",value = "Displays a leaderboard of all the members' # of eggs collected on the server!")
            embed.add_field(name = "" + self.bot.prefix + "serverstats",value = "Shows all the stats for the server!")
            embed.add_field(name = "" + self.bot.prefix + "donationgoaltracker",value = "Shows the donation goals for all the areas!")
            embed.add_field(name = "⠀",value = "⠀",inline = False)

        elif(help_type.lower() == "info"):
            embed = extra_functions.embedBuilder("⚙️ Info Command Line ⚙️","Use " + self.bot.prefix + "help [type] to find a specifically what you are looking for.","For any questions/concerns please visit the official TheKWitt server!\nhttps://discord.gg/ZNpCNyNubU",color=0xFF00C4)
            embed.add_field(name = "" + self.bot.prefix + "help",value = "Gives you all the commands!")
            embed.add_field(name = "" + self.bot.prefix + "backstory",value = "Didn't get to see the welcome message? Now you can!")
            embed.add_field(name = "" + self.bot.prefix + "invite",value = "Get the invite link for the bot!")
            embed.add_field(name = "" + self.bot.prefix + "credits",value = "Get info about the bot and it's creators!")
            embed.add_field(name = "" + self.bot.prefix + "support",value = "Shows a link to the support server!")
            embed.add_field(name = "" + self.bot.prefix + "manual",value = "Tells you everything about the bot!")
            embed.add_field(name = "" + self.bot.prefix + "atlas [Area]",value = "Shows lore for the area!")
            embed.add_field(name = "" + self.bot.prefix + "eggcyclopedia [Egg ID]",value = "Shows lore for that egg!")
            embed.add_field(name = "⠀",value = "⠀",inline = False)
        try:
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"help send message")
        except discord.errors.Forbidden as e:
            extra_functions.logger_print(e)
            return
    
    @help_command.error
    async def help_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            embed = extra_functions.embedBuilder("⚙️ Help Command Line ⚙️","Use " + self.bot.prefix + "help [type] to find a specifically what you are looking for.\n\nIf you want help on getting details, try out **e!manual** !","For any questions/concerns please visit the official TheKWitt server!\nhttps://discord.gg/ZNpCNyNubU",color=0xFF00C4)
            embed.add_field(name = "Moderator Only Setting Commands",value = "" + self.bot.prefix + "help settings")
            embed.add_field(name = "Moderator Only Tool Commands",value = "" + self.bot.prefix + "help tools",inline = False)
            embed.add_field(name = "Egg Commands",value = "" + self.bot.prefix + "help eggs")
            embed.add_field(name = "Stats Commands",value = "" + self.bot.prefix + "help stats")
            embed.add_field(name = "Info Commands",value = "" + self.bot.prefix + "help info")
            embed.add_field(name = "⠀",value = "⠀",inline = False)

            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",ctx.message.guild.id)
            if settings["message_state"] == -2:
                embed.add_field(name = "Bot Not Activated!",value = "Looks like the bot is not activated! Use the " + self.bot.prefix + "start command to get started! **You must have channel perms to use this command!**")
                
            try:
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"settings send message")
            except discord.errors.Forbidden as e:
                extra_functions.logger_print(e)
                return

def setup(bot):
    bot.add_cog(Help(bot))