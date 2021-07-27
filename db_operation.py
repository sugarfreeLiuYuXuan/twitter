from flask import app
from twittor import db ,create_app
from twittor.models import User

app=create_app()
app.app_context().push()
User.query.all()
u4=User.query.get(4)
u5=User.query.get(5)



u4.followed.append(u5)
db.session.commit()

for u in u4.followed:
    print(u)