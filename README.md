# 😼 Meow Bot — Discord AI Cat

A Discord bot powered by **Google Gemini AI** with a chaotic cat personality. Replies when mentioned, reacts to messages, bullies specific users, and sends cat GIFs. No cap.

---

## ✨ Features

- 🐱 **Cat personality** — replies with meows, gen-z slang, and chaotic energy
- 🤖 **Gemini AI** — powered by Google's `gemini-2.5-flash` model
- 💬 **Mention to chat** — bot only responds when @mentioned
- 🧠 **Channel memory** — reads last 10 messages for context before replying
- 😼 **Bully mode** — randomly hisses at or reacts to specific users
- 🎭 **Emoji reactions** — reacts to messages with context-fitting emojis
- 🖼️ **Cat GIFs** — sends curated cat GIFs randomly or on demand
- 🖥️ **Console input** — send messages directly from your terminal
- 🔔 **Ping support** — bot and console can mention/ping users

---

## 🛠️ Setup

### Requirements
- Python 3.10+
- A Discord bot token — [Discord Developer Portal](https://discord.com/developers/applications)
- A Google Gemini API key — [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install google-genai
   ```
3. Copy `.env.example` to `.env` and fill in your keys:
   ```
   DISCORD_BOT_TOKEN=your_token_here
   GOOGLE_API_KEY=your_gemini_key_here
   ```
4. Run the bot:
   ```
   start.bat
   ```
   or
   ```
   python -X utf8 mybot.py
   ```

---

## ⚙️ Configuration

| File | Purpose |
|------|---------|
| `personality.txt` | Edit the bot's personality and system prompt |
| `cat_gifs.txt` | Add/remove Tenor GIF URLs (one per line) |
| `mybot.py` | Main bot config — channel IDs, bully targets, percentages |

### Key settings in `mybot.py`

```python
BULLY_TARGETS = [123456789]        # User IDs to bully
ALLOWED_CHANNEL_ID = [123456789]   # Channels the bot can talk in
CONSOLE_CHANNEL_ID = [123456789]   # Channels for console input
HISTORY_LIMIT = 10                 # How many messages to read for context
```

---

## 💬 Usage

| Action | How |
|--------|-----|
| Chat with bot | `@bot your message` |
| Get a cat GIF | `@bot gif` |
| Clear history | `@bot reset` |
| Console ping | Type `@username message` in terminal |
| Switch console channel | Type `switch <number>` in terminal |
| Stop bot | Type `quit` in terminal |

---

## 📁 Project Structure

```
mybot.py          — main bot (use this)
personality.txt   — bot personality/system prompt
cat_gifs.txt      — curated cat GIF list
start.bat         — launcher
.env              — your secret keys (never commit this)
```

---

## ⚠️ Notes

- Never share or commit your `.env` file
- Free tier Gemini works with `gemini-2.5-flash`
- Add your Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)
