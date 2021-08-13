import codecs
from urllib import request
from flask import render_template, url_for, jsonify
from requests import session
from werkzeug.utils import redirect


def view_all(postings,themes_db,fs):
    db_dump_themes = themes_db.find()
    list_of_themes_db = []
    for theme in db_dump_themes:
        if theme not in list_of_themes_db:
            list_of_themes_db.append(theme)
    if "email" in session:
        posts = postings.find().sort('date_posted', -1)
        images = {}
        list_of_themes = []
        for post in posts:                # print(post)
            list_of_themes.append(post['type'])
            image = fs.get(post['image_id'])
            base64_data = codecs.encode(image.read(), 'base64')
            image = base64_data.decode('utf-8')
            images.update({post['image_id']: image})
        posts = postings.find().sort('date_posted', -1)
        return jsonify({'posts': posts, 'images': images, 'list_of_themes_db': list_of_themes_db})
    else:
        return jsonify({'message': 'Please Login !!'})
