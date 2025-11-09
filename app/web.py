from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime
import logging
import hmac
import hashlib
import json
import os
from functools import wraps
from urllib.parse import parse_qsl

# Import centralized modules
from app.database import db, get_setting, update_setting, init_default_settings
from app.config import (
    BOT_TOKEN, ADMIN_USER_ID, ENABLE_VALIDATION, DEFAULT_SETTINGS, DEBUG, PORT
)

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Initial Setup ---
# Initialize default settings in the database on startup
with app.app_context():
    init_default_settings(DEFAULT_SETTINGS)

if not BOT_TOKEN and ENABLE_VALIDATION:
    logger.warning("BOT_TOKEN is not set. Telegram data validation will be disabled.")

# --- Authentication & User Handling ---

def validate_telegram_data(init_data: str) -> bool:
    """Validates the authenticity of data from Telegram WebApp."""
    if not BOT_TOKEN:
        return False
    try:
        parsed_data = dict(parse_qsl(init_data))
        if 'hash' not in parsed_data:
            return False
        
        received_hash = parsed_data.pop('hash')
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return calculated_hash == received_hash
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False

def login_required(f):
    """Decorator to protect routes that require a valid Telegram user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        init_data = request.headers.get('X-Telegram-Init-Data')
        if not init_data:
            return jsonify({'error': 'Unauthorized', 'message': 'X-Telegram-Init-Data header is missing.'}), 401

        if ENABLE_VALIDATION and not validate_telegram_data(init_data):
            logger.warning("Invalid Telegram data received.")
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid Telegram data.'}), 401
        
        try:
            user_str = dict(parse_qsl(init_data)).get('user', '{}')
            user_data = json.loads(user_str)
            user_id = user_data.get('id')
            if not user_id:
                return jsonify({'error': 'Unauthorized', 'message': 'User ID not found in data.'}), 401
            
            # Store user_id in Flask's application context global `g`
            g.user_id = user_id
            g.user_data = user_data
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing user data: {e}")
            return jsonify({'error': 'Bad Request', 'message': 'Could not parse user data.'}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to protect routes that require admin privileges."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_id = g.user_id
        if not ADMIN_USER_ID:
            return jsonify({'error': 'Forbidden', 'message': 'Admin not configured.'}), 403
        try:
            admin_ids = [int(uid.strip()) for uid in ADMIN_USER_ID.split(',')]
            if user_id not in admin_ids:
                return jsonify({'error': 'Forbidden', 'message': 'Admin access required.'}), 403
        except ValueError:
            if str(user_id) != str(ADMIN_USER_ID):
                return jsonify({'error': 'Forbidden', 'message': 'Admin access required.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# --- API Routes ---

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    """Gets information about the current user."""
    user = db.execute('SELECT user_id, username, first_name FROM users WHERE user_id = ?', (g.user_id,), fetchone=True)
    if user:
        return jsonify({'user_id': user[0], 'username': user[1], 'first_name': user[2]})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/wishlists', methods=['GET'])
@login_required
def get_wishlists():
    """Gets all wishlists for the current user."""
    wishlists_data = db.execute(
        '''SELECT id, name, is_free, created_at FROM wishlists
           WHERE user_id = ? ORDER BY created_at DESC''',
        (g.user_id,), fetchall=True
    )
    
    result = []
    for wl_id, name, is_free, created_at in wishlists_data:
        item_count = db.execute('SELECT COUNT(*) FROM items WHERE wishlist_id = ?', (wl_id,), fetchone=True)[0]
        result.append({
            'id': wl_id, 'name': name, 'is_free': bool(is_free),
            'item_count': item_count, 'created_at': created_at
        })
    return jsonify(result)

@app.route('/api/wishlists', methods=['POST'])
@login_required
def create_wishlist():
    """Creates a new wishlist."""
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    # Ensure user exists, create if not
    db.execute(
        '''INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
           VALUES (?, ?, ?, ?)''',
        (g.user_id, g.user_data.get('username'), g.user_data.get('first_name'), datetime.now()),
        commit=True
    )

    wishlist_count = db.execute('SELECT COUNT(*) FROM wishlists WHERE user_id = ?', (g.user_id,), fetchone=True)[0]
    is_free = wishlist_count == 0
    
    wishlist_id = db.execute(
        '''INSERT INTO wishlists (user_id, name, is_free, created_at)
           VALUES (?, ?, ?, ?)''',
        (g.user_id, name, 1 if is_free else 0, datetime.now()),
        commit=True
    )
    
    return jsonify({
        'id': wishlist_id, 'name': name, 'is_free': is_free, 'item_count': 0
    }), 201

@app.route('/api/wishlists/<int:wishlist_id>', methods=['GET'])
@login_required
def get_wishlist(wishlist_id):
    """Gets a specific wishlist with its items."""
    wishlist = db.execute('SELECT id, name, user_id FROM wishlists WHERE id = ?', (wishlist_id,), fetchone=True)
    if not wishlist:
        return jsonify({'error': 'Wishlist not found'}), 404
    if wishlist[2] != g.user_id:
        return jsonify({'error': 'Forbidden'}), 403

    items_data = db.execute(
        'SELECT id, title, description, url, image_url, created_at FROM items WHERE wishlist_id = ? ORDER BY created_at DESC',
        (wishlist_id,), fetchall=True
    )
    items = [{
        'id': item[0], 'title': item[1], 'description': item[2] or '',
        'url': item[3] or '', 'image_url': item[4] or '', 'created_at': item[5]
    } for item in items_data]
    
    return jsonify({'id': wishlist[0], 'name': wishlist[1], 'items': items})

@app.route('/api/wishlists/<int:wishlist_id>', methods=['DELETE'])
@login_required
def delete_wishlist(wishlist_id):
    """Deletes a wishlist."""
    wishlist = db.execute('SELECT user_id FROM wishlists WHERE id = ?', (wishlist_id,), fetchone=True)
    if not wishlist:
        return jsonify({'error': 'Wishlist not found'}), 404
    if wishlist[0] != g.user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    db.execute('DELETE FROM items WHERE wishlist_id = ?', (wishlist_id,), commit=True)
    db.execute('DELETE FROM wishlists WHERE id = ?', (wishlist_id,), commit=True)
    
    return jsonify({'success': True})

@app.route('/api/wishlists/<int:wishlist_id>/items', methods=['POST'])
@login_required
def add_item(wishlist_id):
    """Adds an item to a wishlist."""
    wishlist = db.execute('SELECT user_id FROM wishlists WHERE id = ?', (wishlist_id,), fetchone=True)
    if not wishlist:
        return jsonify({'error': 'Wishlist not found'}), 404
    if wishlist[0] != g.user_id:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.json
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    item_count = db.execute('SELECT COUNT(*) FROM items WHERE wishlist_id = ?', (wishlist_id,), fetchone=True)[0]
    wishlist_count = db.execute('SELECT COUNT(*) FROM wishlists WHERE user_id = ?', (g.user_id,), fetchone=True)[0]
    free_items_limit = get_setting('free_wishlist_items', DEFAULT_SETTINGS['free_wishlist_items'])
    
    is_free = wishlist_count == 1 and item_count < free_items_limit
    
    item_id = db.execute(
        '''INSERT INTO items (wishlist_id, title, description, url, image_url, is_free, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            wishlist_id, title[:100], data.get('description', '')[:500] or '',
            data.get('url') or None, data.get('image_url') or None,
            1 if is_free else 0, datetime.now()
        ),
        commit=True
    )
    
    return jsonify({
        'id': item_id, 'title': title, 'description': data.get('description', ''),
        'url': data.get('url', ''), 'image_url': data.get('image_url', '')
    }), 201

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Deletes an item."""
    item = db.execute(
        'SELECT w.user_id FROM items i JOIN wishlists w ON i.wishlist_id = w.id WHERE i.id = ?',
        (item_id,), fetchone=True
    )
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    if item[0] != g.user_id:
        return jsonify({'error': 'Forbidden'}), 403
        
    db.execute('DELETE FROM items WHERE id = ?', (item_id,), commit=True)
    return jsonify({'success': True})

