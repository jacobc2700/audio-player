from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from errors.handlers import errors
import pafy, random
import pytube
import os

from youtube_methods import getLikePercentage, getDislikePercentage, getReactionPercentage, getViewsPerDay
from youtube_methods import getLikesPerDay, getDislikesPerDay, getDaysPassedFromUploadDate

# Configure app.
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Make db.
db = SQLAlchemy(app)

# Register blueprint for the common errors.
app.register_blueprint(errors)

# Audio model for database.
class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(20))
    song_name = db.Column(db.String(20))
    video_url = db.Column(db.String(20))
    embedded_link = db.Column(db.String(20))

    def __repr__(self):
        return f"Audio('{self.id}','{self.artist_name}', '{self.song_name}', '{self.video_url}', '{self.embedded_link}')"

@app.route('/audio/<id>/')
def audio(id):
    audio = Audio.query.filter_by(id=int(id)).first()
    return render_template('audio.html', audio=audio)

@app.route('/player/<id>/')
def player(id):
    audio = Audio.query.filter_by(id=int(id)).first()
    link = audio.video_url
    video_id = link[-11:]
    return render_template('player.html', audio=audio, link=link, video_id=video_id)

@app.route('/clear/')
def clear():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home'))

@app.route('/update/<id>/', methods=['POST'])
def update(id):
    audio = Audio.query.filter_by(id=int(id)).first()
    new_artist_name = request.form['artist_name']
    new_song_name = request.form['song_name']
    new_video_url = request.form['youtube_url']
    if is_youtube_url_valid(new_video_url) == True and new_artist_name != "" and new_song_name != "" and new_artist_name.isspace() == False and new_song_name.isspace() == False:
        audio.artist_name = new_artist_name
        audio.song_name = new_song_name
        audio.video_url = new_video_url
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('audio.html', audio=audio, valid_information=False)

@app.route('/autoplay/')
def autoplay():
    audios = Audio.query.all()
    video_ids = []
    for audio in audios:
        video_id = audio.video_url[-11:]
        video_ids.append(video_id)
    video_id_string = ",".join(video_ids)
    return render_template('autoplay.html', video_id_string=video_id_string, title="Autoplay")

@app.route('/shuffleplay/')
def shuffleplay():
    audios = Audio.query.all()
    video_ids = []
    for audio in audios:
        video_id = audio.video_url[-11:]
        video_ids.append(video_id)
    random.shuffle(video_ids)
    video_id_string = ",".join(video_ids)
    return render_template('shuffleplay.html', video_id_string=video_id_string, title="Shuffleplay")

@app.route('/download/')
def download():
    audios = Audio.query.all()
    return render_template('download.html', audios=audios, title="Download")

@app.route('/home/')
def home():
    audios = Audio.query.all()
    return render_template('home.html', title='Home', audios=audios)

@app.route('/new/')
def new():
    return render_template('new.html', title='New')

@app.route('/statistics/')
def statistics():
    pafy_video_objects = []
    audios = Audio.query.all()
    like_percentages = []
    dislike_percentages = []
    reaction_percentages = []
    views_per_day = []
    likes_per_day = []
    dislikes_per_day = []
    days_passed_from_upload_date = []

    for audio in audios:
        pafy_video_objects.append(pafy.new(audio.video_url))

    for v in pafy_video_objects:    
        like_percentages.append(getLikePercentage(v.likes, v.dislikes))
        dislike_percentages.append(getDislikePercentage(v.likes, v.dislikes))
        reaction_percentages.append(getReactionPercentage(v.viewcount, v.likes, v.dislikes))
        views_per_day.append(getViewsPerDay(v.viewcount, v.published))
        likes_per_day.append(getLikesPerDay(v.likes, v.published))
        dislikes_per_day.append(getDislikesPerDay(v.dislikes, v.published))
        days_passed_from_upload_date.append(getDaysPassedFromUploadDate(v.published))

    return render_template('statistics.html', title='Statistics', 
        audios=audios, pafy_video_objects=pafy_video_objects, length=len(pafy_video_objects), like_percentages=like_percentages,
        dislike_percentages=dislike_percentages, reaction_percentages=reaction_percentages, views_per_day=views_per_day, 
        likes_per_day=likes_per_day, dislikes_per_day=dislikes_per_day, days_passed_from_upload_date=days_passed_from_upload_date)

@app.route('/add/', methods=['POST'])
def add():
    artist_name = request.form['artist_name']
    song_name = request.form['song_name']
    video_url = request.form['youtube_url']
    if is_youtube_url_valid(video_url) == True and artist_name != "" and song_name != "" and artist_name.isspace() == False and song_name.isspace() == False:
        embedded_link = "https://www.youtube.com/embed/"
        youtube_code = video_url[-11:]
        embedded_link += youtube_code + "?rel=0&amp;showinfo=0"
        audio = Audio(artist_name=artist_name, song_name=song_name, video_url=video_url, embedded_link=embedded_link)
        db.session.add(audio)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('new.html', valid_information=False)

@app.route('/send/', methods=['POST'])
def send():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email_address = request.form['email_address']
    subject = request.form['subject']
    message = request.form['message']
    return redirect(url_for('home'))

@app.route('/download-mp4/<id>/')
def download_mp4(id):
    audio = Audio.query.get(id)
    link = audio.video_url
    yt = pytube.YouTube(link)
    stream = yt.streams.first()
    stream.download()
    return redirect(url_for('home'))

@app.route('/download-captions/<id>/')
def download_captions(id):
    audio = Audio.query.get(id)
    link = audio.video_url
    os.system('python captions.py ' + link)
    return redirect(url_for('home'))

@app.route('/download-mp3/<id>/')
def download_mp3(id):
    audio = Audio.query.get(id)
    link = audio.video_url
    os.system("youtube-dl -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 " + link)
    return redirect(url_for('home'))

def is_youtube_url_valid(video_url):
    try:
        video = pafy.new(video_url)
    except:
        return False
    return True

@app.route('/remove/<id>/')
def remove(id):
    db.session.query(Audio).filter_by(id=int(id)).delete()
    db.session.commit()
    return redirect(url_for('home'))

# Run application in debug mode.
if __name__ == '__main__':
    app.run(debug=True)