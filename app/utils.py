import os
from werkzeug.utils import secure_filename
from flask import current_app as app
import json

def fromjson(value):
    return json.loads(value)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        base, ext = os.path.splitext(filename)
        counter = 1

        while os.path.exists(filepath):
            filename = f"{base}_{counter}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1

        file.save(filepath)
        return filename
    return None

def convert_url_to_api(url):
    game_id = url.split('/')[-2]
    api_url = f'https://boardgamegeek.com/xmlapi/boardgame/{game_id}'
    return api_url