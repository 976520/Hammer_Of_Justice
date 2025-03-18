import discord
from discord.ext import commands
import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)

counts = {}

DATABASE = 'counts.json'

def load_counts():
    global counts
    if os.path.exists(DATABASE):
        try:
            with open(DATABASE, 'r', encoding='utf-8') as f:
                counts = json.load(f)
        except Exception as e:
            print(e)

def save_counts():
    try:
        with open(DATABASE, 'w', encoding='utf-8') as f:
            json.dump(counts, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)

@bot.event
async def on_ready():
    load_counts()
    print('굿')
    
    
@bot.command(name='심판')
@commands.has_permissions(moderate_members=True)  
async def judge(ctx, member: discord.Member, *, reason: str = "없"):
    global counts
    
    user_id = str(member.id)
    
    if user_id not in counts:
        counts[user_id] = 0
    
    counts[user_id] += 1
    
    count = counts[user_id]
    if count <= 3:
        timeout_duration = datetime.timedelta(minutes=1) 
        duration_text = "60초"
    else:
        timeout_duration = datetime.timedelta(weeks=1) 
        duration_text = "1주일"
    
    try:
        await member.timeout(timeout_duration, reason=reason)
        
        embed = discord.Embed(
            title="⚖️ 처벌",
            description=f"전과 {count}범 {member.mention}를 {duration_text}동안 구금했습니다.",
            color=0xFF5733
        )
        embed.add_field(name="사유", value=reason, inline=True)
        embed.set_footer(text=f"by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
        save_counts()
        
    except discord.Forbidden:
        await ctx.send("봇 권한 이슈")
    except Exception as e:
        await ctx.send(e)

@bot.command(name='석방')
@commands.has_permissions(moderate_members=True)
async def release(ctx, member: discord.Member):

    try:
        await member.timeout(None)
        
        embed = discord.Embed(
            title="🕊️ 석방",
            description=f"전과 {count}범 {member.mention}를 석방했습니다.",
            color=0x2ECC71
        )
        user_id = str(member.id)
        count = counts.get(user_id, 0)
        embed.set_footer(text=f"by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("봇 권한 이슈")
    except Exception as e:
        await ctx.send(e)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'member':
            embed = discord.Embed(
                title="❌ 오류",
                description="멤버 파라미터 없음",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
        elif error.param.name == 'reason':
            embed = discord.Embed(
                title="❌ 오류",
                description="사유 파라미터 없음",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ 오류",
            description="멤버 낫파운드",
            color=0xE74C3C
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ 오류",
            description="권한 없음",
            color=0xE74C3C
        )
        await ctx.send(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))
