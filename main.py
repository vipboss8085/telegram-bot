
import logging
import os
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
    update.message.reply_text('Hello! Send me lyrics and I will search for the song on YouTube.')

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
            return f"Found song: {title}\nWatch here: {url}"
        else:
            return "Sorry, I couldn't find a song with these lyrics."
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        return "Sorry, there was an error searching for the song."

# Function to handle received messages
def handle_message(update: Update, context: CallbackContext) -> None:
    lyrics = update.message.text
    update.message.reply_text('Searching for the song...')
    result = search_song(lyrics)
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
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

        # Start the Bot
        updater.start_polling()
        logger.info("Bot started successfully")
        
        # Run the bot until you press Ctrl-C
        updater.idle()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
