import discord, random, asyncio, time,json
from Custom_Fancy import new_fancy
from io import BytesIO
from PIL import Image, ImageFilter, ImageDraw, ImageFont,ImageOps
from datetime import datetime
from discord.ext import commands
from database.updates import Database_Methods
from Extras.discord_functions import extra_functions

class Info_Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'eggard', aliases = ["card"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def eggard_command(self,ctx,user: discord.User):
        try:
            if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
                await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)
            elif user.bot:
                embed = discord.Embed(title = "Bots don't have Egg Cards!",description = "Bots are too busy in the backend helping gather eggs for the Conoras!",color = 0xB6004A)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,90,"eggard bot card send error")
                return

            row = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id)
            lb_row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " ORDER BY array_length(basket_eggs,1) DESC")
            max = str(50 + (25 * row['basket_level']))

            
            for x in range(len(lb_row)-1,-1,-1):
                if lb_row[x]['basket_eggs'] == [] or lb_row[x]['basket_eggs'] == None:
                    lb_row.pop(x)  

            for index, item in enumerate(lb_row):
                if item['userid'] == user.id:
                    break
                
            asset = user.avatar_url_as(size = 128)
            data = BytesIO(await asset.read())
            pfp_base = Image.open(data).resize((134,134))

            size = (134, 134)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + size, fill=255)

            pfp = ImageOps.fit(pfp_base, mask.size, centering=(0.5, 0.5))
            pfp.putalpha(mask)
            pfp = pfp.convert("RGBA")

            base = Image.open("Card/Eggard.png").convert("RGBA") #template
            text = Image.new("RGBA", base.size, (255,255,255,0)) #blank image for text

            base.paste(pfp_base.convert("RGBA"), (30,30), pfp.convert("RGBA"))

            t_font = ImageFont.truetype("Card/Title.ttf",60) # Title Font
            r_font = ImageFont.truetype("Card/Rank.ttf",36) # Rank Font
            p_font = ImageFont.truetype("Card/Points.ttf",48) # Point Font
            c_font = ImageFont.truetype("Card/Count.ttf",60) # Point Font
            l_font = ImageFont.truetype("Card/LB.ttf",60) # Rank Font
            d_text = ImageDraw.Draw(text) # Draw Text Image
            
            d_text.text((190,30),user.display_name[:18],font=t_font,fill=(197,231,228,255),)
            d_text.text((190,110),"Level " + str(row["basket_level"]+1) + " | " + self.rank(row["eggs_collected"]),font=r_font,fill=(116,204,209,255))  
            d_text.text((35,289),"Basket - "+self.point_rpg_string(len(row["basket_eggs"])) + "/" + max,font=p_font,fill=(82,181,134,255))
            d_text.text((35,359),"Collectibles - "+self.point_rpg_string(len(row["collection_eggs"])) + "/30",font=p_font,fill=(128,196,184,255))
            d_text.text((35,429),"Collected "+self.point_rpg_string(row["eggs_collected"]) + " Eggs",font=p_font,fill=(83,173,188,255))
            if row["gold_coins"] < 100:
                d_text.text((1061,71),str(row["gold_coins"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
            elif row["gold_coins"] >= 1000:
                l_font = ImageFont.truetype("Card/LB.ttf",29) # Rank Font
                d_text.text((1058,85),str(self.card_point_rpg_string(row["gold_coins"])),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
            else:
                l_font = ImageFont.truetype("Card/LB.ttf",45) # Rank Font
                d_text.text((1059,78),str(row["gold_coins"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
            if row["clusters"] < 100:
                l_font = ImageFont.truetype("Card/LB.ttf",60) # Rank Font
                d_text.text((1058,261),str(row["clusters"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
            elif row["clusters"] >= 1000:
                l_font = ImageFont.truetype("Card/LB.ttf",32) # Rank Font
                d_text.text((1050,280),str(self.card_point_rpg_string(row["clusters"])),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
            else:
                l_font = ImageFont.truetype("Card/LB.ttf",50) # Rank Font
                d_text.text((1055,268),str(row["clusters"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
            try:
                d_text.text((817,430),"Rank: " + str(index+1).zfill(4),font=c_font,fill=(96,197,232,255))
            except:
                d_text.text((917,430),str("No Rank").zfill(4),font=c_font,fill=(96,197,232,255))


            out = Image.alpha_composite(base,text)
            

            with BytesIO() as image_binary:
                out.save(image_binary,'PNG')
                image_binary.seek(0)
                try:
                    row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                    settings = row["default_message_settings"]
                    if(settings[3] == "True"):
                        await ctx.send(file=discord.File(fp=image_binary, filename='image.png'),delete_after = 90)
                    else:
                        await ctx.send(file=discord.File(fp=image_binary, filename='image.png'))
                except discord.errors.Forbidden:
                    extra_functions.logger_print("Forbidden Send occured at eggard self in " + ctx.message.guild.name + " | " + str(ctx.message.guild.id) + ".")
                except discord.errors.HTTPException:
                    extra_functions.logger_print("HTTP Error Send occured at eggard self in " + ctx.message.guild.name + " | " + str(ctx.message.guild.id) + ".")
        except Exception as e:
            pass

    @eggard_command.error
    async def eggard_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            try:
                user = ctx.message.author
                if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id) == None and not user.bot:
                    await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,user.id)
                
                row = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",user.id)
                lb_row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " ORDER BY array_length(basket_eggs,1) DESC")

                max = str(50 + (25 * row['basket_level']))

                for x in range(len(lb_row)-1,-1,-1):
                    if lb_row[x]['basket_eggs'] == [] or lb_row[x]['basket_eggs'] == None:
                        lb_row.pop(x)


                for index, item in enumerate(lb_row):
                    if item['userid'] == user.id:
                        break

                asset = user.avatar_url_as(size = 128)
                data = BytesIO(await asset.read())
                pfp_base = Image.open(data).resize((134,134))

                size = (134, 134)
                mask = Image.new('L', size, 0)
                draw = ImageDraw.Draw(mask) 
                draw.ellipse((0, 0) + size, fill=255)

                pfp = ImageOps.fit(pfp_base, mask.size, centering=(0.5, 0.5))
                pfp.putalpha(mask)
                pfp = pfp.convert("RGBA")

                base = Image.open("Card/Eggard.png").convert("RGBA") #template
                text = Image.new("RGBA", base.size, (255,255,255,0)) #blank image for text

                base.paste(pfp_base.convert("RGBA"), (30,30), pfp.convert("RGBA"))

                t_font = ImageFont.truetype("Card/Title.ttf",60) # Title Font
                r_font = ImageFont.truetype("Card/Rank.ttf",36) # Rank Font
                p_font = ImageFont.truetype("Card/Points.ttf",48) # Point Font
                c_font = ImageFont.truetype("Card/Count.ttf",60) # Point Font
                l_font = ImageFont.truetype("Card/LB.ttf",60) # Rank Font
                d_text = ImageDraw.Draw(text) # Draw Text Image
                
                d_text.text((190,30),user.display_name[:18],font=t_font,fill=(197,231,228,255),)
                d_text.text((190,110),"Level " + str(row["basket_level"]+1) + " | " + self.rank(row["eggs_collected"]),font=r_font,fill=(116,204,209,255))  
                d_text.text((35,289),"Basket - "+self.point_rpg_string(len(row["basket_eggs"])) + "/" + max,font=p_font,fill=(82,181,134,255))
                d_text.text((35,359),"Collectibles - "+self.point_rpg_string(len(row["collection_eggs"])) + "/30",font=p_font,fill=(128,196,184,255))
                d_text.text((35,429),"Collected "+self.point_rpg_string(row["eggs_collected"]) + " Eggs",font=p_font,fill=(83,173,188,255))
                if row["gold_coins"] < 100:
                    d_text.text((1061,71),str(row["gold_coins"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
                elif row["gold_coins"] >= 1000:
                    l_font = ImageFont.truetype("Card/LB.ttf",29) # Rank Font
                    d_text.text((1058,85),str(self.card_point_rpg_string(row["gold_coins"])),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
                else:
                    l_font = ImageFont.truetype("Card/LB.ttf",45) # Rank Font
                    d_text.text((1059,78),str(row["gold_coins"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
                if row["clusters"] < 100:
                    l_font = ImageFont.truetype("Card/LB.ttf",60) # Rank Font
                    d_text.text((1058,261),str(row["clusters"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
                elif row["clusters"] >= 1000:
                    l_font = ImageFont.truetype("Card/LB.ttf",32) # Rank Font
                    d_text.text((1050,280),str(self.card_point_rpg_string(row["clusters"])),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
                else:
                    l_font = ImageFont.truetype("Card/LB.ttf",50) # Rank Font
                    d_text.text((1055,268),str(row["clusters"]).zfill(2),font=l_font,fill=(255,255,255,255),stroke_width=3, stroke_fill=(0,0,0,255))
                try:
                    d_text.text((817,430),"Rank: " + str(index+1).zfill(4),font=c_font,fill=(96,197,232,255))
                except:
                    d_text.text((917,430),str("No Rank").zfill(4),font=c_font,fill=(96,197,232,255))



                out = Image.alpha_composite(base,text)
                

                with BytesIO() as image_binary:
                    out.save(image_binary,'PNG')
                    image_binary.seek(0)
                    try:
                        row = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1;",ctx.guild.id)
                        settings = row["default_message_settings"]
                        if(settings[3] == "True"):
                            await ctx.send(file=discord.File(fp=image_binary, filename='image.png'),delete_after = 90)
                        else:
                            await ctx.send(file=discord.File(fp=image_binary, filename='image.png'))
                    except discord.errors.Forbidden:
                        extra_functions.logger_print("Forbidden Send occured at eggard self in " + ctx.message.guild.name + " | " + str(ctx.message.guild.id) + ".")
                    except discord.errors.HTTPException:
                        extra_functions.logger_print("HTTP Error Send occured at eggard self in " + ctx.message.guild.name + " | " + str(ctx.message.guild.id) + ".")
            except Exception as e:
                pass

        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","That wasn't a discord user!","Remember to do **" + self.bot.prefix + "eggard** [User Mention] or simply **" + self.bot.prefix + "eggard** to see your Egg Card",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"eggard single no discord user send error")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Woah There!  ⚠️","You recently used this command!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after) % 60) + " seconds!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name +  " function cooldown send")           
            return

    @commands.Cog.listener("on_reaction_add")
    async def basket_checker(self,reaction,u_obj):
        message_obj = await self.bot.pg_con.fetchrow("SELECT * FROM basket_messages WHERE Message_ID = $1",reaction.message.id)
        if message_obj != None:
            if message_obj['user_id'] == u_obj.id:
                reaction_name = u_obj.name
                # Setup Database Objs
                user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(reaction.message.guild.id) + " WHERE UserID = $1",message_obj['target_id'])
                page = message_obj['page']
                guild = reaction.message.guild

                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                regs = list(filter(lambda item: item['id'] in user['basket_eggs'],egg_dic['regular_eggs'])) + list(filter(lambda item: item['id'] in user['basket_eggs'],egg_dic['collectible_eggs']))
                
                string = ""

                if(reaction.emoji == '⬅️'):
                    try:
                        await reaction.message.remove_reaction('⬅️', u_obj)
                    except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                        extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                    
                    if(page - 1 >= 0):
                        page -= 1
                    else:
                        return
                elif(reaction.emoji == '➡️'):
                    try:
                        await reaction.message.remove_reaction('➡️', u_obj)
                    except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                        extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                    
                    if(page + 1 <= int(len(regs)/50)):
                        page += 1
                    else:
                        return                        
                u_obj = self.bot.get_user(message_obj['target_id'])

                if page == message_obj["page"]:
                    return

                for x in range(page*50,(page*50) + 50):

                    try:
                        regs[x]
                    except (IndexError, KeyError):
                        break          

                    string += str(regs[x]['emoji']) + new_fancy.small_nums("x " + str(user['basket_eggs'].count(regs[x]['id'])).zfill(3)) + "⠀"
                    if (x + 1) % 5 == 0 and x % 50 != 49:
                        string += "\n\n"

                await self.bot.pg_con.execute("UPDATE basket_messages set page = $1 WHERE Message_ID = $2;",page,reaction.message.id) #Update Loved
                embed = extra_functions.embedBuilder("🧺  " + u_obj.name + "'s Basket  🧺",string,str(len(user['basket_eggs'])) + "/" + str(50 + (25 * user['basket_level'])) + " Eggs\nControlled by " + reaction_name + "\nPage " + str(page + 1) + "/" + str(int(len(regs)/50)+1)  + " | Use emotes to switch pages/rank",0xE56A6A)
                await extra_functions.edit_embed_message(self.bot,reaction.message,embed,"basket edit")

    @commands.command(name = 'basket', aliases = ["bask"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def basket_command(self,ctx,u_obj: discord.User):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id) == None and not u_obj.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,u_obj.id)            
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id)

        if len(user['basket_eggs']) != 0:
            with open('JSON/Eggs.json') as f:
                egg_dic = json.load(f)
            regs = list(filter(lambda item: item['id'] in user['basket_eggs'],egg_dic['regular_eggs'])) + list(filter(lambda item: item['id'] in user['basket_eggs'],egg_dic['collectible_eggs']))
            
            string = ""

            for x in range(0,50):

                try:
                    regs[x]
                except (IndexError, KeyError):
                    break          
                
                string += str(regs[x]['emoji']) + new_fancy.small_nums("x " + str(user['basket_eggs'].count(regs[x]['id'])).zfill(3)) + "⠀"
                if (x + 1) % 5 == 0 and x != 49:
                    string += "\n\n"
            
            embed = extra_functions.embedBuilder("🧺  " + u_obj.name + "'s Basket  🧺",string,str(len(user['basket_eggs'])) + "/" + str(50 + (25 * user['basket_level'])) + " Eggs\nControlled by " + ctx.message.author.name + "\nPage 1/" + str(int(len(regs)/50)+1)  + " | Use emotes to switch pages/rank",0xE56A6A)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"basket send")
            await message_obj.add_reaction('⬅️')
            await message_obj.add_reaction('➡️')
            await self.bot.pg_con.execute("INSERT INTO basket_messages (Message_ID, Guild_ID, User_ID, Target_ID, timeout_message) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,ctx.guild.id,ctx.message.author.id,u_obj.id,datetime.now().timestamp() + 120) #Update Loved

        else:
            embed = extra_functions.embedBuilder("🧺  " + u_obj.name + "'s Empty Basket  🧺","Get some eggs using egg commands! e!help eggs","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"basket empty send")            

    @basket_command.error
    async def basket_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
                await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)            
            user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)

            if len(user['basket_eggs']) != 0:
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                regs = list(filter(lambda item: item['id'] in user['basket_eggs'],egg_dic['regular_eggs'])) + list(filter(lambda item: item['id'] in user['basket_eggs'],egg_dic['collectible_eggs']))
                
                string = ""

                for x in range(0,50):

                    try:
                        regs[x]
                    except (IndexError, KeyError):
                        break          
                    
                    string += str(regs[x]['emoji']) + new_fancy.small_nums("x " + str(user['basket_eggs'].count(regs[x]['id'])).zfill(3)) + "⠀"
                    if (x + 1) % 5 == 0 and x != 49:
                        string += "\n\n"
                
                embed = extra_functions.embedBuilder("🧺  " + ctx.message.author.name + "'s Basket  🧺",string,str(len(user['basket_eggs'])) + "/" + str(50 + (25 * user['basket_level'])) + " Eggs\nControlled by " + ctx.message.author.name + "\nPage 1/" + str(int(len(regs)/50)+1)  + " | Use emotes to switch pages/rank",0xE56A6A)
                message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"basket single send")
                await message_obj.add_reaction('⬅️')
                await message_obj.add_reaction('➡️')
                await self.bot.pg_con.execute("INSERT INTO basket_messages (Message_ID, Guild_ID, User_ID, Target_ID, timeout_message) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,ctx.guild.id,ctx.message.author.id,ctx.message.author.id,datetime.now().timestamp() + 120) #Update Loved
            else:
                embed = extra_functions.embedBuilder("🧺  " + ctx.message.author.name + "'s Empty Basket  🧺","Get some eggs using egg commands! e!help eggs","",0xE56A6A)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"basket single empty send")            
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","That wasn't a discord user!","Remember to do **" + self.bot.prefix + "eggard** [User Mention] or simply **" + self.bot.prefix + "eggard** to see your Egg Card",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"basket single That wasn't a discord user send")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Woah There!  ⚠️","You recently used this command!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after) % 60) + " seconds!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name +  " function cooldown send")           
            return

    @commands.command(name = 'collection')
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def collection_command(self,ctx,u_obj: discord.User):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id) == None and not u_obj.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,u_obj.id)            
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id)

        if len(user['collection_eggs']) != 0:
            with open('JSON/Eggs.json') as f:
                egg_dic = json.load(f)
            regs = list(filter(lambda item: item['id'] in user['collection_eggs'],egg_dic['collectible_eggs']))
            
            string = ""

            for x in range(0,len(regs)):
                string += str(regs[x]['emoji'])
                if (x + 1) % 5 == 0:
                    string += "\n\n"
            
            if(len(user['collection_eggs']) == 30):
                embed = extra_functions.embedBuilder("✨💼  " + u_obj.name + "'s Completed Collection  💼✨",string,str(len(user['collection_eggs'])) + "/30 Eggs",0xE56A6A)
            else:
                embed = extra_functions.embedBuilder("💼  " + u_obj.name + "'s Collection  💼",string,str(len(user['collection_eggs'])) + "/30 Eggs",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"collection send")

        else:
            embed = extra_functions.embedBuilder("💼  " + u_obj.name + "'s Empty Collection  💼","Get some eggs using egg commands! e!help eggs","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"collection empty send")            

    @collection_command.error
    async def collection_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
                await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)            
            user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)

            if len(user['collection_eggs']) != 0:
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                regs = list(filter(lambda item: item['id'] in user['collection_eggs'],egg_dic['collectible_eggs']))
                
                string = ""

                for x in range(0,len(regs)):
                    string += str(regs[x]['emoji'])
                    if (x + 1) % 5 == 0:
                        string += "\n\n"
                
                if(len(user['collection_eggs']) == 30):
                    embed = extra_functions.embedBuilder("✨💼  " + ctx.message.author.name + "'s Completed Collection  💼✨",string,str(len(user['collection_eggs'])) + "/30 Eggs",0xE56A6A)
                else:
                    embed = extra_functions.embedBuilder("💼  " + ctx.message.author.name + "'s Collection  💼",string,str(len(user['collection_eggs'])) + "/30 Eggs",0xE56A6A)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"collection send")

            else:
                embed = extra_functions.embedBuilder("💼  " + ctx.message.author.name + "'s Empty Collection  💼","Get some eggs using egg commands! e!help eggs","",0xE56A6A)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"collection empty send")            
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","That wasn't a discord user!","Remember to do **" + self.bot.prefix + "eggard** [User Mention] or simply **" + self.bot.prefix + "eggard** to see your Egg Card",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"collection no user send")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Woah There!  ⚠️","You recently used this command!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after) % 60) + " seconds!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name +  " function cooldown send")           
            return

    @commands.command(name = 'case')
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def case_command(self,ctx,u_obj: discord.User):
        if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id) == None and not u_obj.bot:
            await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,u_obj.id)            
        user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",u_obj.id)

        if len(user['case_eggs']) != 0:
            with open('JSON/Eggs.json') as f:
                egg_dic = json.load(f)
            regs = list(filter(lambda item: item['id'] in user['case_eggs'],egg_dic['regular_eggs'])) + list(filter(lambda item: item['id'] in user['case_eggs'],egg_dic['collectible_eggs']))
            
            string = ""

            for x in range(0,len(user['case_eggs'])):
                string += str([item for item in regs if item['id'] == user['case_eggs'][x]][0]['emoji']) + "   "
                if (x + 1) % 10 == 0:
                    string += "\n\n"
            
            embed = extra_functions.embedBuilder("🧺  " + u_obj.name + "'s Display Case  🧺",string,str(len(user['case_eggs'])) + "/" + str(20) + " Eggs",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"display send")

        else:
            embed = extra_functions.embedBuilder("🧺  " + u_obj.name + "'s Empty Display Case  🧺","Get some eggs using egg commands! e!help eggs","",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"display empty send")   

    @case_command.error
    async def case_command_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if await self.bot.pg_con.fetchrow("SELECT 1 FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id) == None and not ctx.message.author.bot:
                await Database_Methods.Insert_User(self.bot,ctx.message.guild.id,ctx.message.author.id)            
            user = await self.bot.pg_con.fetchrow("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " WHERE UserID = $1",ctx.message.author.id)

            if len(user['case_eggs']) != 0:
                with open('JSON/Eggs.json') as f:
                    egg_dic = json.load(f)
                regs = list(filter(lambda item: item['id'] in user['case_eggs'],egg_dic['regular_eggs'])) + list(filter(lambda item: item['id'] in user['case_eggs'],egg_dic['collectible_eggs']))
                
                string = ""

                for x in range(0,len(user['case_eggs'])):
                    string += str([item for item in regs if item['id'] == user['case_eggs'][x]][0]['emoji']) + "   "
                    if (x + 1) % 10 == 0:
                        string += "\n\n"
                
                embed = extra_functions.embedBuilder("🧺  " + ctx.message.author.name + "'s Display Case  🧺",string,str(len(user['case_eggs'])) + "/" + str(20) + " Eggs",0xE56A6A)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"display single send")

            else:
                embed = extra_functions.embedBuilder("🧺  " + ctx.message.author.name + "'s Empty Display Case  🧺","Get some eggs using egg commands! e!help eggs","",0xE56A6A)
                await extra_functions.send_embed_ctx(self.bot,ctx,embed,30,"display single empty send")            
        elif isinstance(error,commands.CommandInvokeError):
            pass
        elif isinstance(error, discord.ext.commands.errors.UserNotFound):
            embed = extra_functions.embedBuilder("⚠️   Whoops!  ⚠️ ","That wasn't a discord user!","Remember to do **" + self.bot.prefix + "eggard** [User Mention] or simply **" + self.bot.prefix + "eggard** to see your Egg Card",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,"display single no user send")
        elif isinstance(error,commands.CommandOnCooldown):
            embed = extra_functions.embedBuilder("⚠️  Woah There!  ⚠️","You recently used this command!","Please wait " + str(int(error.retry_after/60)) + " minutes, " + str(int(error.retry_after) % 60) + " seconds!",0xE56A6A)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,20,ctx.command.name +  " function cooldown send")           
            return


    def mask_circle_transparent(self,img, blur_radius, offset=0):
        width, height = img.size
        x = (width - height)//2
        img_cropped = img.crop((x, 0, x+height, height))

        # create grayscale image with white circle (255) on black background (0)
        mask = Image.new('L', img_cropped.size)
        mask_draw = ImageDraw.Draw(mask)
        width, height = img_cropped.size
        mask_draw.ellipse((0, 0, width, height), fill=255)
        #mask.show()

        # add mask as alpha channel
        img_cropped.putalpha(mask)

        return img_cropped

    def card_point_rpg_string(self,points):
        p_string = str(points)
        if(points >= 100000000):
            return p_string[:3] + "." + p_string[3:4] + "M"
        elif(points >= 10000000):
            return p_string[:2] + "." + p_string[2:3] + "M"
        elif(points >= 1000000):
            return p_string[:1] + "." + p_string[1:3] + "M"
        elif(points >= 100000):
            return p_string[:3] + "K"
        elif(points >= 10000):
            return p_string[:2] + "." + p_string[2:3] + "K"
        elif(points >= 1000):
            return p_string[:1] + "." + p_string[1:3] + "K"
        return p_string

    def point_rpg_string(self,points):
        p_string = str(points)
        if(points > 100000000):
            return p_string[:3] + "." + p_string[3:4] + "M"
        elif(points > 10000000):
            return p_string[:2] + "." + p_string[2:3] + "M"
        elif(points > 1000000):
            return p_string[:1] + "." + p_string[1:3] + "M"
        elif(points > 100000):
            return p_string[:3] + "." + p_string[3:4] + "K"
        elif(points > 10000):
            return p_string[:2] + "." + p_string[2:3] + "K"
        return p_string

    @commands.command(name = 'leaderboard', aliases = ["top10","lb","leaderboards"])
    async def leaderboard_command(self,ctx):
        row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " ORDER BY array_length(basket_eggs,1) DESC")
        user_empty = False
        for x in range(len(row)-1,-1,-1):
            try:
                if len(row[x]['basket_eggs']) == 0:
                    if row[x]['userid'] == ctx.message.author.id:
                        user_empty = True
                    row.pop(x)
            except IndexError:
                break

        for index, item in enumerate(row):
            if item['userid'] == ctx.message.author.id:
                break
        try:
            index += 1
        except:
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Empty Leaderboard","No one has any eggs! Go get some!","e!help egg",0xFF42AE)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function unbound send embed")
            return
            
        string = "```css\n[Rank] | {.Eggs.} | Egg Collector\n==========================================\n"
        fucking_eat_my_ass = False
        if not len(row) == 0:
            for x in range (0,10):
                try:
                    row[x]
                except IndexError:
                    break
                
                if(row[x]["userid"] == ctx.message.author.id):
                    fucking_eat_my_ass = True
                if(len(row[x]['basket_eggs']) != 0):
                    try:
                        string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['basket_eggs'])).zfill(4) + "   | " + self.bot.get_user(row[x]["userid"]).display_name[:18] + "\n"
                    except Exception as e:
                        try:
                            user_name = await self.bot.fetch_user(row[x]["userid"])
                            string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['basket_eggs'])).zfill(4) + "   | " + user_name.display_name[:18] + "\n"
                        except Exception as e:
                            print(row[x]["userid"])
            if not fucking_eat_my_ass:
                if user_empty:
                    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(len(row)+1).zfill(2) + "]" + "  |   " + str(0).zfill(4) + "   | " + ctx.message.author.display_name[:18] + "\n"
                else:
                    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(index+1).zfill(2) + "]" + "  |   " + str(len(row[index]['basket_eggs'])).zfill(4) + "   | " + ctx.message.author.display_name[:18] + "\n"

            page_max = 10
            if int(len(row)/10) + 1 < 10:
                page_max = int(len(row)/10) + 1
            string += "```"
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Leaderboard",string,"Page 1/" + str(page_max)  + " | Use emotes to switch pages/rank",0xFF42AE)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function send embed")
            await message_obj.add_reaction('⏪')
            await message_obj.add_reaction('⬅️')
            await message_obj.add_reaction('➡️')
            await message_obj.add_reaction('⏩')
            await self.bot.pg_con.execute("INSERT INTO role_lb_messages (Message_ID,User_ID,Guild_ID,Timeout_Message) VALUES ($1,$2,$3,$4) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,ctx.message.author.id,ctx.guild.id,datetime.now().timestamp() + 120)
        else:
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Empty Leaderboard","","Get some eggs to have a leaderboard!",0xFF42AE)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function send embed")
    
    @leaderboard_command.error
    async def leaderboard_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            embedVar = discord.Embed(title="Attention Server Staff!", description="Whoops! Looks like this bot is missing some perms! Make sure it has the manage channel, message and role perms.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,120,"leaderboard function missing perms")
        elif isinstance(error,commands.CommandInvokeError):
            pass

    @commands.Cog.listener("on_reaction_add")
    async def leaderboard_reaction(self,reaction,user):
        if self.bot.ready:
            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",reaction.message.guild.id)
            if settings["message_state"] != -2:
                if not await self.bot.pg_con.fetchrow("SELECT 1 FROM role_lb_messages WHERE Message_ID = $1",reaction.message.id) == None:
                    row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(reaction.message.guild.id) + " ORDER BY array_length(basket_eggs,1) DESC")
                    lb_row = await self.bot.pg_con.fetchrow("SELECT * FROM role_lb_messages WHERE Message_ID = $1",reaction.message.id)

                    user_empty = False
                    for x in range(len(row)-1,-1,-1):
                        try:
                            if len(row[x]['basket_eggs']) == 0:
                                if row[x]['userid'] == user.id:
                                    user_empty = True
                                row.pop(x)
                        except IndexError:
                            break

                    for index, item in enumerate(row):
                        if item['userid'] == user.id:
                            break
                    index += 1
                            
                    page = lb_row["page"]

                    guild = reaction.message.guild
                    
                    if lb_row["user_id"] == user.id:
                        
                        if(reaction.emoji == '⬅️'):
                            try:
                                await reaction.message.remove_reaction('⬅️', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            if(page - 1 >= 0):
                                page -= 1
                            else:
                                return
                        elif(reaction.emoji == '➡️'):
                            try:
                                await reaction.message.remove_reaction('➡️', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            if(page + 1 <= int(len(row)/10) and page + 1 <= 9):
                                page += 1
                            else:
                                return
                        elif(reaction.emoji == '⏪'):
                            try:
                                await reaction.message.remove_reaction('⏪', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            for x in range(0,5):
                                if(page - 1 >= 0):
                                    page -= 1
                                else:
                                    break
                        elif(reaction.emoji == '⏩'):
                            try:
                                await reaction.message.remove_reaction('⏩', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            for x in range(0,5):
                                if(page + 1 <= int(len(row)/10) and page + 1 <= 9):
                                    page += 1
                                else:
                                    break

                        if page == lb_row["page"]:
                            return

                        string = "```css\n[Rank] | {.Eggs.} | Egg Collector\n==========================================\n"

                        fucking_eat_my_ass = False #post user on bottom bool

                        shit_multiplier = page * 10

                        for x in range (0 + shit_multiplier,10 + shit_multiplier):
                            try:
                                row[x]
                            except IndexError:
                                break
                            
                            if(row[x]["userid"] == user.id):
                                fucking_eat_my_ass = True
                            if(len(row[x]['basket_eggs']) != 0):
                                try:
                                    string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['basket_eggs'])).zfill(4) + "   | " + self.bot.get_user(row[x]["userid"]).display_name[:18] + "\n"
                                except Exception as e:
                                    try:
                                        user_name = await self.bot.fetch_user(row[x]["userid"])
                                        string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['basket_eggs'])).zfill(4) + "   | " + user_name.display_name[:18] + "\n"
                                    except Exception as e:
                                        print(row[x]["userid"])

                        if not fucking_eat_my_ass:
                            if user_empty:
                                string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(len(row)+1).zfill(2) + "]" + "  |   " + str(0).zfill(4) + "   | " + user.display_name[:18] + "\n"
                            else:
                                string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(index).zfill(2) + "]" + "  |   " + str(len(row[index-1]['basket_eggs'])).zfill(4) + "   | " + user.display_name[:18] + "\n"
                        string += "```"

                        page_max = 10
                        
                        if int(len(row)/10) + 1 < 10:
                            page_max = int(len(row)/10) + 1

                        embed = extra_functions.embedBuilder(user.name + "'s Leaderboard",string,"Page " + str(page + 1) + "/" + str(page_max)  + " | Use emotes to switch pages/rank",0xFF42AE)
                        
                        await extra_functions.edit_embed_message(self.bot,reaction.message,embed,"check heart message function edit some")
                        await self.bot.pg_con.execute("UPDATE role_lb_messages set page = $1 WHERE Message_ID = $2;",page,reaction.message.id) #Update Loved

    @commands.command(name = 'historyboard', aliases = ["hlb"])
    async def historyboard_command(self,ctx):
        row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " ORDER BY eggs_collected DESC")
        user_empty = False
        for x in range(len(row)-1,-1,-1):
            try:
                if row[x]['eggs_collected'] == 0:
                    if row[x]['userid'] == ctx.message.author.id:
                        user_empty = True
                    row.pop(x)
            except IndexError:
                break

        for index, item in enumerate(row):
            if item['userid'] == ctx.message.author.id:
                break
        try:
            index += 1
        except:
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Empty History Leaderboard","No one has any eggs! Go get some!","e!help egg",0xFF42AE)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function unbound send embed")
            return

        string = "```css\n[Rank] |  {.Eggs.}  | Egg Collector\n==========================================\n"
        fucking_eat_my_ass = False
        if not len(row) == 0:
            for x in range (0,10):
                try:
                    row[x]
                except IndexError:
                    break
                
                if(row[x]["userid"] == ctx.message.author.id):
                    fucking_eat_my_ass = True
                if(row[x]['eggs_collected'] != 0):
                    try:
                        string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(row[x]['eggs_collected']).zfill(6) + "   | " + self.bot.get_user(row[x]["userid"]).display_name[:18] + "\n"
                    except Exception as e:
                        try:
                            user_name = await self.bot.fetch_user(row[x]["userid"])
                            string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(row[x]['eggs_collected']).zfill(6) + "   | " + user_name.display_name[:18] + "\n"
                        except Exception as e:
                            print(row[x]["userid"])
            if not fucking_eat_my_ass:
                if user_empty:
                    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(len(row)+1).zfill(2) + "]" + "  |   " + str(0).zfill(6) + "   | " + ctx.message.author.display_name[:18] + "\n"
                else:
                    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(index+1).zfill(2) + "]" + "  |   " + str(row[index]['eggs_collected']).zfill(6) + "   | " + ctx.message.author.display_name[:18] + "\n"
            
            page_max = 10
            if int(len(row)/10) + 1 < 10:
                page_max = int(len(row)/10) + 1
            string += "```"
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s History Leaderboard",string,"Page 1/" + str(page_max)  + " | Use emotes to switch pages/rank",0xFF42AE)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function send embed")
            await message_obj.add_reaction('⏪')
            await message_obj.add_reaction('⬅️')
            await message_obj.add_reaction('➡️')
            await message_obj.add_reaction('⏩')
            await self.bot.pg_con.execute("INSERT INTO history_lb_messages (Message_ID,User_ID,Guild_ID,Timeout_Message) VALUES ($1,$2,$3,$4) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,ctx.message.author.id,ctx.guild.id,datetime.now().timestamp() + 120)
        else:
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Empty Leaderboard","","Get some eggs to have a leaderboard!",0xFF42AE)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function send embed")
    
    @historyboard_command.error
    async def historyboard_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            embedVar = discord.Embed(title="Attention Server Staff!", description="Whoops! Looks like this bot is missing some perms! Make sure it has the manage channel, message and role perms.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,120,"leaderboard function missing perms")
        elif isinstance(error,commands.CommandInvokeError):
            pass

    @commands.Cog.listener("on_reaction_add")
    async def historyboard_reaction(self,reaction,user):
        if self.bot.ready:
            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",reaction.message.guild.id)
            if settings["message_state"] != -2:
                if not await self.bot.pg_con.fetchrow("SELECT 1 FROM history_lb_messages WHERE Message_ID = $1",reaction.message.id) == None:
                    row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(reaction.message.guild.id) + " ORDER BY eggs_collected DESC")
                    lb_row = await self.bot.pg_con.fetchrow("SELECT * FROM history_lb_messages WHERE Message_ID = $1",reaction.message.id)
                    
                    user_empty = False

                    for x in range(len(row)-1,-1,-1):
                        try:
                            if row[x]['eggs_collected'] == 0:
                                if row[x]['userid'] == user.id:
                                    user_empty = True
                                row.pop(x)
                        except IndexError:
                            break
                            
                    for index, item in enumerate(row):
                        if item['userid'] == user.id:
                            break
                    index += 1
                    page = lb_row["page"]

                    guild = reaction.message.guild
                    
                    if lb_row["user_id"] == user.id:
                        
                        if(reaction.emoji == '⬅️'):
                            try:
                                await reaction.message.remove_reaction('⬅️', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            if(page - 1 >= 0):
                                page -= 1
                            else:
                                return
                        elif(reaction.emoji == '➡️'):
                            try:
                                await reaction.message.remove_reaction('➡️', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            if(page + 1 <= int(len(row)/10) and page + 1 <= 9):
                                page += 1
                            else:
                                return
                        elif(reaction.emoji == '⏪'):
                            try:
                                await reaction.message.remove_reaction('⏪', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            for x in range(0,5):
                                if(page - 1 >= 0):
                                    page -= 1
                                else:
                                    break
                        elif(reaction.emoji == '⏩'):
                            try:
                                await reaction.message.remove_reaction('⏩', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            for x in range(0,5):
                                if(page + 1 <= int(len(row)/10) and page + 1 <= 9):
                                    page += 1
                                else:
                                    break

                        if page == lb_row["page"]:
                            return

                        string = "```css\n[Rank] | {.Eggs.} | Egg Collector\n==========================================\n"

                        fucking_eat_my_ass = False #post user on bottom bool

                        shit_multiplier = page * 10

                        for x in range (0 + shit_multiplier,10 + shit_multiplier):
                            try:
                                row[x]
                            except IndexError:
                                break
                            
                            if(row[x]["userid"] == user.id):
                                fucking_eat_my_ass = True
                            if(row[x]['eggs_collected'] != 0):
                                try:
                                    string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(row[x]['eggs_collected']).zfill(6) + "   | " + self.bot.get_user(row[x]["userid"]).display_name[:18] + "\n"
                                except Exception as e:
                                    try:
                                        user_name = await self.bot.fetch_user(row[x]["userid"])
                                        string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(row[x]['eggs_collected']).zfill(6) + "   | " + user_name.display_name[:18] + "\n"
                                    except Exception as e:
                                        print(row[x]["userid"])

                        if not fucking_eat_my_ass:
                            if user_empty:
                                string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(len(row)+1).zfill(2) + "]" + "  |   " + str(0).zfill(6) + "   | " + user.display_name[:18] + "\n"
                            else:
                                string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(index).zfill(2) + "]" + "  |   " + str(row[index-1]['eggs_collected']).zfill(6) + "   | " + user.display_name[:18] + "\n"
                        string += "```"

                        page_max = 10
                        
                        if int(len(row)/10) + 1 < 10:
                            page_max = int(len(row)/10) + 1

                        embed = extra_functions.embedBuilder(user.name + "'s History Leaderboard",string,"Page " + str(page + 1) + "/" + str(page_max)  + " | Use emotes to switch pages/rank",0xFF42AE)
                        
                        await extra_functions.edit_embed_message(self.bot,reaction.message,embed,"check heart message function edit some")
                        await self.bot.pg_con.execute("UPDATE history_lb_messages set page = $1 WHERE Message_ID = $2;",page,reaction.message.id) #Update Loved


    @commands.command(name = 'collectionboard', aliases = ["clb"])
    async def collectionboard_command(self,ctx):
        row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(ctx.message.guild.id) + " ORDER BY array_length(collection_eggs,1) DESC")
        user_empty = False
        for x in range(len(row)-1,-1,-1):
            try:
                if len(row[x]['collection_eggs']) == 0:
                    if row[x]['userid'] == ctx.message.author.id:
                        user_empty = True
                    row.pop(x)
            except IndexError:
                break

        for index, item in enumerate(row):
            if item['userid'] == ctx.message.author.id:
                break    
        try:
            index += 1
        except:
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Empty Collection Leaderboard","No one has any rare eggs! Go get some!","e!help egg",0xFF42AE)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function unbound send embed")
            return

        string = "```css\n[Rank] | .Eggs. | Egg Collector\n==========================================\n"
        fucking_eat_my_ass = False
        if not len(row) == 0:
            for x in range (0,10):
                try:
                    row[x]
                except IndexError:
                    break
                
                if(row[x]["userid"] == ctx.message.author.id):
                    fucking_eat_my_ass = True
                if(len(row[x]['collection_eggs']) != 0):
                    try:
                        string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['collection_eggs'])).zfill(2) + "   |  " + self.bot.get_user(row[x]["userid"]).display_name[:18] + "\n"
                    except Exception as e:
                        try:
                            user_name = await self.bot.fetch_user(row[x]["userid"])
                            string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['collection_eggs'])).zfill(2) + "   |  " + user_name.display_name[:18] + "\n"
                        except Exception as e:
                            print(row[x]["userid"])
            if not fucking_eat_my_ass:
                if user_empty:
                    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(len(row)+1).zfill(2) + "]" + "  |   " + str(0).zfill(2) + "   | " + ctx.message.author.display_name[:18] + "\n"
                else:
                    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(index+1).zfill(2) + "]" + "  |   " + str(len(row[index]['collection_eggs'])).zfill(2) + "   | " + ctx.message.author.display_name[:18] + "\n"

            page_max = 10
            if int(len(row)/10) + 1 < 10:
                page_max = int(len(row)/10) + 1
            string += "```"
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Collection Leaderboard",string,"Page 1/" + str(page_max)  + " | Use emotes to switch pages/rank",0xFF42AE)
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"leaderboard function send embed")
            await message_obj.add_reaction('⏪')
            await message_obj.add_reaction('⬅️')
            await message_obj.add_reaction('➡️')
            await message_obj.add_reaction('⏩')
            await self.bot.pg_con.execute("INSERT INTO collection_lb_messages (Message_ID,User_ID,Guild_ID,Timeout_Message) VALUES ($1,$2,$3,$4) ON CONFLICT (Message_ID) DO NOTHING;",message_obj.id,ctx.message.author.id,ctx.guild.id,datetime.now().timestamp() + 120)
        else:
            embed = extra_functions.embedBuilder(ctx.message.author.name + "'s Empty Leaderboard","","Get some eggs to have a leaderboard!",0xFF42AE)
            await extra_functions.send_embed_ctx(self.bot,ctx,embed,120,"collection leaderboard function send embed")
    
    @collectionboard_command.error
    async def collectionboard_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            embedVar = discord.Embed(title="Attention Server Staff!", description="Whoops! Looks like this bot is missing some perms! Make sure it has the manage channel, message and role perms.", color=0xFFCC00)
            embedVar.set_footer(text = "If you encounter anymore problems, please join https://discord.gg/ZNpCNyNubU and tag TheKWitt!")
            
            message_obj = await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,120,"leaderboard function missing perms")
        elif isinstance(error,commands.CommandInvokeError):
            pass

    @commands.Cog.listener("on_reaction_add")
    async def collectionboard_reaction(self,reaction,user):
        if self.bot.ready:
            settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE guild_id = $1",reaction.message.guild.id)
            if settings["message_state"] != -2:
                if not await self.bot.pg_con.fetchrow("SELECT 1 FROM collection_lb_messages WHERE Message_ID = $1",reaction.message.id) == None:
                    row = await self.bot.pg_con.fetch("SELECT * FROM " + "g_" + str(reaction.message.guild.id) + " ORDER BY array_length(collection_eggs,1) DESC")
                    lb_row = await self.bot.pg_con.fetchrow("SELECT * FROM collection_lb_messages WHERE Message_ID = $1",reaction.message.id)
                    
                    user_empty = False

                    for x in range(len(row)-1,-1,-1):
                        try:
                            if len(row[x]['collection_eggs']) == 0:
                                if row[x]['userid'] == user.id:
                                    user_empty = True
                                row.pop(x)
                        except IndexError:
                            break

                    for index, item in enumerate(row):
                        if item['userid'] == user.id:
                            break
                    index += 1
                    page = lb_row["page"]

                    guild = reaction.message.guild
                    
                    if lb_row["user_id"] == user.id:
                        
                        if(reaction.emoji == '⬅️'):
                            try:
                                await reaction.message.remove_reaction('⬅️', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            if(page - 1 >= 0):
                                page -= 1
                            else:
                                return
                        elif(reaction.emoji == '➡️'):
                            try:
                                await reaction.message.remove_reaction('➡️', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            if(page + 1 <= int(len(row)/10) and page + 1 <= 9):
                                page += 1
                            else:
                                return
                        elif(reaction.emoji == '⏪'):
                            try:
                                await reaction.message.remove_reaction('⏪', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            for x in range(0,5):
                                if(page - 1 >= 0):
                                    page -= 1
                                else:
                                    break
                        elif(reaction.emoji == '⏩'):
                            try:
                                await reaction.message.remove_reaction('⏩', user)
                            except(discord.errors.Forbidden,discord.errors.NotFound,discord.errors.HTTPException,discord.errors.InvalidArgument):
                                extra_functions.logger_print(guild.name + " with ID: " + str(guild.id) + " - No Access To Reaction")                    
                            
                            for x in range(0,5):
                                if(page + 1 <= int(len(row)/10) and page + 1 <= 9):
                                    page += 1
                                else:
                                    break

                        if page == lb_row["page"]:
                            return


                        string = "```css\n[Rank] | .Eggs.  | Egg Collector\n==========================================\n"

                        fucking_eat_my_ass = False #post user on bottom bool

                        shit_multiplier = page * 10

                        for x in range (0 + shit_multiplier,10 + shit_multiplier):
                            try:
                                row[x]
                            except IndexError:
                                break
                            
                            if(row[x]["userid"] == user.id):
                                fucking_eat_my_ass = True
                            if(len(row[x]['collection_eggs']) != 0):
                                try:
                                    string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['collection_eggs'])).zfill(2) + "  | " + self.bot.get_user(row[x]["userid"]).display_name[:18] + "\n"
                                except Exception as e:
                                    try:
                                        user_name = await self.bot.fetch_user(row[x]["userid"])
                                        string += " " + "[" + str(x+1).zfill(2) + "]" + "  |   " + str(len(row[x]['collection_eggs'])).zfill(2) + "  | " + user_name.display_name[:18] + "\n"
                                    except Exception as e:
                                        print(row[x]["userid"])

                        if not fucking_eat_my_ass:
                            if user_empty:
                                string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(len(row)+1).zfill(2) + "]" + "  |   " + str(0).zfill(2) + "   | " + user.display_name[:18] + "\n"
                            else:
                                string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n " + "[" + str(index).zfill(2) + "]" + "  |   " + str(len(row[index-1]['collection_eggs'])).zfill(2) + "   | " + user.display_name[:18] + "\n"

                        string += "```"

                        page_max = 10
                        
                        if int(len(row)/10) + 1 < 10:
                            page_max = int(len(row)/10) + 1

                        embed = extra_functions.embedBuilder(user.name + "'s Collection Leaderboard",string,"Page " + str(page + 1) + "/" + str(page_max)  + " | Use emotes to switch pages/rank",0xFF42AE)
                        
                        await extra_functions.edit_embed_message(self.bot,reaction.message,embed,"check heart message function edit some")
                        await self.bot.pg_con.execute("UPDATE collection_lb_messages set page = $1 WHERE Message_ID = $2;",page,reaction.message.id) #Update Loved

    def rank(self,points):
        if points > 1000000:
            return "THE CRIMSON INVESTIGATOR"
        elif points > 250000:
            return "GOD OF EGGS"
        elif points > 100000:
            return "Cracklefest Hyper Collector"
        elif points > 50000:
            return "Cracklefest Gadabout"
        elif points > 22500:
            return "Cracklefest Globetrotter"
        elif points > 10000:
            return "Cracklefest Rover"
        elif points > 4500:
            return "Cracklefest Sightseer"
        elif points > 2000:
            return "Cracklefest Collector"
        elif points > 1000:
            return "Cracklefest Traveler"
        elif points > 500:
            return "Cracklefest Wanderer"
        elif points > 250:
            return "Cracklefest Explorer"
        elif points > 100:
            return "Cracklefest Scout"
        else:
            return "Cracklefest Visitor"



    @commands.command(name = 'manual') # Info Command
    async def manual(self,ctx,type):
        if type.lower() == "summary":
            embedVar = discord.Embed(title="📔  Cracklefest's Summary Manual  📔", description="", color=0xFFA500)
            embedVar.add_field(name = "What is this bot?", value = "This is an Easter Incremental Game! Imagine Easter but with Rich RPG Lore! You collect eggs to get #1 on the server and earn a title or collect all 30 exclusive eggs to earn the collector title!",inline=False)
            embedVar.add_field(name = "What do you do?", value = "You collect eggs, sell them for gold coins and upgrade your basket with said coins. You can gather eggs by exploring or opening egg clusters that spawn on your server! You can get gold coins (Ask the mods if they set this up yet.) You can see the commands with " + self.bot.prefix + "help eggs!",inline=False)
            embedVar.add_field(name = "How do you get eggs?", value = "You can explore using e!explore or break clusters you collected with e!uncluster! You can also get mail with items using the e!mailbox command! For more commands about getting eggs, try out the " + self.bot.prefix + "help eggs command!",inline=False)
            embedVar.add_field(name = "Where can I find Egg IDs?", value = "**You can find Egg IDs by clicking/tapping the emoji of the egg!**",inline=False)
            embedVar.add_field(name = "How does ranking work?", value = "The person who has the most in their basket gets the role! You can check who is first with e!leaderboard!",inline=False)
            embedVar.add_field(name = "What if I don't want to go for the top collector?", value = "We have something for you then! Every area has five valuable collectible eggs that **ANYONE** can get! If you get all 30, you get a special special role!",inline=False)
            embedVar.add_field(name = "How long is this bot going to last?", value = "For the whole month of april! It won't end on april! The bot will be online till May 5th so you can see all the stats after the event ends!",inline=False)
            embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"manual command send")
        if type.lower() == "things":
            embedVar = discord.Embed(title="📔  Cracklefest's Thing Manual  📔", description="", color=0xFFA500)
            embedVar.add_field(name = "Eggs, Gold Coins and Upgrading", value = "Eggs are collectible objects you can get by exploring or openning clusters! You can either find regular eggs or rare eggs! (Except for The Arcane Void)\n**You can find Egg IDs by clicking/tapping the emoji of the egg!**\n\nGold Coins are the currency used among the conoras. Using gold coins will allow you to upgrade your basket to hold more eggs!",inline=False)
            embedVar.add_field(name = "Baskets, Collection, And Display Cases", value = "Baskets are used to hold eggs you receive! Eggs in the basket are randomly selected to be sold once the command is used. You can upgrade your basket with e!upgrade with gold coins!\n**The higher the level you are, the more eggs you can collect at once from clusters and exploring! But you'll have to spend more gold coins for each level.**\n\nCollections are where your rare eggs are stored. It can't hold duplicates so all duplicates are sent straight to your basket instead!\n\nDisplay Cases are where you can keep eggs you don't want to sell! Duplicate Rare Eggs can be placed here as well!",inline=False)
            embedVar.add_field(name = "Exploring and Clusters", value = "Exploring allows you to visit different areas with unique interactions and collect eggs! Each area has its own set of regular and rare eggs! There are 6 different areas in Coneyford! You can see them all with e!atlas. Egg clusters are bundles of eggs that can be collected from your mailbox or messages that spawn on the server! You can break them with e!uncluster! Make sure you have room for them though!",inline=False)
            embedVar.add_field(name = "Mailbox and Lottery", value = "Mailboxes are where you can get free gold coins and clusters sent by the folks of Coneyford! Lottery is where you can test your luck by betting your gold coins for tripling your payout!",inline=False)
            embedVar.add_field(name = "Donating and Purification", value = "Purification is a way for the server to cooperatively help stop the corruption in Coneyford! You can donate eggs using the donate command. If enough eggs are donated, the area gets purified. Purified Areas grant explorers double the amount of eggs! If all the areas are purified, then any exploration will become tripled in value!\n\nFor every area purified, you also get a bonus towards clusters as well!",inline=False)
            embedVar.add_field(name = "Trading", value = "Want an egg someone else has? Well now you can trade with them! As long as they have a regular egg or duplicate collectible is in their basket, you can give them whatever you want to from your basket in return for that egg! Use the command e!trade [User Mention] [Your Egg ID] [Their Egg ID] to open up a trade window! They have the choose to either accept or deny that offer within five minutes!",inline=False)
            embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"manual command send")
        if type.lower() == "settings":
            embedVar = discord.Embed(title="📔  Cracklefest's Settings Manual  📔", description="", color=0xFFA500)
            embedVar.add_field(name = "What are settings?", value = "The settings are for you to be able to tweek the bot to however you desire! This makes it easier for servers of all sizes!",inline=False)
            embedVar.add_field(name = "What are the settings for Egg Cooldowns?", value = "Quick - 120 Seconds\nShort - 240 Seconds\nNormal - 300 Seconds\nLong - 600 Seconds\nLengthy - 1200 Seconds",inline=False)
            embedVar.add_field(name = "What are the settings for Mailbox Cooldowns?", value = "Quick - 4 Hours\nShort - 8 Hours\nNormal - 12 Hours\nLong - 18 Hours\nLengthy - 24 Hours",inline=False)
            embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"manual command send")


    @manual.error
    async def manual_error(self,ctx,error):
        if isinstance(error, commands.MissingRequiredArgument):
            embedVar = discord.Embed(title="📔  Cracklefest's Manual  📔", description=self.manual_string(), color=0xFFA500)
            embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
            await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"manual command send")


        if isinstance(error, commands.BotMissingPermissions):
            pass

    def manual_string(self):
        string = "Welcome to the manual directory!\n\n"
        string += "For the how to play portion. Use **e!manual summary**\n"
        string += "For the explanations of everything portion. Use **e!manual things**\n"
        string += "For the settings portion. Use **e!manual settings**"
        string += "\n\n----------------------------------------------------------\n\n"

        return string

    @commands.command(name = 'invite') # Info Command
    async def invite(self,ctx):
        #embedVar = discord.Embed(title="🔗  Bot Link  🔗", description="The bot isn't ready to be invited to everywhere yet! ;)", color=0xFFA500)
        embedVar = discord.Embed(title="🔗  Bot Link  🔗", description="Use this link if you want to invite the bot to your own server!\n\nhttps://discord.com/oauth2/authorize?client_id=819714651184693259&permissions=268823632&scope=bot", color=0xFFA500)
        embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"manual command send")

    @invite.error
    async def invite_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass

    @commands.command(name = 'credits') # Info Command
    async def credits(self,ctx):
        embedVar = discord.Embed(title="📔  Credit Sheet  📔", description=self.credits_string(self.bot.get_guild(746399419460616193).members), color=0xFFA500)
        embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"manual command send")

    @credits.error
    async def credits_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass

    def credits_string(self,members):
        string = "\n__**The Engineer and Artist**__\n"
        string += "TheKWitt"
        string += "\n\n__**Beta Testers from Vapordice**__\n"

        temp = " "
        beta_testers = []
        for member in members:
            if "beta bot tester" in [r.name.lower() for r in member.roles]:
                beta_testers.append(member)
        rando_mems = random.sample(beta_testers,5)
        for member in rando_mems:
            if "beta bot tester" in [r.name.lower() for r in member.roles]:
                temp += member.name + ", "

        string += temp[:-2] +  " and " + str(len(beta_testers) - 5) + " others!"
        #string += "\n\n----------------------------------------------------------\n\n"

        return string

    @commands.command(name = 'version')
    async def version_command(self,ctx):
        embedVar = discord.Embed(title="📔  Versions  📔", description="Bot Version :" + self.bot.bot_version + "\n\nDatabase Version: " + self.bot.db_version, color=0xFFA500)
        embedVar.set_footer(text = "For any questions/concerns please visit the official TheKWitt server! https://discord.gg/ZNpCNyNubU")
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"version command send")

    @version_command.error
    async def version_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass
    
    @commands.command(name = 'backstory')
    async def backstory_command(self,ctx):
        embedVar = discord.Embed(title="📖  The Cracklefest Scramble  📖", description="""In the land of Coneyford, Jethro the ruler of the land was excited to once again host a glorious event for his people, the Conoras. They call this event, Cracklefest. Every year around this time, everyone designs and crafts perfectly eggsquisite eggs to share. A holiday of genuine friendship and Renaissance.\n\nHowever, this year, the evil being known as the crimson wizard emerges from his realm and casts a mighty spell covering Coneyford! The storm caused the whole continent to morph and corrupt into terrible things! But most importantly, the storm scrambled all the eggs away from the conoras which left thousands of eggs placed all around Coneyford.\n\nWith eggs everywhere, it was uncertain that they were all able to be collected in time. Out of desperation, Jethro hired the people of **""" + ctx.guild.name + """** to find all the eggs and save Cracklefest!\n\n⠀""", color=0xFF7878)
        embedVar.add_field(name="The Objective",value="**It is your job to collect as many eggs as you can before the end of the month.\n\nYou can collect eggs in six different lands that you unlock by upgrading your basket. The basket holds a special power to repel the storm, allowing people to explore that area. You can also collect collectible eggs, there are five in each land.\n\nEgg clusters can also be found spawned in the server. They can hold alot of eggs at once with no cooldown attached to them!.\n\nThe person with the most eggs wins a role called Cracklefest Savior! People who find all the collectible eggs win a rolled Cracklefest Collector!**")
        embedVar.set_footer(text = "To change the server settings for commands and hearts, check out " + self.bot.prefix + "setsetting!")
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"backstory command send!")

    @backstory_command.error
    async def backstory_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass

    @commands.command(name = 'serverstats')
    async def serverstats_command(self,ctx):
        embedVar = discord.Embed(title="📖  " + ctx.guild.name + "'s Stats  📖", description="", color=0xFF7878)
        stats = await self.bot.pg_con.fetchrow("SELECT * FROM server_stats WHERE Guild_ID = $1",ctx.guild.id)
        embedVar.add_field(name="Eggs Collected",value = str(stats['eggs_collected']) + " Eggs")
        embedVar.add_field(name="Eggs Sold",value = str(stats['eggs_sold']) + " Eggs")
        embedVar.add_field(name="Trades Accepted",value = str(stats['trades_count']) + " Trades")
        lottery_stats = stats['lottery_results']
        embedVar.add_field(name="Lottery Cards",value = str(lottery_stats[1]) + " Won\n" + str(lottery_stats[0]) + " Lost")
        embedVar.add_field(name="Mailbox Mail Count",value = str(stats['mailbox_openings']) + " Pieces of Mail")
        embedVar.add_field(name="Clusters Spawned",value = str(stats['cluster_spawns']) + " Egg Clusters")
        embedVar.add_field(name="Server Level",value = "Level " + str(stats['upgrades']))
        explore_stats = stats['areas_explored']
        embedVar.add_field(name="Areas Explored",value = "The Coney Grounds - Visited " + str(explore_stats[0]) + " Times\n" + "The Hulking Fields - Visited " + str(explore_stats[1]) + " Times\n" + "The Woodland Valley - Visited " + str(explore_stats[2]) + " Times\n" + "The Oracle Rivers - Visited " + str(explore_stats[3]) + " Times\n" + "The Ethereal Garden - Visited " + str(explore_stats[4]) + " Times\n" + "The Crimson Grove - Visited " + str(explore_stats[5]) + " Times\n" + "The Arcane Void - Visited " + str(explore_stats[6]) + " Times\n",inline = False)
        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
        purr = settings['purification_count']
        default = settings['default_server_settings']
        embedVar.add_field(name="Area Donation Tracker",value = "The Coney Grounds - " + str(purr[0]) + "/" + default[2] + " Eggs Donated\n" + "The Hulking Fields - " + str(purr[1]) + "/" + default[2] + " Eggs Donated\n" + "The Woodland Valley - " + str(purr[2]) + "/" + default[2] + " Eggs Donated\n" + "The Oracle Rivers - " + str(purr[3]) + "/" + default[2] + " Eggs Donated\n" + "The Ethereal Garden - " + str(purr[4]) + "/" + default[2] + " Eggs Donated\n" + "The Crimson Grove - " + str(purr[5]) + "/" + default[2] + " Eggs Donated\n")
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"server stats command send!")

    @serverstats_command.error
    async def serverstats_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass

    @commands.command(name = 'donationgoaltracker')
    async def donation_command(self,ctx):
        settings = await self.bot.pg_con.fetchrow("SELECT * FROM guild_settings WHERE Guild_ID = $1",ctx.guild.id)
        purr = settings['purification_count']
        default = settings['default_server_settings']
        string = "The Coney Grounds - " + str(purr[0]) + "/" + default[2] + " Eggs Donated\n" + "The Hulking Fields - " + str(purr[1]) + "/" + default[2] + " Eggs Donated\n" + "The Woodland Valley - " + str(purr[2]) + "/" + default[2] + " Eggs Donated\n" + "The Oracle Rivers - " + str(purr[3]) + "/" + default[2] + " Eggs Donated\n" + "The Ethereal Garden - " + str(purr[4]) + "/" + default[2] + " Eggs Donated\n" + "The Crimson Grove - " + str(purr[5]) + "/" + default[2] + " Eggs Donated\n"
        embedVar = discord.Embed(title="📖  " + ctx.guild.name + "'s Donations  📖", description=string, color=0xFFFF87)
        await extra_functions.send_embed_ctx(self.bot,ctx,embedVar,300,"donation goal command send!")

    @donation_command.error
    async def donation_command_error(self,ctx,error):
        if isinstance(error, commands.BotMissingPermissions):
            pass

    def time_emoji(self,seconds):
        if seconds > 600: # More than 10 min
            return "🕚"
        elif seconds > 540: # 10 min
            return "🕙"
        elif seconds > 480: # 9 min
            return "🕘"
        elif seconds > 420: # 8 min
            return "🕗"
        elif seconds > 360: # 7 min
            return "🕖"
        elif seconds > 300: # 6 min
            return "🕕"
        elif seconds > 240: # 5 min
            return "🕔"
        elif seconds > 180: # 4 min
            return "🕓"
        elif seconds > 120: # 3 min
            return "🕒"
        elif seconds > 60: # 2 min
            return "🕑"
        elif seconds >= 0: # 1 min
            return "🕐"
        elif seconds < 0: # 0 min
            return "🕛"

def setup(bot):
    bot.add_cog(Info_Profile(bot))