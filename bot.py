import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

load_dotenv()
DISCORD_API = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print("ICS Merger bot is running")

@bot.command()
async def example(ctx):
    await ctx.send("**Sample Text File Format:**\n\n"
        "Each line in the .txt file should contain a single calendar URL.\n\n"
        "For example:\n"
        "https://example.com/calendar1\n"
        "https://example.com/calendar2\n"
        "https://example.com/calendar3\n\n"
        "Make sure to save your calendar URLs in this format and send them in a .txt file.")

@bot.command(name='help')
async def custom_help(ctx):
    help_message = (
        "**Welcome to the Calendar Bot!**\n\n"
        "Here are the commands you can use:\n"
        "• `!merge` - Initiate the bot and get instructions to send a .txt file with calendar URLs.\n"
        "• `!example` - Receive a sample format of the .txt file for calendar URLs.\n"
        "• `!help` - Display this help message.\n\n"
        "If you need further assistance, feel free to ask!"
    )
    await ctx.send(help_message)

@bot.command()
async def merge(ctx):
    if len(ctx.message.attachments) > 0:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith('.txt'):
            repo = "apsh0tDev/ICSMerger_calendars"
            now = datetime.now()
            formatted_date_time = now.strftime('%Y%m%d%H%M')
            txt_filename = f"merged_calendar_{formatted_date_time}.txt"
            await ctx.send("📂 Got your file! Please wait a few moments while the merge is completed. ⌛")
            

        else:
            await ctx.send("Format not supported. Please send a valid .txt file")
    else:
        await ctx.send("No file attached! Please type !merge and attach a .txt file containing the list of URLs.")

def startBot():
    bot.run(DISCORD_API)

if __name__ == "__main__":
    startBot()