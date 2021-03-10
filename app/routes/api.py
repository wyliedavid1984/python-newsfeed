from flask import Blueprint, request, jsonify, session, redirect
from app.models import User, Post, Comment, Vote
from app.db import get_db
import sys

bp = Blueprint("api", __name__, url_prefix="/api")


# signup route for new users and then sign that user
@bp.route("/users", methods=["POST"])
def signup():
  data = request.get_json()
  db=get_db()
  print(data)
  
  try:
    # setup new user
    newUser = User(
      username = data["username"],
      email = data["email"],
      password = data["password"]
    )

    # save new user to database
    db.add(newUser)
    db.commit()
    print("success!")
  except:
    # print error message out
    print(sys.exc_info()[0])

    #insert failed, so rollback and send error to frontend
    db.rollback()
    return jsonify(message = "Signup failed"), 500
  
  # start session for new user
  session.clear()
  session["user_id"] = newUser.id
  session['loggedIn'] = True

  return jsonify(id=newUser.id)


# logout route
@bp.route("/users/logout", methods=["POST"])
def logout():
  #remove session variable
  session.clear()
  return "", 204


# login route
@bp.route("/users/login", methods=["POST"])
def login():
  data = request.get_json()
  db = get_db()

  # try to get user otherwise throw error message
  try:
    user = db.query(User).filter(User.email == data["email"]).one()
  except:
    print(sys.exc_info()[0])

    return jsonify(message = "Incorrect credentials"), 400

  # verify password and throw error message is wrongh
  if user.verify_password(data["password"]) == False:
    return jsonify(message = "Incorrect credentials"), 400
  
  # start session for user
  session.clear()
  session["user_id"] = user.id
  session["loggedIn"] = True

  return jsonify(id = user.id)
@bp.route("/comments", methods=["POST"])
def comment():
  data = request.get_json()
  db = get_db()

  try:
    #create a new comment
    newComment = Comment(
      comment_text = data["comment_text"],
      post_id = data["post_id"],
      user_id = session.get("user_id")
    )

    db.add(newComment)
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = "Comment Failed"), 500
    
  return jsonify(id = newComment.id)