@app.route('/api/pricing', methods=['GET'])
@login_required
def get_pricing():
    """Gets pricing information."""
    wishlist_count = db.execute('SELECT COUNT(*) FROM wishlists WHERE user_id = ?', (g.user_id,), fetchone=True)[0]
    
    return jsonify({
        'free_wishlist_items': get_setting('free_wishlist_items', DEFAULT_SETTINGS['free_wishlist_items']),
        'new_wishlist_price': get_setting('new_wishlist_price', DEFAULT_SETTINGS['new_wishlist_price']),
        'new_item_price': get_setting('new_item_price', DEFAULT_SETTINGS['new_item_price']),
        'has_free_wishlist': wishlist_count == 0
    })

# --- Public Routes (for inline mode, etc.) ---

@app.route('/api/public/wishlist/<int:wishlist_id>', methods=['GET'])
def get_public_wishlist(wishlist_id):
    """Gets a public view of a wishlist."""
    wishlist = db.execute(
        '''SELECT w.id, w.name, w.user_id, u.first_name, u.username
           FROM wishlists w JOIN users u ON w.user_id = u.user_id WHERE w.id = ?''',
        (wishlist_id,), fetchone=True
    )
    if not wishlist:
        return jsonify({'error': 'Wishlist not found'}), 404

    items_data = db.execute(
        'SELECT id, title, description, url, image_url, created_at FROM items WHERE wishlist_id = ? ORDER BY created_at DESC',
        (wishlist_id,), fetchall=True
    )
    items = [{
        'id': item[0], 'title': item[1], 'description': item[2] or '',
        'url': item[3] or '', 'image_url': item[4] or '', 'created_at': item[5]
    } for item in items_data]
    
    return jsonify({
        'id': wishlist[0], 'name': wishlist[1], 'user_id': wishlist[2],
        'user_name': wishlist[3], 'user_username': wishlist[4], 'items': items
    })

