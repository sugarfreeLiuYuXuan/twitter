import os

config_path = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(config_path, 'twittor.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'abc123'
    TWEET_PER_PAGE = 3

    MAIL_DEBU=True
    MAIL_SUPPRESS_SEND=False
    MAIL_SERVER='smtp.qq.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USE_TLS=False
    MAIL_DEFAULT_SENDER='562048502@qq.com'
    MAIL_USERNAME='562048502@qq.com'
    MAIL_PASSWORD='horupuixraecbdec'

    