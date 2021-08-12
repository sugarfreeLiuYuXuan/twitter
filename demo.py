from twittor import db,create_app
from twittor.models.user import User
from twittor.models.tweets import Tweet


#通过terminal简单操作数据库
app = create_app()
app.app_context().push()
User.query.all()

t1 = Tweet(body="my name is xxx",user_id = 1)
db.session.add(t1)
db.session.commit()
User.query.all()
