import discord
from discord.ext import commands
import datetime
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix='/', intents=intents)

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_CHARSET = 'utf8mb4'

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(e)
        return None

def create_tables():
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS counts (
                    user_id VARCHAR(20),
                    server_id VARCHAR(20),
                    count INT NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, server_id)
                )
                ''')
            connection.commit()
            print("테이블 생성")
        except Exception as e:
            print(e)
        finally:
            connection.close()
    else:
        print("DB연결 실패")

def get_user_count(user_id, server_id):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = "SELECT count FROM counts WHERE user_id = %s AND server_id = %s"
            cursor.execute(sql, (user_id, server_id))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result['count']
            return 0
        except Exception as e:
            print(e)
            return 0
        finally:
            connection.close()
    return 0

def update_user_count(user_id, server_id, count):
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO counts (user_id, server_id, count) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE count = %s
                """
                cursor.execute(sql, (user_id, server_id, count, count))
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
    server_id = str(ctx.guild.id)
    
    count = get_user_count(user_id, server_id) + 1
    
    update_user_count(user_id, server_id, count)
    
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
    server_id = str(ctx.guild.id)
    count = get_user_count(user_id, server_id)

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

@bot.command(name='청소')
@commands.has_permissions(manage_channels=True)
async def clean_channel(ctx, *, channel_name: str = None):
    try:
        original_channel = ctx.channel
        channel_to_delete = original_channel
        
        if channel_name:
            found_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
            if found_channel:
                channel_to_delete = found_channel
            else:
                embed = discord.Embed(
                    title="❌ 오류",
                    description=f"'{channel_name}' 채널을 찾을 수 없습니다.",
                    color=0xE74C3C
                )
                await ctx.send(embed=embed)
                return
        
        category = channel_to_delete.category
        position = channel_to_delete.position
        topic = channel_to_delete.topic
        slowmode_delay = channel_to_delete.slowmode_delay
        nsfw = channel_to_delete.is_nsfw()
        overwrites = channel_to_delete.overwrites
        
        embed = discord.Embed(
            title="🧹 채널 청소",
            description=f"채널 '{channel_to_delete.name}'을(를) 삭제하고 다시 생성합니다.",
            color=0x3498DB
        )
        await ctx.send(embed=embed)
        
        await channel_to_delete.delete(reason="더럽다 더러워")
        
        new_channel = await ctx.guild.create_text_channel(
            name=channel_to_delete.name,
            category=category,
            topic=topic,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            overwrites=overwrites,
            position=position,
            reason="더럽다 더러워"
        )
        
        embed = discord.Embed(
            title="✅ 청소 완료",
            description=f"채널이 성공적으로 청소되었습니다.",
            color=0x2ECC71
        )
        await new_channel.send(embed=embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ 오류",
            description="채널을 관리할 권한이 없습니다.",
            color=0xE74C3C
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ 오류",
            description=e,
            color=0xE74C3C
        )
        await ctx.send(embed=embed)

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

TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
bot.run(TOKEN)
