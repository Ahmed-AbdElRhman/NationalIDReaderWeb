from datetime import datetime, timedelta
from app.Database import db, bcrypt
from app.Database.models import AppSubscription as AppSubscriptionTable
from app.Database.models import AdminUser as AdminUserTable
# from app.config import SECRET_KEY,SUBSCRIPTION_DAYS, MAX_SCANS,ADMIN_USERNAME, ADMIN_PASSWORD
from app.utils.logger import get_logger
logger = get_logger(__name__)

class DBService:
    # This class is used to manage the database connection and operations.
    #Singleton pattern to ensure only one instance exists
    _instance = None
    app= None  # Placeholder for the Flask app instance
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # print("HIIIIIIIII56666")
            # print(cls._instance)
            cls._instance = super(DBService, cls).__new__(cls)
        return cls._instance

    def __init__(self, app=None):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # Initialize the service only once
            if app:
                self.app = app
                self._initialize_service()
            else:
                raise ValueError("Flask app instance is required for DBservice initialization")
    def _initialize_service(self):
        # Perform any necessary initialization here
        # setting up database connections, loading configurations, etc.
        logger.debug("Initializing AppSubscriptionService")
        self.appSubscription = AppSubscriptionTable()  
        self.adminUser = AdminUserTable() 
        if not self.app:
            raise ValueError("Flask app instance is required for DBservice initialization")
        db.init_app(self.app)
        bcrypt.init_app(self.app)
        print(self.app.config['SQLALCHEMY_DATABASE_URI'])
        with self.app.app_context():
            db.create_all()
            logger.debug("Database tables created or verified Creating AppSubscriptionTable if not exists")
            # Create initial subscription if not exists
            self.appSubscription= AppSubscriptionTable.query.first()
            if not self.appSubscription:
                self.appSubscription = AppSubscriptionTable()
                db.session.add(self.appSubscription)
                self.update_subscription_hash()
                self.update_subscription()
            if not self.adminUser.query.filter_by(username=self.app.config['ADMIN_USERNAME']).first():
                admin = AdminUserTable(username=self.app.config['ADMIN_USERNAME'])
                admin.set_password(self.app.config['ADMIN_PASSWORD'])  # Default password
                db.session.add(admin)
                db.session.commit()
        logger.debug("DB initialized successfully")
# ------------------ Subscription Management Methods ------------------
    # 
    def get_subscription(self):
        """Retrieve the first AppSubscription record"""
        if not self.appSubscription:
            self.appSubscription = AppSubscriptionTable.query.first()
        return self.appSubscription
    
    def update_subscription_hash(self):
        """Update the verification hash after changes"""
        logger.debug("Updating subscription verification hash")
        self.appSubscription.verification_hash = self.appSubscription.compute_hash(self.app.config['SECRET_KEY'])
        print(self.appSubscription.verification_hash)
        logger.debug("Subscription verification hash updated successfully")

    
    def update_subscription(self):
        """Update the AppSubscription record"""
        logger.debug("Updating AppSubscription record")
        db.session.add(self.appSubscription)
        db.session.commit()
        self.appSubscription= AppSubscriptionTable.query.first()  # Refresh the instance
        logger.debug("AppSubscription record updated successfully")
    
    def verify_subscription_integrity(self):
        """Check if subscription data has been tampered with"""
        logger.debug("Verifying subscription integrity")
        self.appSubscription = self.get_subscription()
        if not self.appSubscription:
            logger.error("No subscription found for integrity verification")
            return False
        current_hash = self.appSubscription.verification_hash
        computed_hash = self.appSubscription.compute_hash(self.app.config['SECRET_KEY'])
        
        if current_hash != computed_hash:
            logger.error(f"TAMPER_DETECTED Hash mismatch: stored {current_hash}, computed {computed_hash}")
            return False
        return True
    
    def validate_subscription(self):
        """Check subscription status and expiration with integrity verification"""
        logger.debug("Validating subscription status and expiration")
        if not self.verify_subscription_integrity():
            return False, "Subscription integrity check failed:"
        self.appSubscription = self.get_subscription()
        if not self.appSubscriptio or not self.appSubscriptio.is_active:
            return False, "Subscription not active Maybe expired"
        # Check time expiration (1 year)
        if datetime.utcnow() > self.appSubscriptio.install_date + timedelta(days= self.app.config['SUBSCRIPTION_DAYS']):
            self.appSubscriptio.is_active = False
            self.update_subscription_hash()
            self.update_subscription()
            logger.info("Subscription expired due to time limit")
            return False, "Subscription expired (time limit)"
            # Check scan limit
        if self.appSubscriptio.total_scans >= self.app.config['MAX_SCANS']:
            self.appSubscriptio.is_active = False
            self.update_subscription_hash()
            self.update_subscription()
            logger.info("Subscription expired due to scan limit reached")
            self.log_audit_event("SUBSCRIPTION_EXPIRED", "Scan limit reached")
            return False, "Subscription expired (scan limit)"
        return True, "Subscription is valid"

    def increment_scan_count(self):
        """Increment the scan count for the subscription"""
        logger.debug("Incrementing scan count for subscription")
        self.appSubscription = self.get_subscription()
        self.appSubscription.total_scans += 1
        self.update_subscription_hash()
        self.update_subscription()
        return self.appSubscription.total_scans
    
    def renew_subscription(self):
        """Update the AppSubscription record"""
        logger.debug("Updating AppSubscription record")
        self.appSubscription = self.get_subscription()
        self.appSubscription.total_scans = 0
        self.appSubscription.install_date = datetime.utcnow()
        self.appSubscription.is_active = True
        self.update_subscription_hash()
        self.update_subscription()
        logger.debug("AppSubscription record updated successfully")
        return  self.appSubscription
    
    # ------------------ Admin User Management Methods ------------------
    def get_admin_user(self, username):
        """Retrieve an AdminUser by username"""
        admin_user = AdminUserTable.query.filter_by(username=username).first()
        if not admin_user:
            raise ValueError("Admin user not found")
        return admin_user
    
    def create_admin_user(self, username, password):
        """Create a new AdminUser"""
        if AdminUserTable.query.filter_by(username=username).first():
            raise ValueError("Username already exists")
        admin_user = AdminUserTable(username=username)
        admin_user.set_password(password)
        self.app.db.session.add(admin_user)
        self.app.db.session.commit()
        return admin_user
    
    def update_admin_user(self, username, new_password=None):
        """Update an existing AdminUser's password"""
        admin_user = self.get_admin_user(username)
        if new_password:
            admin_user.set_password(new_password)
        self.app.db.session.commit()
        return admin_user
    
    def change_admin_password(self, username, old_password, new_password):
        """Change the password for an AdminUser"""
        admin_user = self.get_admin_user(username)
        if not admin_user.check_password(old_password):
            raise ValueError("Old password is incorrect")
        admin_user.set_password(new_password)
        self.app.db.session.commit()
        return admin_user
    
    def check_admin_password(self, username, password):
        """Check if the provided password matches the AdminUser's password"""
        admin_user = self.get_admin_user(username)
        return admin_user.check_password(password)





