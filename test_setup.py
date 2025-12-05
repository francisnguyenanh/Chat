"""
Test script to verify the application setup
"""
import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        print("✓ Flask installed")
        import flask_sqlalchemy
        print("✓ Flask-SQLAlchemy installed")
        import flask_login
        print("✓ Flask-Login installed")
        import flask_socketio
        print("✓ Flask-SocketIO installed")
        import eventlet
        print("✓ Eventlet installed")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        return False

def test_files():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    required_files = [
        'app.py',
        'models.py',
        'config.py',
        'init_db.py',
        'requirements.txt',
        'templates/login.html',
        'templates/chat.html',
        'templates/admin.html',
        'static/css/style.css',
        'static/js/chat.js',
        'static/js/admin.js',
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_database_init():
    """Test database initialization"""
    print("\nTesting database initialization...")
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # Check if we can create tables
            db.create_all()
            print("✓ Database tables can be created")
            
            # Check if we can query users
            user_count = User.query.count()
            print(f"✓ Database accessible (found {user_count} users)")
            
            if user_count == 0:
                print("\n⚠ Database is empty. Run 'python init_db.py' to create default users.")
            else:
                admin = User.query.filter_by(is_admin=True).first()
                if admin:
                    print(f"✓ Admin account found: {admin.username}")
                
                users = User.query.filter_by(is_admin=False).count()
                print(f"✓ Regular users: {users}")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def main():
    print("=" * 60)
    print("CHAT APP - SYSTEM TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Package Installation", test_imports()))
    
    # Test file structure
    results.append(("File Structure", test_files()))
    
    # Test database
    results.append(("Database Setup", test_database_init()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed! Your application is ready to run.")
        print("\nTo start the application:")
        print("  1. Run: python init_db.py (if database is empty)")
        print("  2. Run: python app.py")
        print("  3. Open: http://localhost:5000")
        print("\nOr simply double-click: run.bat")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("Run 'pip install -r requirements.txt' if packages are missing.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
