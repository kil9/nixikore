import datetime

from config import db


class Config(db.Model):
    __tablename__ = 'config'
    key = db.Column(db.String(32), primary_key=True)
    value = db.Column(db.String(1024))
    modified_at = db.Column(db.DateTime, default=datetime.datetime.now)


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512))


class Follower(db.Model):
    __tablename__ = 'followers'

    id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(256))
    mention_id = db.Column(db.String(256))
    is_blocked = db.Column(db.Integer, default=0)

    added_at = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.datetime.now)


class PendingTweet(db.Model):
    __tablename__ = 'pending_tweets'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    reply_id = db.Column(db.String(256), default=None)
    image_keyword = db.Column(db.String(1024), default=None)
    added_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        form = (self.id, self.content, self.image_keyword)
        return "<PendingTweet[%r] '%r' %r)>" % form


class PeriodicScript(db.Model):
    __tablename__ = 'periodic_scripts'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    is_blocked = db.Column(db.Integer, default=0)
    image_keyword = db.Column(db.String(1024), default=None)

    added_by = db.Column(db.String(512), default='system')
    added_at = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_by = db.Column(db.String(512), default='system')
    modified_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        form = (self.id, self.content)
        return "<PeriodicScript[%r] %r)>" % form


class ResponseScript(db.Model):
    __tablename__ = 'response_scripts'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(256))
    content = db.Column(db.Text)
    image_keyword = db.Column(db.String(1024), default=None)

    is_blocked = db.Column(db.Integer, default=0)

    added_by = db.Column(db.String(512), default='system')
    added_at = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_by = db.Column(db.String(512), default='system')
    modified_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        form = (self.id, self.content)
        return "<ResponseScript[%r] %r)>" % form


class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(256))
    content = db.Column(db.Text)
    is_blocked = db.Column(db.Integer, default=0)

    added_by = db.Column(db.String(512), default='system')
    added_at = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_by = db.Column(db.String(512), default='system')
    modified_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        form = (self.id, self.category, self.content)
        return "<Word[%r] %r / %r)>" % form
