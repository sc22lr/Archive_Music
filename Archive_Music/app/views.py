from flask import render_template, flash, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from app import app
from .forms import RegisterForm, LoginForm, NewPasswordForm, SearchForm, PlaylistForm, AddSongToPlaylistForm
from .models import db, User, Track, Playlist
from .spotify import sp, spotipy, sp_oauth

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    search_results = []
    users = User.query.all()
    if form.validate_on_submit():
        search = form.search.data
        try:
            results = sp.search(q=search, type='track,artist', limit=10)
            search_results = {
                'tracks': [
                    {
                        'name': track['name'],
                        'artist': ', '.join(artist['name'] for artist in track['artists']),
                        'url': track['external_urls']['spotify'],
                        'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None
                    }
                    for track in results['tracks']['items']
                ],
                'artists': [
                    {
                        'name': artist['name'],
                        'url': artist['external_urls']['spotify'],
                        'image': artist['images'][0]['url'] if artist['images'] else None
                    }
                    for artist in results['artists']['items']
                ]
            }
        except Exception as e:
            flash(f"Error during search: {e}", 'danger')

    return render_template('index.html', form=form, search_results=search_results,  users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))   
    if form.errors:
        flash('Form submission failed. Please check the fields and try again.', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('profile'))
    return render_template('login.html', form=form)

@app.route("/spotify_login")
def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = NewPasswordForm()
    user = User.query.filter_by(email=form.email.data).first()

    if form.validate_on_submit() and form.verify_email.data:
            if user:
                flash('Email verified. Please enter a new password.', 'success')
                return redirect(url_for('change_password'))
            else:
                flash('No account found with this email.', 'danger')
                return redirect(url_for('change_password'))

    if form.validate_on_submit() and form.reset_password.data:
            if user:
                user.password = form.new_password.data
                db.session.commit()
                flash('Password successfully updated.', 'success')
                return redirect(url_for('login'))
            else:
                flash('An error occurred. Please try again.', 'danger')
    return render_template('change_password.html', form=form, user=user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist_name = form.name.data
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
        new_playlist = Playlist(name=playlist_name, spotify_id=playlist['id'], user_id=current_user.id)
        db.session.add(new_playlist)
        db.session.commit()
        flash('Playlist created successfully!', 'success')
        return redirect(url_for('add_song_to_playlist', playlist_id=new_playlist.id))
    return render_template('create_playlist.html', form=form)

@app.route('/add_song_to_playlist/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def add_song_to_playlist(playlist_id):
    form = AddSongToPlaylistForm()
    playlist = Playlist.query.get(playlist_id)
    if form.validate_on_submit():
        song_query = form.song_query.data
        results = sp.search(q=song_query, type='track', limit=5)
        tracks = results['tracks']['items']
        if tracks:
            track_id = tracks[0]['id']
            sp.playlist_add_items(playlist.spotify_id, [track_id])
            flash(f'Song added to playlist: {tracks[0]["name"]}', 'success')
        else:
            flash('No results found for that song.', 'danger')
    return render_template('add_song_to_playlist.html', form=form, playlist=playlist)

@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    spot = spotipy.Spotify(auth=session['token_info']['access_token'])
    tracks = spot.current_user_top_tracks()
    return render_template('spotify_tracks.html', tracks=tracks['items'])

@app.route('/genre')
def genre():
    genres = ['pop', 'rock', 'hip-hop', 'jazz', 'classical', 'electronic', 'country']
    genre_songs = {}
    for genre in genres:
        try:
            results = sp.search(q=f'genre:{genre}', type='playlist', limit=1)
            if results.get('playlists') and results['playlists'].get('items'):
                playlist_id = results['playlists']['items'][0]['id']
                playlist_tracks = sp.playlist_tracks(playlist_id, limit=5)
                songs = []
                for track in playlist_tracks['items']:
                    track_info = track.get('track') 
                    if track_info and track_info.get('name') and track_info.get('artists'):
                        songs.append({
                            'name': track_info['name'],
                            'artist': ', '.join(artist['name'] for artist in track_info['artists']),
                            'url': track_info['external_urls'].get('spotify', '#'),
                            'album_cover': track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
                        })

                genre_songs[genre] = songs
        except Exception as e:
            print(f"Error processing genre {genre}: {e}")

    return render_template('genre.html', genres=genre_songs)

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    data = request.get_json()
    search_query = data.get('search', '').strip()
    suggestions = []
    if search_query:
        try:
            results = sp.search(q=search_query, type='track,artist', limit=5)
            suggestions = [
                track['name']
                for track in results.get('tracks', {}).get('items', [])
            ]
            suggestions.extend([
                artist['name']
                for artist in results.get('artists', {}).get('items', [])
            ])
        except Exception as e:
            print(f"Error fetching Spotify suggestions: {e}")
    return jsonify({'status': 'OK', 'suggestions': suggestions})

