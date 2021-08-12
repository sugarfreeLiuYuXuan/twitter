from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError,Length

from twittor.models.user import  User
from twittor.models.tweets import Tweet


class LoginForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("用户名" ,validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    remember_me = BooleanField("记住我")
    submit = SubmitField('登陆')


class RegisterForm(FlaskForm):
    username = StringField("用户名" ,validators=[DataRequired()])
    email = StringField("邮箱地址", validators=[DataRequired(), Email()])
    password = PasswordField("设置密码", validators=[DataRequired()])
    password2 = PasswordField(
        "确认密码", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已被占用')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已被注册')

class EditProfileForm(FlaskForm):
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=120)])
    submit = SubmitField('保存')


class TweetForm(FlaskForm):
    tweet = TextAreaField('发文',validators=[DataRequired(),Length(min=0, max=280)])
    submit = SubmitField('OK')

class PasswdResetRequestForm(FlaskForm):
    email = StringField("邮件地址",validators=[DataRequired(),Email()])
    submit = SubmitField('重设密码')

    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if not user:
            raise ValidationError(
                '此邮箱没有用来注册任何账号'
            )

class PasswdResetForm(FlaskForm):
    password = PasswordField("设置密码", validators=[DataRequired()])
    password2 = PasswordField(
        "重设密码", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('确认修改')