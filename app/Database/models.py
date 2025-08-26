from datetime import datetime, timezone
from typing import  Dict, Any
from hashlib import sha256
import bcrypt

class AppSubscription:
    """Represents an application subscription"""
    
    def __init__(self, id: int = 1, install_date: datetime = None, 
                 total_scans: int = 0, is_active: bool = True, 
                 last_modified: datetime = None, verification_hash: str = ""):
        self.id = id
        self.install_date = install_date or datetime.now(timezone.utc)
        self.total_scans = total_scans
        self.is_active = is_active
        self.last_modified = last_modified or datetime.now(timezone.utc)
        self.verification_hash = verification_hash
    
    def compute_hash(self, secret_key: str) -> str:
        """Compute the verification hash for the subscription with detailed debugging"""
        # Convert all values to consistent string representations
        install_date_str = self.install_date.isoformat() if isinstance(self.install_date, datetime) else str(self.install_date)
        last_modified_str = self.last_modified.isoformat() if isinstance(self.last_modified, datetime) else str(self.last_modified)
        
        data = f"{self.id}{install_date_str}{self.total_scans}{self.is_active}{last_modified_str}{secret_key}"
        
        return sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'install_date': self.install_date,
            'total_scans': self.total_scans,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'verification_hash': self.verification_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSubscription':
        """Create object from dictionary with proper type conversion"""
        # Convert string dates back to datetime objects
        install_date = data.get('install_date')
        if isinstance(install_date, str):
            install_date = datetime.fromisoformat(install_date.replace('Z', '+00:00'))
        
        last_modified = data.get('last_modified')
        if isinstance(last_modified, str):
            last_modified = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
        
        # Ensure boolean values are properly converted
        is_active = data.get('is_active', True)
        if isinstance(is_active, int):
            is_active = bool(is_active)
        elif isinstance(is_active, str):
            is_active = is_active.lower() in ('true', '1', 'yes')
        
        return cls(
            id=data.get('id', 1),
            install_date=install_date,
            total_scans=data.get('total_scans', 0),
            is_active=is_active,
            last_modified=last_modified,
            verification_hash=data.get('verification_hash', '')
        )
    
    def __repr__(self):
        return f"AppSubscription(id={self.id}, install_date={self.install_date}, total_scans={self.total_scans}, is_active={self.is_active}), last_modified={self.last_modified}, verification_hash={self.verification_hash})"

class AdminUser:
    """Represents an admin user"""
    
    def __init__(self, id: int = 1, username: str = "", password_hash: str = "", 
                 created_at: datetime = None, last_login: datetime = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_login = last_login
    
    def set_password(self, password: str):
        """Set the password hash"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminUser':
        """Create object from dictionary"""
        return cls(
            id=data.get('id', 1),
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            created_at=data.get('created_at'),
            last_login=data.get('last_login')
        )
    
    def __repr__(self):
        return f"AdminUser(id={self.id}, username={self.username}, created_at={self.created_at})"
