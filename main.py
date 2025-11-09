import os
import threading
from app.web import app as flask_app
from bot.main import main as bot_main

def run_flask():
    # Используем переменные окружения для порта, как принято на Railway
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Запускаем бота в основном потоке
    bot_main()
