#MirekeiBOT
#coded by Arn Christian (MireiKei)
import discord, requests, random, asyncio, json, sqlite3
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from discord.ext import commands
from io import BytesIO

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Tenor GIF API
tenor_apikey = "API KEY"
tenor_limit = 5
tenor_ckey = "mirei_kei"

#database from user when playin gambling
connect = sqlite3.connect("gambling-database.db")
cursor = connect.cursor()

def random_color():
    symbols = ["🔵", "🔴", "🟡"]
    weights = [0.1, 0.3, 0.6]
    return random.choices(symbols, weights=weights, k=1)[0]

@bot.command(name="gambling")
async def gamble(ctx):
    #adding the user if it's was the first time
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id = ?)", (ctx.author.id, ))
    check_exists = cursor.fetchone()[0] == 1
    if not check_exists:
        cursor.execute("INSERT INTO users (id, name, money, token) VALUES (?, ?, ?, ?)", (ctx.author.id, ctx.author.name, 1000, 100))
        await ctx.send(f"{ctx.author.mention} **Since this is your first time, you got 100 tokens :D!**")
        connect.commit()

    get_coin = 0
    while True:
        cursor.execute("SELECT * FROM users WHERE id = ?", (ctx.author.id,))
        res = cursor.fetchone()
        def check(reaction, user):
            return (user == ctx.author 
                and reaction.message.id == message.id
                and (str(reaction.emoji) == "🤑" or str(reaction.emoji) == "❎")
            )
        await ctx.send(
            "**Reward list for this season: ** \n"
            f"🔵**: $1000** \n"
            f"🔴**: $500** \n"
            f"🟡**: $100** \n"
        )
        message = await ctx.send(
            f"**Name**: ``{res[1]} 🤖`` \n"
            f"**Money**: ``${res[2]} 💸`` \n"
            f"**Tokens**: ``{res[3]} 🪙`` \n"
            f"```React [🤑] to start pull or [❎] to exit.```"
        )
        await message.add_reaction("🤑")
        await message.add_reaction("❎")
        try:
            check_token = 0
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "🤑":
                if res[3] <= 0:
                    await ctx.send("**You don't have for pull sadgee**")
                else:
                    spin = await ctx.send("**Spinning...**")
                    slot_1 = random_color()
                    slot_2 = random_color()
                    slot_3 = random_color()
                    await spin.edit(content=f"{slot_1} {slot_2} {slot_3}")
                    if (slot_1 == "🔵" and slot_2 == "🔵" and slot_3 == "🔵"):
                        get_coin = 1000
                        await ctx.send(f"**You got {get_coin} coins!**")
                    elif (slot_1 == "🔴" and slot_2 == "🔴" and slot_3 == "🔴"):
                        get_coin = 500
                        await ctx.send(f"**You got {get_coin} coins!**")
                    elif (slot_1 == "🟡" and slot_2 == "🟡" and slot_3 == "🟡"):
                        get_coin = 100
                        await ctx.send(f"**You got {get_coin} coins!**")
                    else:
                        await ctx.send("**Awww dangg itt!!! 💸**")
                    set_money = res[2] + get_coin
                    set_token = res[3] -1
                    cursor.execute("UPDATE users SET money = ?, token = ? WHERE id = ?", (set_money, set_token, ctx.author.id))
                    connect.commit()     
            elif str(reaction.emoji) == "❎":
                await ctx.send("**Thank you for playing!**")
                break
        except asyncio.TimeoutError:
            print("Time out")
            break

#command that talks to mirei kei bot
model = SentenceTransformer('all-MiniLM-L6-v2')
def knowledge_base():
    try:
        with open('mirei_memory.json', 'r', encoding='utf-8') as file:
            datas = json.load(file)
    except FileNotFoundError:
        datas = {}
    return datas

