import datetime
from urllib import request
from flask import url_for, jsonify
from requests import session
from werkzeug.utils import redirect


def post_action(postings,fs,user_data):
    if "email" in session:
        user_id = session["email"]
        type_of_pet = request.form.get("type")
        tags = request.values.get("tags")
        tags = tags.lower()
        post_date = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
        title = request.values.get("title")
        desc = request.values.get("description")
        location = request.values.get("location")

        if 'file' in request.files:
            print('Here')
            image = request.files["file"]
            title = request.values.get('title')
            img_id = fs.put(image, content_type=image.content_type, filename=title)

        query = {
            'id': img_id,
            'title': request.form.get('title'),
        }
        # status = postings.insert_one(query)
        status = "Open"
        try:
            post_response = postings.insert_one(
                {"user_id": user_id, "tags": tags, "date_posted": post_date, "detailed_description": desc,
                 "post_title": title, "location": location, "image_id": img_id, "type": type_of_pet, "status": status})
            # print(str(post_response.inserted_id))
            post_id = str(post_response.inserted_id)
            # insert document ID into User_data table
            user_data.insert_one({"user_id": user_id, "posts": [post_id], })
            # print(post_id)
            session["post_id"] = post_id
            return jsonify({'message': 'successful'})
        except Exception as e:
            print(e)
            return jsonify()
    else:
        return jsonify({'message': 'Not Logged in!!'})
