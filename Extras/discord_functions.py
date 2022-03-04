import discord, random, asyncio, asyncpg, os, os.path
from datetime import datetime

class extra_functions:

    @staticmethod
    def logger_print(string):
        string = str(string)
        with open('discord_console_logger.txt', encoding='utf-8', mode='a') as f:
            try:
                f.write(str(datetime.now()) + " | " + string + "\n")
            except(TypeError, ValueError,UnicodeDecodeError,OSError,EOFError):
                pass
        print(str(datetime.now())," | ",string)
        return

    @staticmethod
    def logger_noprint(string):
        string = str(string)
        with open('discord_console_logger.txt', encoding='utf-8', mode='a') as f:
            try:
                f.write(str(datetime.now()) + " | " + string + "\n")
            except(TypeError, ValueError,UnicodeDecodeError,OSError,EOFError):
                pass
        return

    @staticmethod
    def tag_to_user(bot,tag):
        return bot.get_user(int(tag.replace('<','').replace('>','').replace('!','').replace('@','')))
        
    @staticmethod
    def user_to_tag(bot,user_id):
        return "<@!" + str(user_id) + ">"

    @staticmethod
    def tag_to_user(bot,tag):
        return bot.get_user(int(tag.replace('<','').replace('>','').replace('!','').replace('@','')))
        
    @staticmethod
    def user_to_tag(bot,user_id):
        return "<@!" + str(user_id) + ">"

    @staticmethod
    def embedBuilder(title,description,footer,color):
        embed = discord.Embed(title = title,description = "⠀\n" + description + "\n⠀",color = color)
        embed.set_footer(text=footer)
        return embed


    @staticmethod
    def embedBuilder_url(title,description,footer,color,url):
        embed = discord.Embed(title = title,description = "⠀\n" + description + "\n⠀",color = color, url=url)
        embed.set_footer(text=footer)
        return embed

    @staticmethod
    def embedBuilder_thumbnail(title,description,footer,color,thumbnail):
        embed = discord.Embed(title = title,description = "⠀\n" + description + "\n⠀",color = color, thumbnail = thumbnail)
        embed.set_footer(text=footer)
        return embed

    @staticmethod
    def embedBuilder_both(title,description,footer,color,url,thumbnail):
        embed = discord.Embed(title = title,description = "⠀\n" + description + "\n⠀",color = color, url = url,thumbnail = thumbnail)
        embed.set_footer(text=footer)
        return embed

    @staticmethod
    async def send_regular_message(bot,content,message,seconds,error_path):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",message.guild.id)
        settings = row["default_message_settings"]
        for x in range(0,3):
            try:
                if(settings[3] == "True"):
                    return await message.channel.send(content = content,delete_after=seconds)
                else:
                    return await message.channel.send(content = content)
            except discord.errors.Forbidden:
                extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")
            except discord.errors.HTTPException as e:
                extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")
    
    @staticmethod
    async def send_regular_channel(bot,content,channel,seconds,error_path):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",channel.guild.id)
        settings = row["default_message_settings"]
        for x in range(0,3):
            try:
                if(settings[3] == "True"):
                    return await channel.send(content = content,delete_after=seconds)
                else:
                    return await channel.send(content = content)
            except discord.errors.Forbidden:
                extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + channel.guild.name + " | " + str(channel.guild.id) + ".")
            except discord.errors.HTTPException as e:
                extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + channel.guild.name + " | " + str(channel.guild.id) + ".")
            
    @staticmethod
    async def send_regular_ctx(bot,content,ctx,seconds,error_path):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.message.guild.id)
        settings = row["default_message_settings"]
        for x in range(0,3):
            try:
                if(settings[3] == "True"):
                    return await ctx.channel.send(content = content,delete_after=seconds)
                else:
                    return await ctx.channel.send(content = content)
            except discord.errors.Forbidden:
                extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + ctx.guild.name + " | " + str(ctx.guild.id) + ".")
            except discord.errors.HTTPException as e:
                extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + ctx.guild.name + " | " + str(ctx.guild.id) + ".")


    @staticmethod
    async def send_embed_message(bot,message,embed,seconds,error_path):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",message.guild.id)
        settings = row["default_message_settings"]
        for x in range(0,3):
            try:
                if(settings[3] == "True"):
                    return await message.channel.send(embed=embed,delete_after=seconds)
                else:
                    return await message.channel.send(embed=embed)
            except discord.errors.Forbidden:
                extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")
            except discord.errors.HTTPException as e:
                extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")

    @staticmethod
    async def send_embed_ctx(bot,ctx,embed,seconds,error_path):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
        settings = row["default_message_settings"]
        for x in range(0,3):
            try:
                if(settings[3] == "True"):
                    return await ctx.send(embed=embed,delete_after=seconds)
                else:
                    return await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + ctx.message.guild.name + " | " + str(ctx.message.guild.id) + ".")
            except discord.errors.HTTPException as e:
                extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + ctx.message.guild.name + " | " + str(ctx.message.guild.id) + ".")

    @staticmethod
    def time_to_string(timestamp):
        string = ""
        if(timestamp > 3600):
            if(timestamp/3600 == 1):
                string += "1 Hour, "
            else:
                string += str(int(timestamp/3600)) + " Hours, "

            if(timestamp/60) % 60 == 1:
                string += "1 Minute, "
            else:
                string += str(int((timestamp/60) % 60))  + " Minutes, "

            if timestamp % 60 == 1:
                string += "1 Second, "
            else:
                string += str(timestamp % 60) + " Seconds "
        
        elif(timestamp > 60):
            
            if(timestamp/60) % 60 == 1:
                string += "1 Minute, "
            else:
                string += str(int((timestamp/60) % 60))  + " Minutes, "

            if timestamp % 60 == 1:
                string += "1 Second, "
            else:
                string += str(timestamp % 60) + " Seconds "

        else:
            if timestamp % 60 == 1:
                string += "1 Second, "
            else:
                string += str(timestamp % 60) + " Seconds "
        
        return string

    @staticmethod
    async def send_embed_channel(bot,channel,embed,seconds,error_path):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",channel.guild.id)
        settings = row["default_message_settings"]
        try:
            if(settings[3] == "True"):
                return await channel.send(embed=embed,delete_after=seconds)
            else:
                return await channel.send(embed=embed)
        except discord.errors.Forbidden:
            extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + channel.guild.name + " | " + str(channel.guild.id) + ".")
        except discord.errors.HTTPException as e:
            extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + channel.guild.name + " | " + str(channel.guild.id) + ".")

    @staticmethod
    async def edit_embed_message(bot,message,embed,error_path):
        for x in range(0,3):
            try:
                return await message.edit(embed=embed)
            except discord.errors.Forbidden:
                extra_functions.logger_print("Forbidden Send occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")
            except discord.errors.HTTPException as e:
                extra_functions.logger_print(str(e) + " occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")
            except discord.errors.NotFound:
                extra_functions.logger_print("Not Found Send occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")
            except AttributeError:
                extra_functions.logger_print("Attribute Error occured at " + error_path + " in " + message.guild.name + " | " + str(message.guild.id) + ".")


    @staticmethod
    def str_to_bool(s):
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
        else:
            pass#raise ValueError 

    @staticmethod
    def check_for_empty_sql_array(value):
        if(value == None):
            return []
        else:
            return value

    @staticmethod
    async def reset_server_message(bot,guild):
        row = await bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",guild.id)

        active_settings = row["active_message_settings"]
        default_settings = row["default_message_settings"]
        active_settings[0] = int(default_settings[0]) + datetime.now().timestamp()
        active_settings[1] = int(default_settings[1])
        if len(row['possible_channel_ids']) > 0:
            await bot.pg_con.execute("UPDATE guild_settings set active_message_settings = $1,message_state = $2 WHERE Guild_ID = $3;",active_settings,0,guild.id) #Update Loved
        else:
            await bot.pg_con.execute("UPDATE guild_settings set active_message_settings = $1,message_state = $2 WHERE Guild_ID = $3;",active_settings,-1,guild.id) #Update Loved
        await bot.pg_con.execute("DELETE from egg_messages WHERE Guild_ID = $1;",guild.id)
        extra_functions.logger_noprint(guild.name + " : " + str(guild.id) + " - Reset Server Spawn")

    @staticmethod
    async def change_roles(bot,channel,guild):

        temp_role = None

        for r in guild.roles:
            if 'cracklefest savior' in r.name.lower():
                temp_role = r
                #print(temp_role.name)
                #extra_functions.logger_noprint(guild.name + " - Found Role for Transfer")
                break

        if temp_role != None:

            row = await bot.pg_con.fetch("SELECT * FROM " + "g_" + str(guild.id) + " ORDER BY array_length(basket_eggs,1) DESC")

            for x in range(len(row)-1,-1,-1):
                if row[x]['basket_eggs'] == [] or row[x]['basket_eggs'] == None or guild.get_member(row[x]["userid"]) == None:
                    row.pop(x)  

            temp_count = 0

            for m in range(1,len(row)):
                if (len(row[0]["basket_eggs"]) != len(row[m]["basket_eggs"])):
                    break
                temp_count += 1

            for m in range(0,temp_count+1):
                member = None
                try:
                    member = guild.get_member(int(row[m]["userid"]))
                except(IndexError,TypeError):
                    pass
                if(member != None):
                    if not "cracklefest savior" in [r.name.lower() for r in guild.get_member(row[m]["userid"]).roles]:
                        try:
                            if int(len(row[m]["basket_eggs"])) != 0:
                                await guild.get_member(int(row[m]["userid"])).add_roles(temp_role)
                        except(discord.errors.Forbidden):
                            embedVar = discord.Embed(title="Attention Server Staff!", description="Whoops! Looks like the Cracklefest Savior role is higher than the bot role!\nPlease assign a bot role or the included bot role to have manage channel, messages and role perms to this bot that is higher than Cracklefest Savior.", color=0xFFCC00)
                            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                            await extra_functions.send_embed_channel(bot,channel,embedVar,30,"Changing role too high send")
            for m in range(temp_count+1,len(row)):
                member = None
                try:
                    member = guild.get_member(int(row[m]["userid"]))
                except(TypeError):
                    #print(server.users[m].name + " - Error")
                    extra_functions.logger_print(str(guild.name) + " with ID: "+ str(guild.id) + "Not Member") 
                if(member != None):
                    for r in member.roles:
                        if "cracklefest savior" in r.name.lower():
                            try:
                                await guild.get_member(int(row[m]["userid"])).remove_roles(temp_role)
                            except (discord.errors.Forbidden):
                                extra_functions.logger_print(str(guild.name) + " with ID: "+ str(guild.id) + " Unwrap No Roles") 
        else:
            embedVar = discord.Embed(title="Attention Server Staff!", description="Looks like you don't have the included 'Cracklefest Savior'. Please make sure you have a role named Cracklefest Savior to have roles granted. The present has been awarded to the user.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_channel(bot,channel,embedVar,30,"Changing roles no role send")

    @staticmethod
    async def add_secondary_role(bot,user,channel,guild,eggs):

        temp_role = None

        for r in guild.roles:
            if 'cracklefest collector' in r.name.lower():
                temp_role = r
                #print(temp_role.name)
                #extra_functions.logger_noprint(guild.name + " - Found Role for Transfer")
                break

        if temp_role != None:

            row = await bot.pg_con.fetch("SELECT * FROM " + "g_" + str(guild.id) + " WHERE userid = $1",user.id)
            if(user != None):
                if not "cracklefest collector" in [r.name.lower() for r in guild.get_member(user.id).roles]:
                    try:
                        if int(len(eggs)) >= 30:
                            await guild.get_member(user.id).add_roles(temp_role)
                    except(discord.errors.Forbidden):
                        embedVar = discord.Embed(title="Attention Server Staff!", description="Whoops! Looks like the Cracklefest Savior role is higher than the bot role!\nPlease assign a bot role or the included bot role to have manage channel, messages and role perms to this bot that is higher than Cracklefest Savior.", color=0xFFCC00)
                        embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
                        await extra_functions.send_embed_channel(bot,channel,embedVar,30,"Changing role too high send")
        else:
            embedVar = discord.Embed(title="Attention Server Staff!", description="Looks like you don't have the included 'Cracklefest Savior'. Please make sure you have a role named Cracklefest Savior to have roles granted. The present has been awarded to the user.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            await extra_functions.send_embed_channel(bot,channel,embedVar,30,"Changing roles no role send")



    @staticmethod
    async def check_for_main_channel(guild):
        for c in guild.channels:
            if(isinstance(c,discord.TextChannel)):
                if "general" in c.name or "banter" in c.name or "main" in c.name:
                    return c
    
    @staticmethod
    def bracket_array(type):
        if type == 1:
            return [["<:TL01:825100052976107562>","<:TopLine01:825100053181497394>","<:TR01:825100052782645344>"],["<:BL01:825100053047017563>","<:BottomLine01:825100053068775425>","<:BR01:825100052837040130>"],["<:Empty:825101942644408350>","",""]]
        elif type == 2:
            return [["<:RTL01:825100053071790171>","<:RichTopLine01:825100053143093359>","<:RTR01:825100052535181313>"],["<:RBL01:825100052733100053>","<:RichBottomLine01:825100448233947256>","<:RBR01:825100052824850453>"],["<:Empty:825101942644408350>","",""]]


