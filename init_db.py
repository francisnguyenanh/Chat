from app import app, db
from models import User

def init_database():
    """Initialize database with admin and 9 users"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Database already initialized!')
            return
        
        # Create admin user
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create 9 regular users
        for i in range(1, 10):
            user = User(username=f'user{i}', is_admin=False)
            user.set_password(f'password{i}')
            db.session.add(user)
        
        # Commit changes
        db.session.commit()
        
        print('✅ Database initialized successfully!')
        print('\nDefault accounts:')
        print('=' * 50)
        print('Admin:')
        print('  Username: admin')
        print('  Password: admin123')
        print('\nUsers:')
        for i in range(1, 10):
            print(f'  Username: user{i}  |  Password: password{i}')
        print('=' * 50)

if __name__ == '__main__':
    init_database()
