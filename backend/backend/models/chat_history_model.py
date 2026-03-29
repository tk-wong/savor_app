from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from backend.db_manager import db


class ChatHistoryModel(db.Model):
    __tablename__ = 'chat_history'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    user_id: db.Column = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt: db.Column = db.Column(db.Text, nullable=False)
    response: db.Column = db.Column(JSONB, nullable=False)
    chat_group_id: db.Column = db.Column(db.Integer, db.ForeignKey('chat_groups.id'), nullable=False)
    image_url: db.Column = db.Column(db.String(255), nullable=True)
    timestamp: db.Column = db.Column(db.DateTime(timezone=True), nullable=False,
                                     default=lambda: datetime.now(UTC), server_default=func.now())
    chat_group = db.relationship("ChatGroupModel",
                                 back_populates="chat_histories")

    def __repr__(self):
        return f'<ChatHistory id: {self.id}, user_id: {self.user_id}, prompt: {self.prompt}, response: {self.response}, timestamp: {self.timestamp}>'
