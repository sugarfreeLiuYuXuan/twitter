from email.mime import text
from twittor.email import send_email
from flask import render_template, redirect, url_for, request,abort,current_app
from flask.helpers import flash
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import form
from twittor.forms import LoginForm, PasswdResetRequestForm, RegisterForm,EditProfileForm,\
    TweetForm,PasswdResetForm
from twittor.models.user import User, load_user
from twittor.models.tweets import Tweet
from twittor import db


@login_required
def index():
    form = TweetForm()
    if form.validate_on_submit():
        t = Tweet(body=form.tweet.data,author=current_user)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('index'))
    page_number= int (request.args.get('page') or 1)
    tweets = current_user.own_and_followed_tweets().paginate(
        page=page_number,per_page=current_app.config['TWEET_PER_PAGE'],error_out=False)
    next_url = url_for('index',page=tweets.next_num)
    prev_url = url_for('index',page=tweets.prev_num)
    flag_next = tweets.has_next
    flag_prev = tweets.has_prev
    return render_template(
        'index.html',tweets=tweets.items,form=form,next_url=next_url,prev_url=prev_url,
        flag_next=flag_next,flag_prev=flag_prev
        )


def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            print('invalid username or password')
            return redirect(url_for('login'))
        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html', title="Sign In", form=form)

def logout():
    logout_user()
    return redirect(url_for('login'))


def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)

@login_required   #仅登陆后的用户可以操作
def user(username):
    ur=User.query.filter_by(username= username).first()
    if ur is None:
        abort(404)
    page_number= int (request.args.get('page') or 1)
    tweets=Tweet.query.filter_by(author=ur).order_by(Tweet.create_time.desc()).paginate(
        page=page_number,per_page=current_app.config['TWEET_PER_PAGE'],error_out=False) 

    next_url = url_for('profile',page=tweets.next_num,username=username)
    prev_url = url_for('profile',page=tweets.prev_num,username=username)
    flag_next = tweets.has_next
    flag_prev = tweets.has_prev

    if request.method=='POST':
        if request.form['request_button'] == 'Follow':
            current_user.follow(ur)
            db.session.commit()
        elif request.form['request_button'] == 'UnFollow':
            current_user.unfollow(ur)
            db.session.commit()
        else:
            flash("系统将会发送激活邮件至您的邮箱，请查收")
            send_email_for_user_activate(current_user)
    return render_template('user.html',title='Profile',tweets=tweets.items,user=ur,
        next_url=next_url,prev_url=prev_url,flag_next=flag_next,flag_prev=flag_prev)

def send_email_for_user_activate(user):
    token = user.get_jwt()
    url_user_activate = url_for(
        'user_activate',
        token=token,
        _external=True
    )
    send_email(
        subject=current_app.config['MAIN_SUBJECT_USER_ACTIVATE'],
        recipients=[user.email],
        text_body= render_template(
            'email/user_activate.txt',
            username=user.username,
            url_user_activate=url_user_activate
        ),
        html_body=render_template(
            'email/user_activate.html',
            username=user.username,
            url_user_activate=url_user_activate
        )
    )


def user_activate(token):
    if current_user.is_authenticated:
        print("3333")
        return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        print("11")
        msg = "Token可能已经过期，请重新点击按钮发送邮箱"
    else:
        print("22")
        user.is_activated = True
        db.session.commit()
        msg = '用户邮箱已经被激活'
    return render_template(
        'user_activate.html', msg=msg
    )


def page_not_found(err):
    return render_template('404.html'),404

@login_required  #仅当前用户可以修改
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.about_me.data = current_user.about_me
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    return render_template('edit_profile.html', form=form)


def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswdResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        
        if user:
            flash(
                "你将收到一份来自服务器的验证邮件请至邮箱或垃圾箱中查看你的邮件"
            )
            token = user.get_jwt()
            url_password_reset = url_for(
                'password_reset',token=token,
                _external = True    #代表完整的http链接
            )
            url_password_reset_request = url_for(
                'password_reset_request',
                _external =True    
            )

            send_email(
                subject=current_app.config['MAIL_SUBJECT_RESET_PASSWORD'],
                recipients=[user.email],
                text_body='ok',
                html_body=render_template(
                    'email/email_for_reset_password.html',
                    url_password_reset = url_password_reset,
                    url_password_reset_request=url_password_reset_request
                )
            )
        return redirect(url_for('login'))
    return render_template('password_reset_request.html',form=form)



def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        return redirect(url_for('login'))
    form = PasswdResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template(
        'password_reset.html', title='Password Reset', form=form
    )

@login_required
def explore():
    # get all user and sort by followers
    page_num = int(request.args.get('page') or 1)
    tweets = Tweet.query.order_by(Tweet.create_time.desc()).paginate(
        page=page_num, per_page=10, error_out=False)

    next_url = url_for('explore', page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for('explore', page=tweets.prev_num) if tweets.has_prev else None
    return render_template(
        'explore.html', tweets=tweets.items, next_url=next_url, prev_url=prev_url
    )

