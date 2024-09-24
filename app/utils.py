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
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        base, ext = os.path.splitext(filename)
        counter = 1

        while os.path.exists(filepath):
            filename = f"{base}_{counter}{ext}"
            filepath = os.path.join('uploads', filename)
            counter += 1

        file.save(filepath)
        return filename
    return None

def convert_url_to_api(url):
    game_id = url.split('/')[-2]
    api_url = f'https://boardgamegeek.com/xmlapi/boardgame/{game_id}'
    return api_url

def get_omnivas():
    locations_file = os.path.join(os.path.dirname(__file__), '..', 'instance', 'locations.json')
    locations_file = os.path.abspath(locations_file)
    
    with open(locations_file, 'r', encoding='utf-8') as file:
        locations_data = json.load(file)
        
        OMNIVA_LOCATIONS = [loc['NAME'] for loc in locations_data if loc.get('A0_Name') == 'LV']
        return OMNIVA_LOCATIONS