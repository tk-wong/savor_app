from sqlalchemy.dialects.postgresql import JSONB

from backend.db_manager import db


class ChatHistoryModel(db.Model):
    __tablename__ = 'chat_history'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    user_id: db.Column = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message: db.Column = db.Column(JSONB, nullable=False)
    chat_group_id: db.Column = db.Column(db.Integer, db.ForeignKey('chat_groups.id'), nullable=False)
    image_url: db.Column = db.Column(db.String(255), nullable=True)
    timestamp: db.Column = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<ChatHistory user_id: {self.user_id}, message: {self.message}, timestamp: {self.timestamp}, id: {self.id}>'
