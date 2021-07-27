from datetime import datetime
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

from twittor import db, login_manager


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(120))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    tweets = db.relationship('Tweet', backref='author', lazy='dynamic')   #一对多

  

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),    #找关注了多少人
        secondaryjoin=(followers.c.followed_id == id),  #找有多少人关注我
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')    #多对多


    def __repr__(self):
        return 'id={}, username={}, email={}, password_hash={}'.format(
            self.id, self.username, self.email, self.password_hash
        )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self,size=80):
        md5_digest=md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://gravatar.loli.net/avatar/{}/?d=identicon&s={}".format(md5_digest,size)
    
    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "id={}, body={}, create_time={}, user_id={}".format(
            self.id, self.body, self.create_time, self.user_id
        )
