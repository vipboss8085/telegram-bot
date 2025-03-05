
import logging
import os
import random
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API tokens from environment variables
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# YouTube API Setup
def get_youtube_client():
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Command to start bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me lyrics and I will search for the song on YouTube and generate viral metadata.')

# Function to search YouTube for song
def search_song(lyrics: str):
    youtube = get_youtube_client()
    try:
        request = youtube.search().list(
            q=lyrics,
            part="snippet",
            maxResults=1,
            type="video"
        )
        response = request.execute()

        if response['items']:
            video = response['items'][0]
            title = video['snippet']['title']
            video_id = video['id']['videoId']
            url = f'https://www.youtube.com/watch?v={video_id}'
            return {
                'title': title,
                'url': url,
                'full_response': f"Found song: {title}\nWatch here: {url}"
            }
        else:
            return {
                'title': None,
                'url': None,
                'full_response': "Sorry, I couldn't find a song with these lyrics."
            }
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        return {
            'title': None,
            'url': None,
            'full_response': "Sorry, there was an error searching for the song."
        }

# Function to get trending shorts data
def get_trending_shorts():
    try:
        youtube = get_youtube_client()
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="US",
            videoCategoryId="10",  # Music category
            maxResults=10
        )
        response = request.execute()
        
        trending_titles = [item['snippet']['title'] for item in response.get('items', [])]
        trending_tags = []
        for item in response.get('items', []):
            if 'tags' in item['snippet']:
                trending_tags.extend(item['snippet']['tags'])
        
        # Get unique tags
        trending_tags = list(set(trending_tags))
        
        return trending_titles, trending_tags
    except Exception as e:
        logger.error(f"Error fetching trending data: {e}")
        # Return some default values if API fails
        return (
            ["viral", "trending", "music", "shorts", "tiktok"],
            ["viral", "#trending", "#shorts", "#music", "#fyp", "#foryou", "#songlyrics"]
        )

# Function to generate viral title
def generate_viral_title(song_title, trending_titles):
    if not song_title:
        return "Viral Music Short 🔥 | Popular Song Lyrics"
    
    templates = [
        f"🎵 {song_title} | Viral Lyrics Short 🔥",
        f"This song is EVERYWHERE on TikTok 😱 | {song_title}",
        f"POV: You found {song_title} on your FYP 🎶",
        f"LYRICS: {song_title} | The song everyone is searching for 🔍",
        f"Most VIRAL song right now 🔥 | {song_title}",
        f"This song just went VIRAL 📈 | {song_title}"
    ]
    
    # Add some trending patterns if available
    if trending_titles:
        patterns = [title.split('|')[0].strip() if '|' in title else title for title in trending_titles]
        patterns = [p for p in patterns if len(p) < 30]  # Filter out too long patterns
        if patterns:
            templates.append(f"{random.choice(patterns)} | {song_title} 🎵")
    
    return random.choice(templates)

# Function to generate SEO description
def generate_description(song_title, trending_tags):
    if not song_title:
        return "Enjoy this viral music short! Perfect for your playlist."
    
    lines = [
        f"🎵 {song_title}",
        "",
        "👇 LYRICS in this short 👇",
        "",
        "Follow for more song lyrics and music shorts!",
        "",
        "Save this to watch later 🔖",
        "Like if you love this song ❤️",
        ""
    ]
    
    # Add some trending tags
    if trending_tags:
        selected_tags = random.sample(trending_tags, min(5, len(trending_tags)))
        tags_line = " ".join(selected_tags)
        lines.append(tags_line)
    
    return "\n".join(lines)

# Function to generate tags
def generate_tags(song_title):
    base_tags = [
        "#shorts", "#viral", "#music", "#lyrics", "#song", 
        "#tiktok", "#ytshorts", "#trending", "#viralvideo", 
        "#songlyrics", "#fyp", "#foryou", "#foryoupage"
    ]
    
    if song_title:
        # Create song-specific tags
        song_words = song_title.lower().replace("'", "").replace("(", "").replace(")", "").split()
        song_tags = []
        
        # Single word tags
        for word in song_words:
            if len(word) > 3 and word not in ["feat", "featuring", "with", "lyrics"]:
                song_tags.append(f"#{word}")
        
        # Combined tags (up to 3 words)
        if len(song_words) >= 2:
            combined = "".join(song_words[:min(3, len(song_words))])
            song_tags.append(f"#{combined}")
        
        # Full song title tag
        full_tag = "".join(song_words)
        if len(full_tag) < 20:  # Avoid too long tags
            song_tags.append(f"#{full_tag}")
        
        # Add song tags to base tags
        base_tags.extend(song_tags[:5])  # Add up to 5 song-specific tags
    
    # Randomize the order a bit
    random.shuffle(base_tags)
    
    return " ".join(base_tags[:15])  # Return up to 15 tags

# Function to handle basic song search
def handle_message(update: Update, context: CallbackContext) -> None:
    lyrics = update.message.text
    update.message.reply_text('Searching for the song...')
    result = search_song(lyrics)
    update.message.reply_text(result['full_response'])

# Function to handle metadata generation
def generate_metadata(update: Update, context: CallbackContext) -> None:
    lyrics = update.message.text
    update.message.reply_text('Searching for song and generating viral metadata...')

    # Song Search
    song_result = search_song(lyrics)
    song_title = song_result.get('title')
    
    trending_titles, trending_tags = get_trending_shorts()

    # Metadata Generate
    viral_title = generate_viral_title(song_title, trending_titles)
    seo_description = generate_description(song_title, trending_tags)
    seo_tags = generate_tags(song_title)

    # Send Response
    if song_result['url']:
        result = f"🎵 Found song: {song_title}\n🔗 {song_result['url']}\n\n📱 VIRAL METADATA 📱\n\n*Title:*\n{viral_title}\n\n*Description:*\n{seo_description}\n\n*Tags:*\n{seo_tags}"
    else:
        result = f"⚠️ {song_result['full_response']}\n\nI still generated some generic metadata for you:\n\n*Title:*\n{viral_title}\n\n*Description:*\n{seo_description}\n\n*Tags:*\n{seo_tags}"
    
    update.message.reply_text(result)

# Main function to run the bot
def main() -> None:
    # Check if tokens are available
    if not TELEGRAM_API_TOKEN:
        logger.error("TELEGRAM_API_TOKEN not found in environment variables")
        return
    
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY not found in environment variables")
        return
    
    try:
        updater = Updater(TELEGRAM_API_TOKEN)
        dispatcher = updater.dispatcher

        # Handlers for different commands
        dispatcher.add_handler(CommandHandler("start", start))
        
        # Add command handlers for different functionalities
        dispatcher.add_handler(CommandHandler("search", handle_message))
        dispatcher.add_handler(CommandHandler("metadata", generate_metadata))
        
        # Default handler - generate metadata
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_metadata))

        # Start the Bot
        updater.start_polling()
        logger.info("Bot started successfully")
        
        # Run the bot until you press Ctrl-C
        updater.idle()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
