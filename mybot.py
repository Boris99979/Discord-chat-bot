import os
import re
import asyncio
import random
import discord
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- Load personality from file ---
with open("personality.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# --- Load cat GIFs from file ---
with open("cat_gifs.txt", "r", encoding="utf-8") as f:
    CAT_GIFS = [line.strip() for line in f if line.strip()]

# --- Setup Gemini ---
gemini = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"

# --- Config ---
BULLY_TARGETS = [444075681740226573, 357532921021595648, 412351662796046343]  # Add more IDs separated by commas
BULLY_REACTIONS = ["😼", "😾", "🖕"]
HISS_MESSAGES = ["HSSSSSS", "*hisses*", "HISSSS 😾", "*arches back and hisses*"]
CONSOLE_CHANNEL_ID = [1506582343891161168, 779846116220600321, 1505119971607580785]
ALLOWED_CHANNEL_ID = [1506582343891161168, 779846116220600321, 1505119971607580785]
HISTORY_LIMIT = 10

# --- Setup Discord ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

async def get_channel_history(message):
    """Fetch the last HISTORY_LIMIT messages and return text + user map {name: id}."""
    history = []
    user_map = {}
    async for msg in message.channel.history(limit=HISTORY_LIMIT + 1, before=message):
        if msg.content:
            history.append(f"{msg.author.display_name}: {msg.content}")
            user_map[msg.author.display_name.lower()] = msg.author.id
            user_map[msg.author.name.lower()] = msg.author.id
    history.reverse()
    return "\n".join(history), user_map

def resolve_mentions(text, guild):
    """Convert @name in text to Discord mention <@ID>."""
    def replace(match):
        name = match.group(1).lower()
        if guild:
            for member in guild.members:
                if member.display_name.lower() == name or member.name.lower() == name:
                    return f"<@{member.id}>"
        return match.group(0)
    return re.sub(r'@(\w+)', replace, text)

async def console_input():
    loop = asyncio.get_event_loop()
    await client.wait_until_ready()

    # Fetch all console channels
    channels = []
    for cid in CONSOLE_CHANNEL_ID:
        try:
            ch = await client.fetch_channel(cid)
            channels.append(ch)
        except Exception as e:
            print(f"Could not find channel {cid}: {e}")

    if not channels:
        print("No valid console channels found.")
        return

    current = channels[0]
    guild = current.guild

    print("\nConsole ready! Commands:")
    print("  'switch <number>' — switch active channel")
    print("  '@username message' — ping someone")
    print("  'quit' — stop the bot")
    for i, ch in enumerate(channels):
        print(f"  [{i+1}] #{ch.name}")
    print(f"\nCurrently sending to #{current.name}\n")

    while True:
        text = await loop.run_in_executor(None, input, f"[#{current.name}] You > ")
        stripped = text.strip()

        if stripped.lower() == "quit":
            await client.close()
            break
        elif stripped.lower().startswith("switch "):
            try:
                idx = int(stripped.split(" ", 1)[1]) - 1
                if 0 <= idx < len(channels):
                    current = channels[idx]
                    guild = current.guild
                    print(f"Switched to #{current.name}")
                else:
                    print(f"Invalid number. Pick 1-{len(channels)}")
            except ValueError:
                print("Usage: switch <number>")
        elif stripped:
            resolved = resolve_mentions(stripped, guild)
            await current.send(resolved)

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")
    asyncio.create_task(console_input())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # React only in the allowed channels
    if message.channel.id not in ALLOWED_CHANNEL_ID:
        return

    # 10% chance to react to any message with a context-fitting emoji
    if message.content.strip() and random.random() < 0.5:
        try:
            emoji_response = await asyncio.to_thread(
                gemini.models.generate_content,
                model=MODEL,
                contents=f"React to this message with a single fitting emoji. Reply with ONLY the emoji, nothing else: {message.content}"
            )
            emoji = emoji_response.text.strip()
            if emoji:
                await message.add_reaction(emoji)
        except Exception:
            pass  # Silently ignore if it fails

    # Random reactions to bully targets
    if message.author.id in BULLY_TARGETS:
        if random.random() < 0.6:
            action = random.choice(["emoji", "hiss"])
            if action == "emoji":
                await message.add_reaction(random.choice(BULLY_REACTIONS))
            else:
                await message.channel.send(random.choice(HISS_MESSAGES))

    # Only reply when mentioned
    if client.user not in message.mentions:
        return

    text = message.content.replace(f"<@{client.user.id}>", "").strip()

    if not text:
        await message.reply("Meow? Ask me something~ 😼")
        return

    if text.lower() == "reset":
        await message.reply("*forgets everything* Meow~ 🐱")
        return

    # GIF command
    if text.lower() in ["gif", "cat gif", "send gif"]:
        await message.reply(random.choice(CAT_GIFS))
        return

    # Fetch channel history + user map
    channel_context, user_map = await get_channel_history(message)

    # Add the message author to the user map too
    user_map[message.author.display_name.lower()] = message.author.id
    user_map[message.author.name.lower()] = message.author.id

    # Build user list so Gemini knows how to mention people
    user_list = "\n".join([f"{name} -> <@{uid}>" for name, uid in user_map.items()])

    # Build full prompt
    full_prompt = ""
    if user_list:
        full_prompt += f"Users you can mention (use exactly as shown):\n{user_list}\n\n"
    if channel_context:
        full_prompt += f"Recent chat history:\n{channel_context}\n\n"
    full_prompt += f"{message.author.display_name}: {text}"

    async with message.channel.typing():
        retries = 3
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(
                    gemini.models.generate_content,
                    model=MODEL,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=3000,
                    )
                )

                reply = response.text

                if len(reply) > 1900:
                    chunks = [reply[i:i+1900] for i in range(0, len(reply), 1900)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await message.reply(chunk)
                        else:
                            await message.channel.send(chunk)
                else:
                    await message.reply(reply)

                # 20% chance to also send a random cat GIF with the reply
                if random.random() < 0.55:
                    await message.channel.send(random.choice(CAT_GIFS))
                break

            except Exception as e:
                error = str(e)
                if "503" in error and attempt < retries - 1:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                await message.reply(f"Something went wrong: `{error}`")

client.run(os.getenv("DISCORD_BOT_TOKEN"))