@bot.command(name="mirei")
async def mirei(ctx, *, insert: str):
    if not knowledge_base():
        await ctx.send("Memory is empty.")
        return  
    insert_embedding = model.encode([insert])
    keys = list(knowledge_base().keys())
    keys_embeddings = model.encode(keys)
    similarities = cosine_similarity(insert_embedding, keys_embeddings)[0]
    max_idx = similarities.argmax()
    max_similarity = similarities[max_idx]
    THRESHOLD = 0.6 
    if max_similarity >= THRESHOLD:
        matched_key = keys[max_idx]
        await ctx.send(knowledge_base()[matched_key])
    else:
        await ctx.send(f"{get_related_info(insert)}")

def get_related_info(query: str) -> str:
    embeddings = model.encode(list(knowledge_base().keys()))
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    best_match_idx = similarities.argmax()
    if similarities[best_match_idx] > 0.5:
        return knowledge_base()[list(knowledge_base().keys())[best_match_idx]]
    else:
        return "I'm still under of training, maybe I can learn that in the future. <3"
    

#Gemini API
@bot.command(name="talk")
async def talk(ctx, *, insert: str):
    genai.configure(api_key="API KEY")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(insert)
    max_length = 2000
    if len(response.text) > max_length:
        await ctx.send("I can't generate too much sentences, please minimalize it.")
    else:
        await ctx.send(response.text)


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

#the command searcher
@bot.command(name="query")
async def query(ctx):
    await ctx.send("**Command List**") 
    helpList = [
        "**mirei** - talk to personal bot \n"
        "**talk** - talk to GPT bot \n"
        "**fight** - fighting with other user \n"
        "**query** - lists of the commands \n"
        "**pat** - patting the mention person \n"
        "**hug** - hugging the mention person \n"
        "**kiss** - kissing the mention person \n"
    ]
    for i in helpList:
        await ctx.send(f"{i}")

#this is for fight command that sends GIF
async def fightGIF(ctx):
    try:
        url = tenorRandomGIF(tenor_apikey, "anime punch", 10, tenor_ckey)
        response = requests.get(url)
        response.raise_for_status()
        file = discord.File(BytesIO(response.content), filename=url.split("/")[-1])
        await ctx.send(file=file)
    except:
        await ctx.send("Connection lost, please try again")

#making a simple random damage altho its kinda
#weird method way (might update in the future)
def randomDamage():
    damage = [5, 15, 40]
    rand = random.choice(damage)
    return rand

#display out after attacking
async def attackDisplay(ctx):
    if randomDamage() == 40:
        await ctx.send("**What a critical damage!!**")
    else:
        await ctx.send("**Punch!!**")

#creating a figthing command that allows to fight with two users
@bot.command(name="fight")
async def duelFight(ctx, user: discord.User):
    #creating a boolean set and getter
    flag = False
    #cannot be respond by bot
    if user.bot:
        await ctx.send("**You cannot fight me im just a BOT dumbass**")
        return
    
    #checks if the typer (mention) was mention so it can't attack himself
    if ctx.author.mention in ctx.message.content:
        #display an output
        await ctx.send("You cannot fight to your self loser.")
    else:
        #otherwise mention the other user to accept the challenge
        await ctx.send(f"{user.mention} do you accept the challenge from {ctx.author.mention} **yes** or **no**")
        def check_response(msg):
            return (
                msg.author == user
                and msg.channel == ctx.channel
                #check if the other user type the option
                and (msg.content.lower() or msg.content.upper()) in ['yes', 'no']
            )
        try:
            #creating a duration within 25 seconds if the user doesn't reponse
            #it will eventually go to exception
            response = await bot.wait_for('message', timeout=25.0, check=check_response)
            if response.content.lower() == 'yes' or response.content.upper() == 'yes':
                #gets the true if the user say yes
                flag = True
            elif response.content.lower() == 'no' or response.content.upper() == 'no':
                await ctx.send(f"{user.mention} your so weak to refuse the duel")
        except asyncio.TimeoutError:
            await ctx.send(f"{user.mention}, you didn't respond in time!")
    #if flag was triggerd
    if flag == True:
        #creating a handle loop
        core = True
        winner = False
        getUserWinner = None
        #set life points to both players
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
                        await ctx.send("Please type **attack**")
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

bot.run("API KEY")
