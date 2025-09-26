#!/usr/bin/env python3
"""
Setup script for Analytics Agent
This script helps set up the development environment
"""

import os
import sys
import subprocess
import platform


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.8+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported. Please use Python 3.8+")
        return False


def create_virtual_environment():
    """Create Python virtual environment"""
    venv_path = "venv"
    
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment already exists at {venv_path}")
        return True
    
    return run_command(f"python3 -m venv {venv_path}", "Creating virtual environment")


def get_activation_command():
    """Get the correct activation command for the current platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies():
    """Install Python dependencies"""
    activation_cmd = get_activation_command()
    
    if platform.system() == "Windows":
        pip_cmd = f"{activation_cmd} && pip install -r requirements.txt"
    else:
        pip_cmd = f"{activation_cmd} && pip install -r requirements.txt"
    
    return run_command(pip_cmd, "Installing Python dependencies")


def setup_git_ignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# MongoDB
dump/

# Temporary files
*.tmp
*.temp
"""
    
    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ .gitignore file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .gitignore: {e}")
        return False


def check_mongodb():
    """Check if MongoDB is available"""
    print("🔍 Checking MongoDB availability...")
    
    # Try to connect to local MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB is running locally")
        client.close()
        return True
    except:
        print("⚠️  MongoDB not detected locally")
        print("💡 You can:")
        print("   1. Install MongoDB locally")
        print("   2. Use MongoDB Atlas (cloud)")
        print("   3. Update MONGODB_URI in .env file")
        return False


def display_next_steps():
    """Display next steps for the user"""
    activation_cmd = get_activation_command()
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print(f"1. Activate virtual environment: {activation_cmd}")
    print("2. Update .env file with your OpenAI API key")
    print("3. Ensure MongoDB is running")
    print("4. Run setup verification: python test_setup.py")
    print("5. Load sample data: python -m src.data_pipeline")
    print("\n💡 Quick Start:")
    print(f"   {activation_cmd}")
    print("   python test_setup.py")
    print("\n📚 Documentation:")
    print("   - Check tasks/README.md for project overview")
    print("   - See .env.template for configuration options")


def main():
    """Main setup function"""
    print("🚀 Analytics Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not create_virtual_environment():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Dependency installation failed. Try manually:")
        activation_cmd = get_activation_command()
        print(f"   {activation_cmd}")
        print("   pip install -r requirements.txt")
    
    # Setup .gitignore
    setup_git_ignore()
    
    # Check MongoDB
    check_mongodb()
    
    # Display next steps
    display_next_steps()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)