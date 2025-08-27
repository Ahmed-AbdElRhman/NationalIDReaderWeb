import sqlite3
import os
# import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.Database.models import AppSubscription, AdminUser
# Load environment variables from .env file if it exists
from dotenv import load_dotenv,set_key
load_dotenv()  
# import logging as logger

# Set up logging
from app.utils.logger import get_logger
# from run import app
logger = get_logger(__name__)

class OCRDB:
    def __init__(self, db_path: str = os.environ.get("DB_NAME", "instance/OCRDB.db")):
        self.db_path = db_path
        self.connection = None
        self.secret_key = os.getenv('SUBSCRIPTION_SECRET_KEY')
        self.subscription_expiry_days = int(os.getenv('SUBSCRIPTION_EXPIRY_DAYS', 365))  # Default to 1 year
        self.max_scans = int(os.getenv('MAX_SCANS', 11))  # Default to 1000 scans
        self.subscription = None  # Cached subscription object
        self.adminUser = None  # Cached admin user object
        # Initialize the database and create initial subscription and admin user
        self.init_db()
        self.createNew_app_subscription()
        self.createNew_admin_user(
            os.getenv('ADMIN_USERNAME', 'admin'),
            os.getenv('ADMIN_PASSWORD', 'P@ssw0rd')  # Default admin password for testing
        )  
        logger.info(f"Database initialized at {self.db_path}, expiry days: {self.subscription_expiry_days}, max scans: {self.max_scans}")
    
    # Get a database connection, reconnecting if necessary
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
    # Register datetime adapters for Python 3.12+ compatibility
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
    # Get current UTC datetime with timezone awareness
    def _get_current_utc_datetime(self):
        """Get current UTC datetime with timezone awareness"""
        return datetime.now()
    # Initialize the database with required tables
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
        
        # Create admin_users table (only one row)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                last_login DATETIME
            )
        ''')
        
        conn.commit()
    
    # ---------- Subscription business logic methods ----------
    def get_app_subscription(self) -> Optional[AppSubscription]:
        """Get the app subscription as an object with detailed debugging"""
        logger.debug("Fetching app subscription from database or cache")
        if self.subscription:
            logger.debug(f"Returning cached subscription: {self.subscription}")
            return self.subscription
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
            # print(f"NEW Computed hash: {subscription.verification_hash}")  # Debugging print statement
            conn.execute('''
                UPDATE app_subscription 
                SET install_date = ?, total_scans = ?, is_active = ?, 
                    last_modified = ?, verification_hash = ?
                WHERE id = 1
            ''', (subscription.install_date, subscription.total_scans, 
                    subscription.is_active, subscription.last_modified, 
                    subscription.verification_hash))
            
            conn.commit()
            logger.info("App subscription saved successfully")
            self.subscription = subscription  # Cache the updated subscription
            return True
        except Exception as e:
            logger.error(f"Error save app subscription: {e}")
            return False
    # Create a new app subscription
    def createNew_app_subscription(self, install_date: datetime = None) -> Optional[AppSubscription]:
        """Create a new app subscription"""
        self.subscription = self.get_app_subscription()
        if self.subscription:
            logger.warning("Subscription already exists, not creating a new one")
            return self.subscription
        # Create a new subscription with current date and reset scan count
        subscription = AppSubscription(
            install_date=install_date or self._get_current_utc_datetime(),
            total_scans=0,
            is_active=True
        )
        try:
            conn = self.get_connection()
            # Update the last_modified timestamp
            subscription.last_modified = self._get_current_utc_datetime()
            # Compute verification hash
            subscription.verification_hash = subscription.compute_hash(self.secret_key)
            # Update existing subscription
            conn.execute('''
                INSERT INTO app_subscription 
                (id, install_date, total_scans, is_active, last_modified, verification_hash)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (subscription.install_date, subscription.total_scans, 
                    subscription.is_active, subscription.last_modified, 
                    subscription.verification_hash))
            conn.commit()
            logger.info("New App subscription Created successfully")
            self.subscription = subscription  # Cache the new subscription
            return subscription
        except Exception as e:
            logger.error(f"Error creating new app subscription: {e}")
            return None
        
    # Verify the subscription integrity Hashing
    def verify_subscription(self) -> bool:
        """Verify the subscription integrity Hashing"""
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
    
    # Validate the subscription status
    def validate_subscription(self) -> tuple[bool, Optional[str]]:
        """
        Validate that the subscription is active, not expired, and within scan limits
        Returns True if valid, False otherwise
        """
        warningMSG=None
        subscription = self.get_app_subscription()
    
        # Check if subscription is active
        if not subscription.is_active:
            logger.warning("Subscription is not active")
            return False,"Subscription is not active"
        
        # First verify the subscription integrity
        if not self.verify_subscription():
            logger.warning("Subscription verification failed")
            self.deActivate_subscription()  # Deactivate if verification fails
            return False,"Subscription verification failed"
        
        
        if not subscription:
            logger.warning("No subscription found")
            self.deActivate_subscription()  # Deactivate if no subscription found
            return False,"No subscription found"
        
        
        # Check if subscription is expired (older than 1 year)
        expiry_date = subscription.install_date + timedelta(days=self.subscription_expiry_days)
        if self._get_current_utc_datetime() > expiry_date:
            logger.warning(f"Subscription expired on {expiry_date}")
            self.deActivate_subscription()  # Deactivate if expired
            return False,f"Subscription expired on {expiry_date}"
        
        # Check if scan limit exceeded
        if subscription.total_scans >= self.max_scans:
            logger.warning(f"Scan limit exceeded: {subscription.total_scans}/{self.max_scans}")
            self.deActivate_subscription()  # Deactivate if scan limit exceeded
            return False,f"Scan limit exceeded: {subscription.total_scans}/{self.max_scans}"
        
        # Check if subscription is nearing expiry or scan limit
        if self._get_current_utc_datetime() > expiry_date+ timedelta(days=30):
            logger.warning(f"Subscription is nearing expiry: {expiry_date}")
            warningMSG=f"Subscription is nearing expiry: {expiry_date}"

        if subscription.total_scans >= self.max_scans-1000:
            logger.warning(f"Subscription is nearing scan limit: {subscription.total_scans}/{self.max_scans}")
            warningMSG=f"Subscription is nearing scan limit: {subscription.total_scans}/{self.max_scans}"

        logger.info("Subscription validation passed")
        return True,warningMSG
    
    def deActivate_subscription(self) -> bool:
        return True
        """Deactivate the subscription"""
        subscription = self.get_app_subscription()
        if not subscription:
            logger.warning("No subscription found to increment")
            return False
        
        subscription.is_active = False
        return self.save_app_subscription(subscription)
    
    def increment_scan_count(self, validateRequired:bool = True) -> tuple[bool, Optional[str]]:
        """Increment the total scan count by 1"""
        saveMSG=None
        if validateRequired:
            is_valid, MSG = self.validate_subscription()
            if not is_valid:
                saveMSG=f"Subscription validation failed: {MSG}"
                logger.warning(saveMSG)
                return False,saveMSG
            elif MSG:
                saveMSG=f"Subscription validation warning: {MSG}"
                logger.warning(saveMSG) 
        subscription = self.get_app_subscription()
        if not subscription:
            logger.warning("No subscription found to increment")
            return False,"No subscription found to increment"
        
        subscription.total_scans += 1
        return self.save_app_subscription(subscription),saveMSG
    
    def renew_subscription(self,MAX_SCANS,subscription_expiry_days) -> Optional[AppSubscription]:
        """Renew the subscription by creating a new one"""
        # Create a new subscription with current date and reset scan count
        new_subscription = AppSubscription(
            install_date=self._get_current_utc_datetime(),
            total_scans=0,
            is_active=True
        )
        #Udate the env file with new values
        try:
            # Update the value in the .env file
            dotenv_path = os.path.join(os.getcwd(), '.env')
            set_key(dotenv_path, "MAX_SCANS", str(MAX_SCANS))
            set_key(dotenv_path, "SUBSCRIPTION_EXPIRY_DAYS", str(subscription_expiry_days))
            logger.info(f"Updated SUBSCRIPTION_EXPIRY_DAYS,MAX_SCANS to {subscription_expiry_days}:{MAX_SCANS} in {dotenv_path}")
            self.subscription_expiry_days = subscription_expiry_days
            self.max_scans = MAX_SCANS
        except Exception as e:
            raise Exception(f"Error updating .env file: {e}")      
        
        if self.save_app_subscription(new_subscription):
            logger.info("Subscription renewed successfully")
            return new_subscription
        else:
            logger.error("Failed to renew subscription")
            return None
    def get_subscription_status(self):
        """Get the current subscription status"""
        subscription = self.get_app_subscription()
        if not subscription:
            logger.warning("No subscription found")
            return None
        subscriptionDict = subscription.to_dict()
        subscriptionDict["expiry_days"] = self.subscription_expiry_days
        subscriptionDict["expiry_date"] = (subscription.install_date + timedelta(days=self.subscription_expiry_days)).isoformat()
        subscriptionDict["max_scans"] = self.max_scans
        return subscriptionDict
    
    # ----------- Admin user management methods -----------
    # Get the admin user as an object
    def get_admin_user(self) -> Optional[AdminUser]:
        """Get the admin user as an object"""
        if self.adminUser:
            logger.debug(f"Returning cached admin user: {self.adminUser}")
            return self.adminUser 
        try:
            conn = self.get_connection()
            cursor = conn.execute("SELECT * FROM admin_users WHERE id = 1")
            row = cursor.fetchone()
            if row:
                admin_dict = dict(row)
                # Convert string dates back to datetime objects if needed
                for date_field in ['created_at', 'last_login']:
                    if date_field in admin_dict and isinstance(admin_dict[date_field], str):
                        admin_dict[date_field] = datetime.fromisoformat(admin_dict[date_field])
                return AdminUser.from_dict(admin_dict)
            return None
        except Exception as e:
            logger.error(f"Error getting admin user: {e}")
            return None
    
    def save_admin_user(self, admin: AdminUser) -> bool:
        """Save the admin user to database"""
        try:
            conn = self.get_connection()
            # Update admin
            conn.execute('''
                    UPDATE admin_users 
                    SET username = ?, password_hash = ?, created_at = ?, last_login = ?
                    WHERE id = 1
                ''', (admin.username, admin.password_hash, admin.created_at, admin.last_login))
            conn.commit()
            logger.info("Admin user Updated successfully")
            self.adminUser = admin  # Cache the saved admin user
            return True
        except Exception as e:
            logger.error(f"Error Updated admin user: {e}")
            return False
    
    def createNew_admin_user(self, username: str, password: str) -> Optional[AdminUser]:
        """Create a new admin user"""
        if not username or not password:
            logger.error("Username and password must be provided to create an admin user")
            return None
        # Check if admin user already exists
        self.adminUser = self.get_admin_user()
        if self.adminUser:
            logger.warning("Admin user already exists, not creating a new one")
            return self.adminUser
        # Create a new admin user
        logger.info(f"Creating new admin user with username: {username}")
        admin = AdminUser(username=username)
        admin.set_password(password)
        try:
            conn = self.get_connection()
            conn = self.get_connection()
            conn.execute('''
                        INSERT INTO admin_users 
                        (id, username, password_hash, created_at, last_login)
                        VALUES (1, ?, ?, ?, ?)
                    ''', (admin.username, admin.password_hash, admin.created_at, admin.last_login))
                
            conn.commit()
            self.adminUser = admin  # Cache the new admin user
            logger.info("Admin user saved successfully")
            return admin
        except sqlite3.IntegrityError as e:
            logger.error(f"Admin user creation failed due to integrity error: {e}")
            return None
    
    def login_admin_user(self, username: str, password: str) -> Optional[AdminUser]:
        """Login the admin user and update last login time"""
        admin = self.get_admin_user()
        if not admin:
            logger.warning("No admin user found to login")
            return None
        
        if admin.username != username:
            logger.warning("Username does not match")
            return None
        
        if not admin.check_password(password):
            logger.warning("Password does not match")
            return None
        
        # Update last login time
        admin.last_login = self._get_current_utc_datetime()
        if self.save_admin_user(admin):
            logger.info("Admin user logged in successfully")
            return admin
        else:
            logger.error("Failed to update last login time for admin user")
            return None
        
    def verify_admin_password(self, password: str) -> bool:
        """Verify the admin password"""
        try:
            admin = self.get_admin_user()
            if not admin:
                logger.warning("No admin user found")
                return False
            
            return admin.check_password(password)
        except Exception as e:
            logger.error(f"Error verifying admin password: {e}")
            return False
    
    def update_admin_last_login(self):
        """Update the admin's last login time"""
        admin = self.get_admin_user()
        if admin:
            admin.last_login = self._get_current_utc_datetime()
            self.save_admin_user(admin)
            logger.info("Admin last login updated")
    
    def update_admin_password(self,username,currentpassword, new_password: str) -> bool:
        """Update the admin password"""
        admin = self.get_admin_user()
        if not admin:
            logger.warning("No admin user found to update password")
            return False
        
        # Verify current password and username
        if admin.username != username:
            logger.warning("Username does not match")
            return False
        if not admin.check_password(currentpassword):
            logger.warning("Current password does not match")
            return False
        # Update to new password
        admin.set_password(new_password)
        return self.save_admin_user(admin)
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()


# Example usage
# if __name__ == "__main__":
#     # Initialize the database
#     db = OCRDB()
#     new_subscription = db.renew_subscription()
#     print("New subscription:", new_subscription)
#     # Create initial subscription if it doesn't exist
#     subscription = db.get_app_subscription()
#     print("Current subscription:", subscription)
#     if not subscription:
#         print("Creating new subscription...")
#         subscription = db.createNew_app_subscription()
    
#     # Create admin user if it doesn't exist
#     admin = db.get_admin_user()
#     if not admin:
#         print("Creating admin user...")
#         admin = db.createNew_admin_user("admin", "secure_password")
    
#     # Test subscription validation
#     print("Subscription validation:", db.validate_subscription())
    
#     # Test scan increment
#     print("Current scans:", subscription.total_scans)
#     db.increment_scan_count()

#     subscription = db.get_app_subscription()
#     print("Scans after increment:", subscription.total_scans)
    
#     # Test admin authentication
#     print("Admin authentication:", db.verify_admin_password("P@ssw0rd"))
    
#     # # Test subscription renewal
#     # print("Renewing subscription...")
#     # new_subscription = db.renew_subscription()
#     # print("New subscription:", new_subscription)
    
#     # Close the connection when done
#     db.close()