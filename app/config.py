import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Telegram Bot ---
# !!! SECURITY WARNING: Do not hardcode the bot token in production.
# Use an environment variable for this.
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '')

# --- Web App ---
SECRET_KEY = os.environ.get('SECRET_KEY')
ENABLE_VALIDATION = os.environ.get('ENABLE_VALIDATION', 'True').lower() == 'true'

# --- Database ---
DB_NAME = os.environ.get('DB_PATH', 'wishlist.db')

# --- Monetization ---
# These are default values. They will be stored in the DB after first launch.
DEFAULT_SETTINGS = {
    'free_wishlist_items': int(os.environ.get('FREE_WISHLIST_ITEMS', 5)),
    'new_wishlist_price': int(os.environ.get('NEW_WISHLIST_PRICE', 10)),
    'new_item_price': int(os.environ.get('NEW_ITEM_PRICE', 2)),
}

# --- Misc ---
SKIP_WORDS = {"пропустить", "skip", "нет", "no", "пропуск"}
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))
