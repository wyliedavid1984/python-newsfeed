from flask import Blueprint, render_template, session
from app.models import Post
from app.db import get_db
from app.utils.auth import login_required

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# gets all post from user
@bp.route('/')
@login_required
def dash():
  # connect to db
  db = get_db()
  # db query
  posts = (
    db.query(Post)
    .filter(Post.user_id == session.get("user_id"))
    .order_by(Post.created_at.desc())
    .all()
  )
  # return dashboard with posts
  return render_template('dashboard.html',
    posts=posts,
    loggedIn=session.get("loggedIn")
  )


@bp.route('/edit/<id>')
@login_required
def edit(id):
  # get on single post by id
  db = get_db()
  post = db.query(Post).filter(Post.id == id).one()
  # return single post edit
  return render_template('edit-post.html',
    post=post,
    loggedIn=session.get("loggedIn")
  )