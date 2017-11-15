from flask import Flask, render_template, request, redirect, url_for, session, g
import config
from models import User, Question, Comment
from exts import db
from decorators import login_required
from sqlalchemy import or_


app = Flask(__name__)
app.config.from_object(config)
# 创建db时没有传入app，需要在主文件中进行一次init
db.init_app(app)


@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter(User.email == email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 让此用户在一个月内保持登录
            if request.form.get('remember_me') == 'on':
                session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'邮箱或密码错误，请确认后再登录'


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('email')
        username = request.form.get('username')
        password_set = request.form.get('password_set')
        password_confirm = request.form.get('password_confirm')

        # 校验项
        user = User.query.filter(User.email == email).first()
        if user:
            return u'该邮箱已被注册，请更换邮箱或尝试登录'
        elif password_set != password_confirm:
            return u'两次输入的密码不相同，请核对后再填写'
        else:
            user = User(email=email, username=username, password=password_set)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    # session.pop('user_id')
    # del session('user_id')
    session.clear()
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/detail/<question_id>/')
def detail(question_id):
    question_detail = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html', question_detail=question_detail)


@app.route('/add_comment/', methods=['POST'])
@login_required
def add_comment():
    raw_comment = request.form.get('comment')
    question_id = request.form.get('question_id')
    comment = Comment(content=raw_comment)
    comment.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    comment.question = question
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


# 这里的请求是'关键字=xxx'形式，不需要在app.route参数中传入<search_content>这类参数
@app.route('/search/')
def search():
    # 获取get请求的表单，用request.args.get
    # 获取post请求的表单，用request.form.get
    q = request.args.get('q')
    # title&content
    # '或'条件，要调用or_函数，如果是'与'条件，直接写条件即可
    questions = Question.query.filter(or_(Question.title.contains(q), Question.content.contains(q))).order_by('-create_time')
    return render_template('index.html', questions=questions)


@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user


# 钩子函数（上下文处理器）实现注销功能
@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user': g.user}
    return {}


if __name__ == '__main__':
    app.run()
