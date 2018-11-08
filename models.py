from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, )
    star = db.Column(db.Float)
    vote = db.Column(db.Float)
    img = db.Column(db.String)
    
    def __init__(self, title, star, vote, img):
        self.title = title
        self.star = star
        self.vote = vote
        self.img = img
    