import sqlite3
import os
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import bcrypt
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more details
logger = logging.getLogger(__name__)

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
        
        logger.debug(f"Hash computation data: {data}")
        logger.debug(f"Data types - id: {type(self.id)}, install_date: {type(self.install_date)}, "
                    f"total_scans: {type(self.total_scans)}, is_active: {type(self.is_active)}, "
                    f"last_modified: {type(self.last_modified)}")
        
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
        return f"AppSubscription(id={self.id}, install_date={self.install_date}, total_scans={self.total_scans}, is_active={self.is_active})"

class OCRDB:
    def __init__(self, db_path: str = "OCRDB.db"):
        self.db_path = db_path
        self.connection = None
        self.secret_key = os.environ.get("APP_SECRET_KEY", "default_secret_key_change_in_production")
        self.subscription_expiry_days = 365
        self.max_scans = 100
        self.init_db()
    
    def get_connection(self):
        """Get a database connection, reconnecting if necessary"""
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self._register_datetime_adapters()
            # Test the connection
            self.connection.execute("SELECT 1")
            return self.connection
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            # Connection is closed or invalid, reopen it
            try:
                self.connection.close()
            except:
                pass
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self._register_datetime_adapters()
            return self.connection
    
    def _register_datetime_adapters(self):
        """Register adapters for datetime objects for Python 3.12+ compatibility"""
        def adapt_datetime_utc(dt):
            return dt.isoformat()
        
        def convert_datetime_utc(timestamp):
            if isinstance(timestamp, bytes):
                timestamp = timestamp.decode('utf-8')
            # Handle both with and without timezone info
            if 'Z' in timestamp:
                timestamp = timestamp.replace('Z', '+00:00')
            return datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
        
        sqlite3.register_adapter(datetime, adapt_datetime_utc)
        sqlite3.register_converter("datetime", convert_datetime_utc)
    
    def _get_current_utc_datetime(self):
        """Get current UTC datetime with timezone awareness"""
        return datetime.now(timezone.utc)
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        
        # Create app_subscription table (only one row)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS app_subscription (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                install_date DATETIME NOT NULL,
                total_scans INTEGER NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                last_modified DATETIME NOT NULL,
                verification_hash TEXT NOT NULL
            )
        ''')
        
        conn.commit()
    
    def get_app_subscription(self) -> Optional[AppSubscription]:
        """Get the app subscription as an object with detailed debugging"""
        try:
            conn = self.get_connection()
            cursor = conn.execute("SELECT * FROM app_subscription WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                subscription_dict = dict(row)
                logger.debug(f"Raw database row: {dict(row)}")
                
                # Convert data types properly
                for field in ['install_date', 'last_modified']:
                    if field in subscription_dict:
                        value = subscription_dict[field]
                        logger.debug(f"Field {field}: {value} (type: {type(value)})")
                        
                        if isinstance(value, str):
                            # Handle ISO format strings
                            if 'Z' in value:
                                value = value.replace('Z', '+00:00')
                            subscription_dict[field] = datetime.fromisoformat(value)
                
                # Handle boolean conversion
                if 'is_active' in subscription_dict:
                    is_active = subscription_dict['is_active']
                    if isinstance(is_active, int):
                        subscription_dict['is_active'] = bool(is_active)
                    elif isinstance(is_active, str):
                        subscription_dict['is_active'] = is_active.lower() in ('true', '1', 'yes', 't')
                
                subscription = AppSubscription.from_dict(subscription_dict)
                logger.debug(f"Created subscription object: {subscription}")
                logger.debug(f"Subscription object types - id: {type(subscription.id)}, "
                            f"install_date: {type(subscription.install_date)}, "
                            f"total_scans: {type(subscription.total_scans)}, "
                            f"is_active: {type(subscription.is_active)}, "
                            f"last_modified: {type(subscription.last_modified)}")
                
                return subscription
            return None
        except Exception as e:
            logger.error(f"Error getting app subscription: {e}")
            return None
    
    def save_app_subscription(self, subscription: AppSubscription) -> bool:
        """Save the app subscription to database"""
        try:
            conn = self.get_connection()
            
            # Update the last_modified timestamp
            subscription.last_modified = self._get_current_utc_datetime()
            
            # Compute verification hash
            subscription.verification_hash = subscription.compute_hash(self.secret_key)
            logger.debug(f"Computed hash: {subscription.verification_hash}")
            
            # Check if subscription exists
            existing = self.get_app_subscription()
            
            if existing:
                # Update existing subscription
                conn.execute('''
                    UPDATE app_subscription 
                    SET install_date = ?, total_scans = ?, is_active = ?, 
                        last_modified = ?, verification_hash = ?
                    WHERE id = 1
                ''', (subscription.install_date, subscription.total_scans, 
                      subscription.is_active, subscription.last_modified, 
                      subscription.verification_hash))
            else:
                # Insert new subscription
                conn.execute('''
                    INSERT INTO app_subscription 
                    (id, install_date, total_scans, is_active, last_modified, verification_hash)
                    VALUES (1, ?, ?, ?, ?, ?)
                ''', (subscription.install_date, subscription.total_scans, 
                      subscription.is_active, subscription.last_modified, 
                      subscription.verification_hash))
            
            conn.commit()
            logger.info("App subscription saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving app subscription: {e}")
            return False
    
    def create_app_subscription(self, install_date: datetime = None) -> Optional[AppSubscription]:
        """Create a new app subscription"""
        subscription = AppSubscription(
            install_date=install_date or self._get_current_utc_datetime(),
            total_scans=0,
            is_active=True
        )
        
        if self.save_app_subscription(subscription):
            return subscription
        return None
    
    def verify_subscription(self) -> bool:
        """Verify the subscription integrity with detailed debugging"""
        try:
            subscription = self.get_app_subscription()
            if not subscription:
                logger.warning("No subscription found to verify")
                return False
            
            # Get the stored hash
            stored_hash = subscription.verification_hash
            logger.debug(f"Stored hash: {stored_hash}")
            
            if not stored_hash or stored_hash == "placeholder":
                logger.warning("Invalid or placeholder hash found")
                return False
            
            # Compute what the hash should be
            computed_hash = subscription.compute_hash(self.secret_key)
            logger.debug(f"Computed hash: {computed_hash}")
            
            # Debug: Check what data is being hashed
            install_date_str = subscription.install_date.isoformat() if isinstance(subscription.install_date, datetime) else str(subscription.install_date)
            last_modified_str = subscription.last_modified.isoformat() if isinstance(subscription.last_modified, datetime) else str(subscription.last_modified)
            
            debug_data = f"{subscription.id}{install_date_str}{subscription.total_scans}{subscription.is_active}{last_modified_str}{self.secret_key}"
            logger.debug(f"Debug hash data: {debug_data}")
            
            # Compare the hashes
            if computed_hash == stored_hash:
                logger.info("Subscription verification passed")
                return True
            else:
                logger.warning("Subscription verification failed")
                logger.warning(f"Computed hash: {computed_hash}")
                logger.warning(f"Stored hash: {stored_hash}")
                logger.warning(f"Hash match: {computed_hash == stored_hash}")
                
                # Additional debugging: Check individual components
                logger.warning("=== COMPONENT ANALYSIS ===")
                logger.warning(f"ID: {subscription.id} (type: {type(subscription.id)})")
                logger.warning(f"Install date: {subscription.install_date} (type: {type(subscription.install_date)})")
                logger.warning(f"Total scans: {subscription.total_scans} (type: {type(subscription.total_scans)})")
                logger.warning(f"Is active: {subscription.is_active} (type: {type(subscription.is_active)})")
                logger.warning(f"Last modified: {subscription.last_modified} (type: {type(subscription.last_modified)})")
                
                return False
        except Exception as e:
            logger.error(f"Error verifying subscription: {e}")
            return False
    
    def validate_subscription(self) -> bool:
        """
        Validate that the subscription is active, not expired, and within scan limits
        Returns True if valid, False otherwise
        """
        # First verify the subscription integrity
        if not self.verify_subscription():
            logger.warning("Subscription verification failed")
            return False
        
        subscription = self.get_app_subscription()
        if not subscription:
            logger.warning("No subscription found")
            return False
        
        # Check if subscription is active
        if not subscription.is_active:
            logger.warning("Subscription is not active")
            return False
        
        # Check if subscription is expired (older than 1 year)
        expiry_date = subscription.install_date + timedelta(days=self.subscription_expiry_days)
        if self._get_current_utc_datetime() > expiry_date:
            logger.warning(f"Subscription expired on {expiry_date}")
            return False
        
        # Check if scan limit exceeded
        if subscription.total_scans >= self.max_scans:
            logger.warning(f"Scan limit exceeded: {subscription.total_scans}/{self.max_scans}")
            return False
        
        logger.info("Subscription validation passed")
        return True
    
    def reset_subscription_for_testing(self):
        """Reset the subscription for testing purposes"""
        conn = self.get_connection()
        conn.execute("DELETE FROM app_subscription WHERE id = 1")
        conn.commit()
        logger.info("Subscription reset for testing")
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


# Debugging and testing function
def debug_subscription_verification():
    """Function to debug subscription verification issues"""
    db = OCRDB()
    
    # Reset subscription for clean testing
    db.reset_subscription_for_testing()
    
    # Create a new subscription
    print("Creating new subscription...")
    subscription = db.create_app_subscription()
    
    if subscription:
        print(f"Created subscription: {subscription}")
        
        # Immediately verify the subscription
        print("Verifying subscription immediately after creation...")
        verification_result = db.verify_subscription()
        print(f"Verification result: {verification_result}")
        
        # Check validation
        print("Validating subscription...")
        validation_result = db.validate_subscription()
        print(f"Validation result: {validation_result}")
        
        # Get the subscription again and check hash
        print("Retrieving subscription from database...")
        retrieved_subscription = db.get_app_subscription()
        if retrieved_subscription:
            print(f"Retrieved subscription: {retrieved_subscription}")
            print(f"Stored hash: {retrieved_subscription.verification_hash}")
            
            # Manually compute hash
            manual_hash = retrieved_subscription.compute_hash(db.secret_key)
            print(f"Manually computed hash: {manual_hash}")
            print(f"Hash match: {manual_hash == retrieved_subscription.verification_hash}")
    
    db.close()


if __name__ == "__main__":
    # Run the debugging function
    debug_subscription_verification()