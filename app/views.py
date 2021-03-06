from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm
from flask.ext.login import current_user, login_user, login_required, logout_user
from forms import LoginForm, RegisterForm, PostArticle
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import User, Post, ROLE_WRITER
from sidebars import twitch_streams

@app.route('/news')
@app.route('/units')
@app.route('/build-orders')
def coming_soon():
    return render_template("coming_soon.html",
            sidebars = g.sidebars,
            title="Coming Soon")

@app.route('/')
@app.route('/index')
def index():
    query = Post.query.order_by(Post.timestamp.desc())
    items = query.paginate(1, 4, False).items
    return render_template("index.html", 
            sidebars = g.sidebars,
            title = "Home",
            items=items)

@app.route('/about')
def about():
    intro_post = Post.query.get(1)
    return render_template("about.html",
            sidebars = g.sidebars,
            title = "About",
            item = intro_post)
    
@app.route('/blog')
def blog():
    query = Post.query.filter_by(type="article",category="site-news").order_by(Post.timestamp.desc())
    items = query.paginate(1, 4, False).items
    return render_template("blog.html", 
            sidebars = g.sidebars,
            title = "Blog",
            items=items)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    g.sidebars = []
    g.sidebars.append({'machine_name':'useful_links'})
    g.sidebars.append({'machine_name':'twitch_streams', 'data': twitch_streams()})
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/article/<articleid>')
def article(articleid):
    if type(articleid) is int:
        item = Post.query.get(articleid)
        if not item:
            abort(404)
    else:
        item = Post.query.filter_by(machine_name=articleid, type="article").order_by(Post.timestamp.desc()).first()
        if not item:
            abort(404)
    return render_template('article_page.html',
            item = item,
            sidebars = g.sidebars,
            title = item.title)

@app.route('/general-guides')
def general_guides():
    query = Post.query.filter_by(type="guide").order_by(Post.timestamp.desc())
    items = query.paginate(1, 4, False).items
    return render_template("general_guides_list.html", 
            sidebars = g.sidebars,
            title = "Home",
            items=items)

@app.route('/guide/<guideid>')
def guide(guideid):
    if type(guideid) is int:
        guide = Post.query.get(guideid)
        if not guide:
            abort(404)
    else:
        guide = Post.query.filter_by(machine_name=guideid,type="guide").order_by(Post.timestamp.desc()).first()
        if not guide:
            abort(404)
    return render_template('guide_page.html',
            item = guide,
            sidebars = g.sidebars,
            title = guide.title)

@app.route('/post-guide', methods = ['GET', 'POST'])
def post_article():
    if g.user is None or not g.user.is_authenticated() or g.user.role < ROLE_WRITER:
      return redirect(url_for('index'))
    form = PostArticle()
    if form.validate_on_submit():
        article = Post(body = form.content.data, title=form.title.data, description=form.description.data, category=form.category.data, machine_name=form.machine_name.data, author=g.user, type="guide", timestamp = datetime.utcnow())
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post_article.html',
        title='Post Guide',
            sidebar = g.sidebars,
        form = form)
    

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        if not login_user(User.query.filter_by(username = form.username.data).first(), form.remember_me.data):
            flash('Error logging in')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html',
            sidebar = g.sidebars,
        title = 'Login',
        form = form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email=form.email.data, password=generate_password_hash(form.password.data), registered=datetime.utcnow(), last_seen=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html',
            sidebar = g.sidebars,
        title='Register',
        form = form)

@app.route('/post-article', methods = ['GET', 'POST'])
def post_article():
    if g.user is None or not g.user.is_authenticated() or g.user.role < ROLE_WRITER:
      return redirect(url_for('index'))
    form = PostArticle()
    if form.validate_on_submit():
        article = Post(body = form.content.data, title=form.title.data, description=form.description.data, category=form.category.data, machine_name=form.machine_name.data, author=g.user, type="article", timestamp = datetime.utcnow())
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post_article.html',
        title='Post Article',
            sidebar = g.sidebars,
        form = form)
