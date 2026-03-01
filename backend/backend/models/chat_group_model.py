from backend.db_manager import db


class ChatGroupModel(db.Model):
    __tablename__ = 'chat_groups'
    id: db.Column = db.Column(db.Integer, primary_key=True)
    name: db.Column = db.Column(db.String(255), nullable=False, default='Unnamed')
    create_user_id: db.Column = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_histories = db.relationship('ChatHistoryModel', back_populates='chat_group', lazy=True,
                                     order_by='ChatHistoryModel.timestamp', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ChatGroup {self.name}, id: {self.id}>'
