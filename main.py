import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, TELEGRAM_BOT_TOKEN
from database import save_to_db, save_meme_to_db
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import telebot
from telebot import types
from PIL import Image, ImageDraw, ImageFont
import requests
import logging
from logging.handlers import RotatingFileHandler


matplotlib.use('Agg')
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [RotatingFileHandler('log.log', maxBytes = 5*1024*1024, backupCount = 3),
                logging.StreamHandler()]
)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
    )

nltk.download('stopwords')

user_states = {}

def clean_text(text):
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    words = text.split()
    words = [word for word in words if word not in stopwords.words('english')]
    return words

def analyze_trends(posts):
    all_words = []
    for post in posts:
        all_words.extend(clean_text(post['title']))
    return Counter(all_words).most_common(5)

def get_posts(subreddit_name, post_type='hot', limit=20):
    subreddit = reddit.subreddit(subreddit_name)

    if post_type == 'hot':
        posts = subreddit.hot(limit=limit)
    elif post_type == 'new':
        posts = subreddit.new(limit=limit)
    elif post_type == 'top':
        posts = subreddit.top(limit=limit)
    elif post_type == 'rising':
        posts = subreddit.rising(limit=limit)
    else:
        posts = subreddit.hot(limit=limit)

    result = []
    for post in posts:
        result.append({
            'title': post.title,
            'upvotes': post.score,
            'url': post.url,
            'subreddit': subreddit_name,
            'created_utc': post.created_utc,
            'is_image': any(ext in post.url.lower() for ext in ['.jpg', '.jpeg', '.png'])
            })
    return result

def plot_trends(trends):
    words = [item[0] for item in trends]
    counts = [item[1] for item in trends]

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)
    plt.title('Top Meme Trends')
    plt.xlabel('Words')
    plt.ylabel('Frequency')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def add_watermark(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code !=200:
            return None
        img = Image.open(BytesIO(response.content))
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        watermark = Image.new('RGBA', img.size, (0,0,0,0))

        draw = ImageDraw.Draw(watermark)

        try:
            font = ImageFont.truetype("arial.ttf", int(img.width / 25))
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", int(img.width / 25))
            except:
                font = ImageFont.load_default()

        text = "MemeBot"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        x = 20
        y = (img.height - text_height)//2

        padding = 5
        draw.rectangle(
            [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
            fill=(0, 0, 0, 100)
        )

        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x == 0 and offset_y == 0:
                    continue
        draw.text((x + offset_x, y + offset_y), text, font=font, fill=(0, 0, 0, 200))

        draw.text((x, y), text, font=font, fill=(255, 255, 255, 230))

        watermarked = Image.alpha_composite(img, watermark)

        buf = BytesIO()
        watermarked.save(buf, format='PNG')
        buf.seek(0)
        return buf

    except Exception as e:
        logging.info(f"Error adding watermark: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🔥 Hot posts')
    btn2 = types.KeyboardButton('🔍 Search by topic')
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "Hi! I'm a MemeBot. What do you wanna do?",
        reply_markup=markup
        )

@bot.message_handler(func=lambda message: message.text == '🔥 Hot posts')
def hot_posts_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Hot')
    btn2 = types.KeyboardButton('New')
    btn3 = types.KeyboardButton('Top')
    btn4 = types.KeyboardButton('Rising')
    btn5 = types.KeyboardButton('↩️ Back')
    markup.add(btn1, btn2, btn3, btn4, btn5)

    bot.send_message(
        message.chat.id,
        "Choose post type:",
        reply_markup=markup
        )

@bot.message_handler(func=lambda message: message.text in ['Hot', 'New', 'Top', 'Rising'])
def send_hot_posts(message):
    post_type = message.text.lower()
    subreddits = ['memes', 'dankmemes', 'wholesomememes']

    bot.send_message(message.chat.id, f"Looking for {post_type} posts...")

    all_posts = []
    for sub in subreddits:
        posts = get_posts(sub, post_type=post_type, limit=10)
        all_posts.extend(posts)

    trends = analyze_trends(all_posts)
    save_to_db(all_posts, trends)

    trend_plot = plot_trends(trends)

    bot.send_photo(message.chat.id, trend_plot)

    top_posts = sorted(all_posts, key=lambda x: x['upvotes'], reverse=True)[:5]

    for post in top_posts:
        caption = f"{post['title']}\nUpvotes: {post['upvotes']}\nSubreddit: {post['subreddit']}"

        if post['is_image']:
            try:
                watermarked = add_watermark(post['url'])
                if watermarked:
                    save_meme_to_db(post, watermarked)
                    watermarked.seek(0)
                    bot.send_photo(message.chat.id, watermarked, caption=caption)
                else:
                    bot.send_photo(message.chat.id, post['url'], caption = caption)
            except Exception as e:
                logging.info(f"Error sending hot post: {e}")
        else:
            save_to_db(all_posts, trends)
            bot.send_message(message.chat.id, f"{caption}\n{post['url']}")

            send_welcome(message)

@bot.message_handler(func=lambda message: message.text == '🔍 Search by topic')
def ask_search_terms(message):
    msg = bot.send_message(
        message.chat.id,
        "Enter keywords separated by commas",
        reply_markup=types.ReplyKeyboardRemove()
        )
    bot.register_next_step_handler(msg, process_search_terms)

def process_search_terms(message):
    keywords = [word.strip() for word in message.text.split(',')]
    subreddits = ['memes', 'dankmemes']

    bot.send_message(message.chat.id, f"Looking for posts by keywords: {', '.join(keywords)}...")

    matching_posts = []
    for sub in subreddits:
        posts = get_posts(sub, 'top', limit=50)
        for post in posts:
            if any(keyword.lower() in post['title'].lower() for keyword in keywords):
                matching_posts.append(post)

    if not matching_posts:
        bot.send_message(message.chat.id, "Nothing found for your request 😢")
        send_welcome(message)
        return

    image_posts = [p for p in matching_posts if p['is_image']][:5]

    if not image_posts:
        bot.send_message(message.chat.id, "No matching memes found with images")
        send_welcome(message)
        return

    for post in image_posts:
        try:
            watermarked_image = add_watermark(post['url'])

            if watermarked_image:
                save_meme_to_db(post, watermarked_image)

                caption = f"{post['title']}\nUpvotes: {post['upvotes']}\nSubreddit: {post['subreddit']}"
                bot.send_photo(message.chat.id, watermarked_image, caption=caption)
            else:
                bot.send_message(message.chat.id, f"Failed to process meme: {post['url']}")

        except Exception as e:
            logging.info(f"Error processing meme: {e}")
            bot.send_message(message.chat.id, f"Error processing meme: {post['url']}")
            send_welcome(message)

@bot.message_handler(func=lambda message: message.text == '↩️ Back')
def back_to_main(message):
    send_welcome(message)

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)