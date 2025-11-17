#!/usr/bin/env python3
"""
Debug script to see why a product isn't being detected as available.
This will show you what text is on the page and why detection fails.
"""

import requests
import sys

def debug_product(url):
    """Debug product availability detection."""
    print("=" * 60)
    print("Product Detection Debugger")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print("Fetching page...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Page loaded (Status: {response.status_code})")
        print()
        
        page_content = response.text.lower()
        
        # Check for sold out indicators
        sold_out_indicators = [
            'sold out',
            'join the waitlist',
            'out of stock',
            'unavailable'
        ]
        
        # Check for available indicators
        available_indicators = [
            'add to shopping bag',
            'add to cart',
            'buy now'
        ]
        
        print("Checking for SOLD OUT indicators:")
        print("-" * 60)
        found_sold_out = False
        for indicator in sold_out_indicators:
            if indicator in page_content:
                count = page_content.count(indicator)
                print(f"  ✅ Found '{indicator}' ({count} times)")
                found_sold_out = True
            else:
                print(f"  ❌ Not found: '{indicator}'")
        print()
        
        print("Checking for AVAILABLE indicators:")
        print("-" * 60)
        found_available = False
        for indicator in available_indicators:
            if indicator in page_content:
                count = page_content.count(indicator)
                print(f"  ✅ Found '{indicator}' ({count} times)")
                found_available = True
            else:
                print(f"  ❌ Not found: '{indicator}'")
        print()
        
        # Look for similar patterns
        print("Looking for similar patterns:")
        print("-" * 60)
        similar_patterns = [
            'add to bag',
            'add to',
            'shopping bag',
            'cart',
            'purchase',
            'buy',
            'available',
            'in stock'
        ]
        for pattern in similar_patterns:
            if pattern in page_content:
                count = page_content.count(pattern)
                print(f"  Found '{pattern}' ({count} times)")
        print()
        
        # Show result
        print("=" * 60)
        print("DETECTION RESULT:")
        print("=" * 60)
        
        if found_sold_out:
            print("❌ Would be detected as: SOLD OUT")
            print("   (Found sold out indicators)")
        elif found_available:
            print("✅ Would be detected as: AVAILABLE")
            print("   (Found available indicators)")
        else:
            print("❌ Would be detected as: SOLD OUT")
            print("   (No clear indicators found - defaults to sold out)")
            print()
            print("💡 TIP: The page might use different wording.")
            print("   Look for button text like 'Add to Bag', 'Purchase', etc.")
            print("   The script needs exact matches for:")
            for ind in available_indicators:
                print(f"     - '{ind}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter product URL to debug: ").strip()
    
    debug_product(url)

