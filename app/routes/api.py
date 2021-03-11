from flask import Blueprint, request, jsonify, session, redirect
from app.models import User, Post, Comment, Vote
from app.db import get_db
import sys
from app.utils.auth import login_required

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
    return jsonify(message = "Signup New User failed"), 500
  
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

  print(user.id, 'user id here')
  # start session for user
  session.clear()
  session["user_id"] = user.id
  session["loggedIn"] = True
  print(session["user_id"], "userId", "is logged in", session["loggedIn"])
  return jsonify(id = user.id)

# added route to make new comments
@bp.route("/comments", methods=["POST"])
@login_required
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
    return jsonify(message = "Create New Comment Failed"), 500
  return jsonify(id = newComment.id)

# update route to increase the vote count
@bp.route("/posts/upvote", methods=["PUT"])
@login_required
def upvote():
  data = request.get_json()
  db = get_db()

  try:
    #create a new bote with incoming id and session id
    newVote = Vote(
      post_id = data["post_id"],
      user_id = session.get("user_id")
    )

    db.add(newVote)
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = "Upvote failed"), 500
  return "", 204

# post route for new post
@bp.route("/posts", methods = ["POST"])
@login_required
def create():
  data = request.get_json()
  db = get_db()

  try:
    # creates new post for db
    newPost = Post(
      title = data["title"],
      post_url = data["post_url"],
      user_id = session.get("user_id")
    )

    db.add(newPost)
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = "Create New Post Failed")
  return jsonify(id = newPost.id)

@bp.route("/posts/<id>", methods=["PUT"])
@login_required
def update(id):
  data = request.get_json()
  db = get_db()
  
  try:
  # get the post from data base and update it
    post = db.query(Post).filter(Post.id == id).one()
    post.title = data["title"]
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = "Post not found"), 404
  return "", 204

@bp.route("posts/<id>", methods=["PUT"])
@login_required
def delete(id):
  db = get_db()

  try:
    # delete the post from db
    db.delete(db.query(Post).filter(Post.id == id).one())
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = "Post not found"), 404
  return "", 204

