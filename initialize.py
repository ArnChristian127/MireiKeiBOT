#MirekeiBOT
#coded by Arn Christian (MireiKei)
import discord, requests, random, asyncio
from discord.ext import commands
from io import BytesIO
from node import node
node()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Tenor GIF API
tenor_apikey = "AIzaSyB_PYY4JLesrNCh4hDYm4F0yo5mze74P2g"
tenor_limit = 5
tenor_ckey = "mirei_kei"

#creating a random gif function as well as sending it to the user
def tenorRandomGIF(apikey, query, limit, ckey):
    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, apikey, ckey,  limit))
    if r.status_code == 200:
        data = r.json()
        gifs = [result["media_formats"]["gif"]["url"] for result in data["results"]]
        if gifs:
            random_gif = random.choice(gifs)
            return random_gif
        else:
            return None

#creating a virtual affection that sends the GIF acording
#to what kind of physical you send to that person
async def physicalVirtual(ctx, user_id, query, title):
    try:
        mention_id = f"{user_id}"
        mention_bot = "<@1313391880993509386>"
        url = tenorRandomGIF(tenor_apikey, query, tenor_limit, tenor_ckey)
        response = requests.get(url)
        response.raise_for_status()
        file = discord.File(BytesIO(response.content), filename=url.split("/")[-1])
        if mention_id == mention_bot:
            await ctx.send(f"**That's so sweet >_<**", file=file)
        else:
            await ctx.send(f"**{title}** {mention_id}", file=file)
    except:
        await ctx.send("Connection lost, please try again")

@bot.command(name="query")
async def query(ctx):
    await ctx.send("**Command List**")
    helpList = [
        "**fight** - fighting with other user \n"
        "**query** - lists of the commands \n"
        "**pat** - patting the mention person \n"
        "**hug** - hugging the mention person \n"
        "**kiss** - kissing the mention person \n"
    ]
    for i in helpList:
        await ctx.send(f"{i}")

async def fightGIF(ctx):
    try:
        url = tenorRandomGIF(tenor_apikey, "anime punch", 10, tenor_ckey)
        response = requests.get(url)
        response.raise_for_status()
        file = discord.File(BytesIO(response.content), filename=url.split("/")[-1])
        await ctx.send(file=file)
    except:
        await ctx.send("Connection lost, please try again")

def randomDamage():
    damage = [5, 15, 40]
    rand = random.choice(damage)
    return rand

async def attackDisplay(ctx):
    if randomDamage() == 40:
        await ctx.send("**What a critical damage!!**")
    else:
        await ctx.send("**Punch!!**")

#creating a figthing command that allows to fight with two users
@bot.command(name="fight")
async def duelFight(ctx, user: discord.User):
    flag = False
    if user.bot:
        return
    
    if ctx.author.mention in ctx.message.content:
        await ctx.send("You cannot fight to your self loser.")
    else:
        await ctx.send(f"{user.mention} do you accept the challenge from {ctx.author.mention} **yes** or **no**")
        def check_response(msg):
            return (
                msg.author == user
                and msg.channel == ctx.channel
                and (msg.content.lower() or msg.content.upper()) in ['yes', 'no']
            )
        try:
            response = await bot.wait_for('message', timeout=25.0, check=check_response)
            if response.content.lower() == 'yes' or response.content.upper() == 'yes':
                flag = True
            elif response.content.lower() == 'no' or response.content.upper() == 'no':
                await ctx.send(f"{user.mention} your so weak to refuse the duel")
        except asyncio.TimeoutError:
            await ctx.send(f"{user.mention}, you didn't respond in time!")
    
    if flag == True:
        core = True
        winner = False
        getUserWinner = None
        your_lp = 100
        opponent_lp = 100
        while True:
            if your_lp <= 0:
                your_lp = 0
                getUserWinner = user.mention
                winner = True
                break
            elif opponent_lp <= 0:
                opponent_lp = 0
                getUserWinner = ctx.author.mention
                winner = True
                break

            await ctx.send(f"{ctx.author.mention} **Life Points**: {your_lp} % \n"
            f"{user.mention} **Life Points**: {opponent_lp} % \n"
            "Type **attack** to attack your opponent \n")
            if core:
                try:
                    await ctx.send(f"{user.mention} your turn.")
                    msg = await bot.wait_for('message', timeout=25.0, check=lambda m: m.author == user and m.channel == ctx.channel)
                    if msg.content.lower() == 'attack':
                        your_lp -= randomDamage()
                        await attackDisplay(ctx)
                        await fightGIF(ctx)
                    else:
                        await ctx.send("Please type **attack** or **block**")
                        continue
                except asyncio.TimeoutError:
                    await ctx.send(f"{user.mention}, you didn't respond in time! So the winner is {ctx.author.mention}")
                    break
            else:
                try:
                    await ctx.send(f"{ctx.author.mention} your turn.")
                    msg = await bot.wait_for('message', timeout=25.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                    if msg.content.lower() == 'attack':
                        opponent_lp -= randomDamage()
                        await attackDisplay(ctx)
                        await fightGIF(ctx)
                    else:
                        await ctx.send("Please type **attack**")
                        continue
                except asyncio.TimeoutError:
                    await ctx.send(f"{user.mention}, you didn't respond in time! **So the winner is {user.mention}!!**")
                    break
            core = not core

        if winner == True:
            await ctx.send(f"{getUserWinner} **is the winner!!**")

@bot.command(name="pat")
async def pat(ctx, id):
    await physicalVirtual(ctx, id, "anime pat", "Pats You!!")

@bot.command(name="hug")
async def hug(ctx, id):
    await physicalVirtual(ctx, id, "anime hug", "Hugs You!!")

@bot.command(name="kiss")
async def kiss(ctx, id):
    await physicalVirtual(ctx, id, "anime kiss", "Kiss You!!")

bot.run("MTMxMzM5MTg4MDk5MzUwOTM4Ng.GfHiez.hTS6oNXbaxFxgluSzTVsjwhdeoAZnxWf4liBqc")