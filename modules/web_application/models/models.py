from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    social_login_provider = db.Column(db.String(50))
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.name}>"

class ScrapedData(db.Model):
    __tablename__ = 'scraped_data'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    scraped_metadata = db.Column(db.JSON)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ScrapedData {self.url}>"

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'content': self.content,
            'scraped_metadata': self.scraped_metadata,
            'created_at': self.created_at.isoformat(),
            'created_by_user_id': self.created_by_user_id
        }

class PromptLog(db.Model):
    __tablename__ = 'prompt_logs'
    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    generated_output = db.Column(db.Text, nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tokens_used = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<PromptLog {self.prompt_text[:20]}>"

    def to_dict(self):
        return {
            'id': self.id,
            'prompt_text': self.prompt_text,
            'generated_output': self.generated_output,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat(),
            'created_by_user_id': self.created_by_user_id
        }
