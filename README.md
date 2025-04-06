# 🤖 MemeBot - Your Personal Reddit Meme Butler 🎩

Tired of manually scavenging Reddit for fresh memes? Let MemeBot be your loyal servant - fetching, watermarking, and delivering spicy memes straight to your Telegram chat! *"Your memes, my lord, as you command!"* (bows dramatically)

## 🚀 Installation - The "I Promise It's Easy" Guide

1. **Clone this repo** (unless you enjoy typing everything manually, you masochist):
```bash
git clone https://github.com/LilyAshford/redditmemebot.git
cd redditmemebot
```

2. **Install dependencies** (warning: may cause sudden excitement):
```bash
pip install -r requirements.txt
```
*Pro tip: If this fails, try turning it off and on again. Just kidding - check Python version (3.8+ required).*

3. **Configure your bot** (the "adulting" part):
```bash
cp config.py config.py
```
Now edit `config.py` like you're hacking the mainframe (but really just paste your API keys).

## 🔑 Configuration - Secrets Management 101

Your `config.py` should look like this (but with actual keys, unless you enjoy error messages):

```python
# Reddit API (get these from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID = "your_id_here" # Like a username, but more cryptic
REDDIT_CLIENT_SECRET = "your_secret_here" # Shh... don't tell anyone!
REDDIT_USER_AGENT = "MemeButler/1.0 by YourRedditUsername" # Be creative!

# Telegram (get token from @BotFather)
TELEGRAM_BOT_TOKEN = "123:abc" # Your bot's DNA

# Optional (for error reports)
ADMIN_CHAT_ID = 1234567890 # Your personal Bat-Signal for errors
```

*Remember:* Never commit real keys to GitHub unless you want your bot to become an open-source pet project for hackers. 🐱‍💻

## 🧠 Features - Why This Bot Doesn't Suck

| Feature | Description | Emotion Guaranteed |
|---------|-------------|---------------------|
| 🔥 Hot Memes | Fresh from Reddit's oven | 😂 → 🤣 |
| 🎨 Auto-Watermark | Your brand on every meme | 😎 (so professional!) |
| 📊 Trend Analysis | See what meme lords are loving | 🤓 (data nerd mode) |
| 💾 Database | Saves memes like a digital hoarder | 🐿️ (squirrel instincts) |

## 🏃‍♂️ Running - The Moment of Truth

```bash
python main.py
```

*Expected output:*
1. Bot wakes up (☕)
2. Connects to Reddit (🤝)
3. Starts serving memes (🎪)

If nothing happens, check:
- Did you add API keys? 🔑
- Is your internet working? 🌐
- Did you sacrifice a USB stick to the tech gods? 🧙‍♂️

## 🛠 Troubleshooting - Because Nothing Works on First Try

**Error:** `Reddit API not working`
- Did you wait 5 minutes after creating Reddit app? They're slower than dial-up
- Check your user agent format: `"AppName/1.0 by YourRedditUsername"`

**Error:** `Telegram bot not responding`
- Did you actually talk to @BotFather or just stare at it menacingly?
- Bot started? Check with `/start` in Telegram

## 🤝 Contributing - Join the Meme Revolution!

Found a bug? Have an idea?
1. Fork it (🍴)
2. Fix it (🔧)
3. Pull request it (🎣)

*First-time contributors get:*
☑️ Virtual high-five
☑️ Eternal gratitude
☑️ My undying love (terms and conditions apply)

## 📜 License - The Fine Print

MIT License - Meaning:
✅ Do whatever you want
✅ No liability
❌ Don't blame me if your group chat becomes 98% memes

---

*Final note:* This bot may cause excessive laughter, increased productivity loss, and sudden urges to send memes at 3AM. Use responsibly. 🚀