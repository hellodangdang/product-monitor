#!/usr/bin/env python3
"""
Quick test script to verify your setup is working correctly.
"""

import sys

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")
    try:
        import selenium
        print("✅ Selenium installed")
    except ImportError:
        print("❌ Selenium not installed. Run: pip3 install selenium")
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager installed")
    except ImportError:
        print("❌ webdriver-manager not installed. Run: pip3 install webdriver-manager")
        return False
    
    try:
        import requests
        print("✅ requests installed")
    except ImportError:
        print("❌ requests not installed. Run: pip3 install requests")
        return False
    
    return True

def test_chrome():
    """Test if Chrome/ChromeDriver can be initialized."""
    print("\nTesting Chrome/ChromeDriver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("✅ Chrome and ChromeDriver working correctly")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Chrome/ChromeDriver test failed: {e}")
        return False

def test_config():
    """Test if config file exists and is valid."""
    print("\nTesting config file...")
    import json
    import os
    
    if not os.path.exists('config.json'):
        print("❌ config.json not found. Run: cp config.json.example config.json")
        return False
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required = ['product_url', 'shipping_info']
        missing = [field for field in required if field not in config]
        if missing:
            print(f"❌ Config missing required fields: {missing}")
            return False
        
        # Check if shipping info has placeholder values
        shipping = config.get('shipping_info', {})
        if shipping.get('email') == 'your-email@example.com':
            print("⚠️  Config file exists but still has placeholder values")
            print("   Please edit config.json with your actual information")
            return False
        
        print("✅ Config file is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Config file has invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Product Monitor Setup Test")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Chrome/ChromeDriver", test_chrome()))
    results.append(("Config File", test_config()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to run:")
        print("   python3 product_monitor.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

