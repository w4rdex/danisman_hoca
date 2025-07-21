from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    publications = db.Column(db.Text)  # birleştirilmiş başlık/metin

    def __repr__(self):
        return f'<Professor {self.name}>'
