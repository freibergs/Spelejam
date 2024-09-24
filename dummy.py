import sqlite3
import random
from faker import Faker
from datetime import datetime
from slugify import slugify

conn = sqlite3.connect('instance/store.db')
cursor = conn.cursor()

fake = Faker()

users = [
    {"username": "admin", "email": fake.email(), "password": "pbkdf2:sha256:600000$N8Z79AH5Yv6g9Wyv$d8f27ef0a35510195415b9e750e3653041affb5cc48ab98c4987fa828ea21a8c", "user_level": 3},
    {"username": "user", "email": fake.email(), "password": "pbkdf2:sha256:600000$N8Z79AH5Yv6g9Wyv$d8f27ef0a35510195415b9e750e3653041affb5cc48ab98c4987fa828ea21a8c", "user_level": 2},
    {"username": "user2", "email": fake.email(), "password": "pbkdf2:sha256:600000$N8Z79AH5Yv6g9Wyv$d8f27ef0a35510195415b9e750e3653041affb5cc48ab98c4987fa828ea21a8c", "user_level": 2}
]

for user in users:
    cursor.execute("""
        INSERT INTO user (username, email, password, location, is_active, user_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user['username'], user['email'], user['password'], None, True, user['user_level']))

conn.commit()

cursor.execute("SELECT id FROM user")
user_ids = [row[0] for row in cursor.fetchall()]

product_count = 100
blog_count = 10
review_count = 20

def add_category(name):
    cursor.execute("SELECT id FROM category WHERE name = ?", (name,))
    category = cursor.fetchone()
    if category is None:
        slug = slugify(name)
        cursor.execute("INSERT INTO category (name, url_slug) VALUES (?, ?)", (name, slug))
        return cursor.lastrowid
    return category[0]

def add_tag(name):
    cursor.execute("SELECT id FROM tag WHERE name = ?", (name,))
    tag = cursor.fetchone()
    if tag is None:
        slug = slugify(name)
        cursor.execute("INSERT INTO tag (name, url_slug) VALUES (?, ?)", (name, slug))
        return cursor.lastrowid
    return tag[0]

def generate_random_players():
    num_players = random.randint(1, 9)
    players = sorted(set(random.choices(range(1, 11), k=random.randint(1, 5))))
    return ",".join(str(p) if p < 10 else "10" for p in players)

category_names = ["Strategy", "Family", "Party", "Abstract", "Thematic"]
tag_names = ["Easy to learn", "For experts", "Short game", "Long game", "Multiplayer"]

category_ids = [add_category(name) for name in category_names]
tag_ids = [add_tag(name) for name in tag_names]

images = ["1.jpg", "2.jpg", "3.png", "4.png", "5.jpg"]

for _ in range(product_count):
    name = fake.word().capitalize() + " " + fake.word().capitalize()
    slug = slugify(name)
    description = fake.sentence(nb_words=10)
    price = round(random.uniform(10.0, 100.0), 2)
    condition = random.randint(1, 10)
    missing_parts = fake.word().capitalize() if random.random() > 0.8 else None
    main_image = random.choice(images)
    additional_images = ",".join(random.sample(images, random.randint(1, 3)))
    category_id = random.choice(category_ids)
    product_tags = random.sample(tag_ids, random.randint(1, 3))
    owner_id = random.choice(user_ids)
    date_added = datetime.utcnow()
    players = generate_random_players()
    bgg_url = "https://boardgamegeek.com/boardgame/413663/pizza-chef-the-next-generation"
    stock = 1

    cursor.execute("""
        INSERT INTO product (name, slug, description, price, condition, missing_parts, main_image, images, bgg_url, owner_id, category_id, date_added, players, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, slug, description, price, condition, missing_parts, main_image, additional_images, bgg_url, owner_id, category_id, date_added, players, stock))

    product_id = cursor.lastrowid

    for tag_id in product_tags:
        cursor.execute("INSERT INTO product_tag (product_id, tag_id) VALUES (?, ?)", (product_id, tag_id))

for _ in range(blog_count):
    title = fake.sentence(nb_words=6).capitalize()
    slug = slugify(title)
    content = "<p>" + fake.paragraph(nb_sentences=5) + "</p>" + "<p>" + fake.paragraph(nb_sentences=5) + "</p>"
    meta_title = title
    meta_description = fake.sentence(nb_words=10)
    meta_keywords = ", ".join(fake.words(nb=5))
    cover_image = random.choice(images)
    created_at = datetime.utcnow()

    cursor.execute("""
        INSERT INTO blog (title, url_slug, content, meta_title, meta_description, meta_keywords, cover_image, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, slug, content, meta_title, meta_description, meta_keywords, cover_image, created_at))

for _ in range(review_count):
    text = fake.sentence(nb_words=20)
    name = fake.name()
    score = random.randint(1, 10)
    date_added = datetime.utcnow()

    cursor.execute("""
        INSERT INTO review (text, name, score, date_added)
        VALUES (?, ?, ?, ?)
    """, (text, name, score, date_added))

conn.commit()
conn.close()

print(f"{product_count} random products, {blog_count} random blog posts, and {review_count} random reviews added to the database.")
