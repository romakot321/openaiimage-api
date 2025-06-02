from loguru import logger

logger.add("/app/logs/app.json", format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}", serialize=True, rotation="500 MB")