# ... (other public routes can be refactored similarly)

# --- Admin Routes ---

@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def get_admin_settings():
    """Gets all application settings."""
    settings_data = db.execute('SELECT key, value FROM settings ORDER BY key', fetchall=True)
    settings = {key: (int(value) if value.isdigit() else value) for key, value in settings_data}
    return jsonify(settings)

@app.route('/api/admin/settings', methods=['POST'])
@admin_required
def update_admin_settings():
    """Updates application settings."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    allowed_keys = DEFAULT_SETTINGS.keys()
    updated = {}
    for key, value in data.items():
        if key in allowed_keys:
            try:
                int_value = int(value)
                if int_value < 0:
                    return jsonify({'error': f'{key} must be non-negative'}), 400
                update_setting(key, int_value)
                updated[key] = int_value
            except ValueError:
                return jsonify({'error': f'{key} must be a number'}), 400
    
    return jsonify({'success': True, 'updated': updated})

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Gets application usage statistics."""
    stats = {
        'total_users': db.execute('SELECT COUNT(*) FROM users', fetchone=True)[0],
        'total_wishlists': db.execute('SELECT COUNT(*) FROM wishlists', fetchone=True)[0],
        'total_items': db.execute('SELECT COUNT(*) FROM items', fetchone=True)[0],
        'wishlists_by_day': db.execute(
            '''SELECT DATE(created_at) as date, COUNT(*) as count
               FROM wishlists WHERE created_at >= date('now', '-7 days')
               GROUP BY DATE(created_at) ORDER BY date''', fetchall=True
        )
    }
    return jsonify(stats)

from telegram import Update
from bot.main import application

# ... (existing imports)

# --- Webhook Routes ---

@app.route('/api/set_webhook', methods=['GET'])
@admin_required
async def set_webhook():
    """Sets the webhook for the Telegram bot."""
    webhook_url = f"https://{request.headers['Host']}/api/webhook"
    try:
        await application.bot.set_webhook(url=webhook_url)
        return jsonify({'status': 'success', 'message': f'Webhook set to {webhook_url}'})
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/webhook', methods=['POST'])
async def webhook():
    """Handles incoming updates from Telegram."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.update_queue.put(update)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


