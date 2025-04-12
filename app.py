import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import create_tables
from commands import Judge, Release, Clean

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')

@bot.event
async def on_ready():
    create_tables()
    print('굿')

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

async def setup():
    await bot.add_cog(Judge(bot))
    await bot.add_cog(Release(bot))
    await bot.add_cog(Clean(bot))

bot.run(TOKEN) 