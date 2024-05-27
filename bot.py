import discord
import os
import io
from dotenv import load_dotenv
from discord.ext import commands, tasks
from merger import process_file
from uploader import upload_files_to_github
from fp.fp import FreeProxy

load_dotenv()
DISCORD_API = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
public_token = os.getenv("public_token")
proxy = FreeProxy(https=True).get()

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
            file_content = io.BytesIO(await attachment.read())
            await ctx.send("📂 Got your file! Please wait a few moments while the merge is completed. ⌛")
            file_result = await process_file(file=file_content, proxy=proxy)
            file_path = f"{file_result}"

            if os.path.exists(file_path):
                print(f"The file {file_path} was saved.")
                txt_filename = replace_extension(file_path=file_path)
                await attachment.save(txt_filename)
                upload = await upload_files_to_github(file_path, txt_filename, public_token)
                if upload == "Success":
                    merged_calendar_url = f"https://raw.githubusercontent.com/apsh0tDev/ICSMerger_calendars/master/{file_path}"
                    await ctx.send(f"Done! 👍 Here's your calendar: {merged_calendar_url}")
                elif upload == "Error":
                    await ctx.send(f"There was an error, please try again in a couple of minutes")


            else:
                print(f"Error storing the file {file_path}")


        else:
            await ctx.send("Format not supported. Please send a valid .txt file")
    else:
        await ctx.send("No file attached! Please type !merge and attach a .txt file containing the list of URLs.")

def startBot():
    bot.run(DISCORD_API)


def replace_extension(file_path):
    root, ext = os.path.splitext(file_path)
    if ext == ".ics":
        new_file_path = root + ".txt"
        return new_file_path
    else:
        return file_path

if __name__ == "__main__":
    startBot()