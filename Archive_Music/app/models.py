from app import db, login_manager
from flask_login import UserMixin

user_tracks = db.Table('user_tracks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', name='fk_user_tracks_user_id'), primary_key=True),
    db.Column('track_id', db.Integer, db.ForeignKey('track.id', name='fk_user_tracks_track_id'), primary_key=True),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id', name='fk_user_tracks_playlist_id'), primary_key=True)
)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spotify_id = db.Column(db.String(100), unique=True, nullable=False)
    user = db.relationship('User', back_populates="playlists")
    tracks = db.relationship('Track', secondary=user_tracks, primaryjoin='user_tracks.c.playlist_id == Playlist.id', secondaryjoin='user_tracks.c.track_id == Track.id', backref='playlists', lazy='dynamic')


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    spotify_id = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', secondary=user_tracks, back_populates="tracks")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tracks = db.relationship('Track', secondary=user_tracks, back_populates="users")
    playlists = db.relationship('Playlist', back_populates="user", lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))