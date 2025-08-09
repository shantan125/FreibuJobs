#!/usr/bin/env python3
"""
Setup Script for LinkedIn Job & Internship Bot

Helps users configure and validate their bot installation.
"""

import os
import sys
from pathlib import Path
import subprocess

def print_header():
    """Print setup header."""
    print("🚀 LinkedIn Job & Internship Bot Setup")
    print("=" * 45)
    print()

def check_python_version():
    """Check Python version compatibility."""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("   Please upgrade to Python 3.8 or higher")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'telegram',
        'selenium',
        'dotenv'  # Changed from 'python-dotenv' to 'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_env_file():
    """Create .env file from template."""
    print("\n🔍 Setting up environment configuration...")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    # Create basic .env file
    env_content = """# LinkedIn Job & Internship Bot Configuration

# Required: Get your token from @BotFather on Telegram
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Optional Configuration (uncomment and modify as needed)
# DEFAULT_LOCATION=India
# MAX_RESULTS=10
# LOG_LEVEL=INFO
# LOG_FILE=linkedin_bot.log

# Advanced Configuration (usually not needed)
# CHROME_DRIVER_PATH=/path/to/chromedriver
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with default configuration")
        print("   Please edit .env and add your TELEGRAM_TOKEN")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def validate_env_config():
    """Validate environment configuration."""
    print("\n🔍 Validating configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    # Check for required variables
    required_vars = ['TELEGRAM_TOKEN']
    missing_vars = []
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing or invalid configuration for: {', '.join(missing_vars)}")
            print("   Please edit .env file and set proper values")
            return False
        else:
            print("✅ Configuration looks good")
            return True
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_chrome_browser():
    """Check if Chrome/Chromium is installed."""
    print("\n🔍 Checking Chrome browser...")
    
    chrome_commands = ['google-chrome', 'chrome', 'chromium', 'chromium-browser']
    
    for cmd in chrome_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Found Chrome: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("⚠️  Chrome/Chromium not found or not in PATH")
    print("   The bot will try to auto-detect Chrome during runtime")
    print("   If you encounter issues, please install Chrome manually")
    return True  # Non-blocking

def run_basic_tests():
    """Run basic functionality tests."""
    print("\n🔍 Running basic tests...")
    
    try:
        # Add current directory to Python path for testing
        sys.path.insert(0, str(Path.cwd()))
        
        # Test imports
        from src.utils.config import ConfigurationManager
        from src.bot.messages import MessageTemplates
        print("✅ Core modules import successfully")
        
        # Test message templates
        welcome = MessageTemplates.welcome_message("TestUser")
        if "TestUser" in welcome:
            print("✅ Message templates working")
        else:
            print("❌ Message template test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎯 Next Steps:")
    print("1. Edit .env file and add your TELEGRAM_TOKEN")
    print("2. Get your token from @BotFather on Telegram:")
    print("   - Start a chat with @BotFather")
    print("   - Send /newbot and follow instructions")
    print("   - Copy the token to your .env file")
    print("3. Run the bot: python main.py")
    print("\n📚 For help, check README.md or run: python main.py --help")

def main():
    """Main setup function."""
    print_header()
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", create_env_file),
        ("Configuration", validate_env_config),
        ("Chrome Browser", check_chrome_browser),
        ("Basic Tests", run_basic_tests)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 45)
    
    if all_passed:
        print("🎉 Setup completed successfully!")
        print_next_steps()
    else:
        print("⚠️  Setup completed with some issues.")
        print("Please resolve the issues above before running the bot.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
