from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length 

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(max=50)])
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    
class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])

class NewPasswordForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(max=50)])
    new_password = PasswordField('new_password', validators=[DataRequired(), Length(min=6)])
    verify_email = SubmitField('verify_email', name='Verify Email')
    reset_password = SubmitField('reset_password', name='Reset Password')

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired(), Length(max=50)])
    submit_search = SubmitField('submit_search', name='Search')

class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name', validators=[DataRequired()])
    create_playlist = SubmitField('Create Playlist', name='Create Playlist')

class AddSongToPlaylistForm(FlaskForm):
    song_query = StringField('Search for a Song', validators=[DataRequired()])
    submit = SubmitField('Search and Add Song')
