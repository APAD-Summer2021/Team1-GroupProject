from urllib import request

from flask import url_for, render_template, jsonify
from passlib.handlers import bcrypt
from requests import session
from werkzeug.utils import redirect


def signup(records):
    if "email" in session:
        return jsonify()
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return jsonify({'message': message})
        if email_found:
            message = 'This email already exists in database'
            return jsonify({'message': message})
        if password1 != password2:
            message = 'Passwords should match!'
            return jsonify({'message': message})
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            return jsonify({'new_email': new_email})
    else:
        return jsonify()
