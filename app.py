import discord
from discord.ext import commands
import datetime
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1234')
DB_NAME = os.getenv('DB_NAME', 'hammer')
DB_CHARSET = 'utf8mb4'

def get_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset=DB_CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(e)
        return None

def create_tables():
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS counts (
                    user_id VARCHAR(20) PRIMARY KEY,
                    count INT NOT NULL DEFAULT 0
                )
                ''')
            connection.commit()
            print("테이블 생성")
        except Exception as e:
            print(e)
        finally:
            connection.close()

def get_user_count(user_id):
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT count FROM counts WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    return result['count']
                return 0
        except Exception as e:
            print(e)
        finally:
            connection.close()
    return 0

def update_user_count(user_id, count):
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO counts (user_id, count) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE count = %s
                """
                cursor.execute(sql, (user_id, count, count))
            connection.commit()
            return True
        except Exception as e:
            print(e)
        finally:
            connection.close()
    return False

@bot.event
async def on_ready():
    create_tables()
    print('굿')
    
@bot.command(name='심판')
@commands.has_permissions(moderate_members=True)  
async def judge(ctx, member: discord.Member, *, reason: str = "없"):
    user_id = str(member.id)
    
    count = get_user_count(user_id) + 1
    
    update_user_count(user_id, count)
    
    if count <= 3:
        timeout_duration = datetime.timedelta(minutes=1) 
        duration_text = "60초"
    else:
        timeout_duration = datetime.timedelta(weeks=1) 
        duration_text = "1주일"
    
    try:
        await member.timeout(timeout_duration, reason=reason)
        
        try:
            dm_embed = discord.Embed(
                title="✉️ 통지서",
                description=f"당신은 **{ctx.guild.name}** 서버에서 {duration_text}동안 타임아웃 되었습니다.",
                color=0xFF5733
            )
            dm_embed.add_field(name="사유", value=reason, inline=True)
            dm_embed.add_field(name="전과", value=f"{count}회", inline=True)
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(f"{member.mention}에게 메시지가 안보내져요")
        except Exception as e:
            print(e)
        
        embed = discord.Embed(
            title="⚖️ 처벌",
            description=f"전과 {count}범 {member.mention}를 {duration_text}동안 구금했습니다.",
            color=0xFF5733
        )
        embed.add_field(name="사유", value=reason, inline=True)
        embed.set_footer(text=f"by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("봇 권한 이슈")
    except Exception as e:
        await ctx.send(e)

@bot.command(name='석방')
@commands.has_permissions(moderate_members=True)
async def release(ctx, member: discord.Member):
    user_id = str(member.id)
    count = get_user_count(user_id)

    try:
        await member.timeout(None)
        
        embed = discord.Embed(
            title="🕊️ 석방",
            description=f"전과 {count}범 {member.mention}를 석방했습니다.",
            color=0x2ECC71
        )
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
