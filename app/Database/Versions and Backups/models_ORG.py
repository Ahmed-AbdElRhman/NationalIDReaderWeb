from datetime import datetime

from hashlib import sha256
from app.Database import db, bcrypt

class AppSubscription(db.Model):
    __tablename__ = 'app_subscription'

    id = db.Column(db.Integer, primary_key=True)
    install_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_scans = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verification_hash = db.Column(db.String(64), nullable=False)
    
    def compute_hash(self, secret_key):
        data = f"{self.id}{self.install_date}{self.total_scans}{self.is_active}{self.last_modified}{secret_key}"
        return sha256(data.encode()).hexdigest()

class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# class AuditLog(db.Model):
#     __tablename__ = 'audit_log'

#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     action = db.Column(db.String(50), nullable=False)
#     details = db.Column(db.Text)
#     client_ip = db.Column(db.String(45))
#     user_agent = db.Column(db.Text)
#     admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))