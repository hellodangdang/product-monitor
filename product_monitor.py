#!/usr/bin/env python3
"""
Product Monitor and Auto-Purchase Bot
Monitors a product page and automatically purchases when it becomes available.
"""

import time
import json
import logging
from typing import Dict, Optional
from selenium import webdriver

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import Twilio for SMS notifications
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. SMS notifications will be disabled. Install with: pip install twilio")
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager



class ProductMonitor:
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the product monitor with configuration."""
        self.config = self.load_config(config_file)
        self.product_url = self.config.get('product_url')
        self.check_interval = self.config.get('check_interval', 60)  # seconds
        self.driver = None
        self.last_status = None
        self.twilio_client = None
        self._setup_twilio()
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_file} not found!")
            raise
    
    def _setup_twilio(self):
        """Setup Twilio client for SMS notifications."""
        if not TWILIO_AVAILABLE:
            return
        
        sms_config = self.config.get('sms_notifications', {})
        account_sid = sms_config.get('twilio_account_sid')
        auth_token = sms_config.get('twilio_auth_token')
        from_number = sms_config.get('twilio_from_number')
        to_number = sms_config.get('to_number')
        
        if account_sid and auth_token and from_number and to_number:
            try:
                self.twilio_client = TwilioClient(account_sid, auth_token)
                logger.info("✅ Twilio SMS notifications enabled")
            except Exception as e:
                logger.warning(f"Failed to setup Twilio: {e}")
                self.twilio_client = None
        else:
            logger.info("SMS notifications not configured (missing Twilio credentials)")
    
    def send_discord_notifications(self, message: str, count: int = 10):
        """Send multiple Discord notifications via webhook."""
        discord_config = self.config.get('discord_notifications', {})
        webhook_url = discord_config.get('webhook_url')
        
        if not webhook_url:
            logger.debug("Discord webhook URL not configured")
            return
        
        logger.info(f"📢 Sending {count} Discord notifications...")
        
        import requests
        
        for i in range(count):
            try:
                payload = {
                    "content": message,
                    "username": "Product Monitor Bot"
                }
                response = requests.post(webhook_url, json=payload, timeout=5)
                if response.status_code == 204:
                    logger.info(f"✅ Discord notification {i+1}/{count} sent successfully")
                else:
                    logger.warning(f"Discord notification {i+1}/{count} returned status {response.status_code}")
                # Small delay between messages to avoid rate limiting
                if i < count - 1:
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to send Discord notification {i+1}/{count}: {e}")
    
    def send_sms_notifications(self, message: str, count: int = 10):
        """Send multiple SMS notifications."""
        if not self.twilio_client:
            logger.debug("Twilio client not available, skipping SMS notifications")
            return
        
        sms_config = self.config.get('sms_notifications', {})
        to_number = sms_config.get('to_number')
        from_number = sms_config.get('twilio_from_number')
        
        if not to_number or not from_number:
            logger.debug("SMS phone numbers not configured")
            return
        
        logger.info(f"📱 Sending {count} SMS notifications to {to_number}...")
        
        for i in range(count):
            try:
                self.twilio_client.messages.create(
                    body=message,
                    from_=from_number,
                    to=to_number
                )
                logger.info(f"✅ SMS {i+1}/{count} sent successfully")
                # Small delay between messages to avoid rate limiting
                if i < count - 1:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Failed to send SMS {i+1}/{count}: {e}")
    
    def setup_driver(self):
        """Setup Selenium WebDriver with Chrome."""
        chrome_options = Options()
        
        # Run in headless mode (set to False if you want to see the browser)
        if self.config.get('headless', True):
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # Use webdriver-manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Make sure window is visible and on top
            if not self.config.get('headless', True):
                try:
                    self.driver.maximize_window()
                    # Bring window to front (macOS)
                    import subprocess
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of process "Google Chrome" to true'], 
                                 capture_output=True, timeout=2)
                except:
                    pass
            
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def check_availability(self) -> bool:
        """Check if the product is available (not sold out)."""
        try:
            logger.info(f"Checking availability for {self.product_url}")
            self.driver.get(self.product_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # FIRST: Check for positive availability indicators (Add to Cart button)
            # This is the most reliable indicator
            add_to_cart_found = False
            try:
                # Look for add to cart button with various selectors
                add_to_cart_selectors = [
                    (By.CSS_SELECTOR, "button[type='submit'][name='add']"),
                    (By.CSS_SELECTOR, "button.product-form__cart-submit"),
                    (By.CSS_SELECTOR, "form[action*='/cart/add'] button[type='submit']"),
                    (By.XPATH, "//button[contains(text(), 'Add to Cart')]"),
                    (By.XPATH, "//button[contains(text(), 'Buy Now')]"),
                    (By.CSS_SELECTOR, "button[type='submit']"),
                ]
                
                for by, selector in add_to_cart_selectors:
                    try:
                        elements = self.driver.find_elements(by, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                # Check if button text doesn't say "Sold Out" or "Waitlist"
                                button_text = element.text.lower()
                                if 'sold out' not in button_text and 'waitlist' not in button_text:
                                    add_to_cart_found = True
                                    logger.info(f"Found enabled Add to Cart button: {element.text}")
                                    break
                        if add_to_cart_found:
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                if add_to_cart_found:
                    logger.info("✅ Product is AVAILABLE (Add to Cart button found)")
                    return True
                    
            except Exception as e:
                logger.debug(f"Error checking for add to cart button: {e}")
            
            # SECOND: Check for explicit sold out indicators in visible elements
            # Only mark as sold out if we find explicit sold out text in visible elements
            try:
                sold_out_xpaths = [
                    "//button[contains(text(), 'Sold Out')]",
                    "//button[contains(text(), 'Join the Waitlist')]",
                    "//*[@class and contains(text(), 'Sold Out')]",
                    "//*[contains(@class, 'sold-out')]",
                ]
                
                for xpath in sold_out_xpaths:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed():
                                logger.info(f"Found sold out indicator: {element.text}")
                                return False
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Error checking for sold out indicators: {e}")
            
            # THIRD: Check page text for sold out, but only if we didn't find Add to Cart
            # This is a fallback check
            try:
                page_text = self.driver.page_source.lower()
                # Look for explicit sold out patterns in the main product area
                # Check for patterns like "Sold Out" near product form or price
                if 'sold out' in page_text:
                    # Double check by looking for the actual button text
                    try:
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if button.is_displayed():
                                btn_text = button.text.lower()
                                if 'sold out' in btn_text or 'join the waitlist' in btn_text:
                                    logger.info("Product is SOLD OUT (found sold out button)")
                                    return False
                    except:
                        pass
            except:
                pass
            
            # If we get here, we couldn't find clear indicators
            # If no add to cart button found, assume sold out for safety
            if not add_to_cart_found:
                logger.warning("⚠️  Could not find Add to Cart button. Assuming SOLD OUT.")
                return False
            else:
                logger.warning("⚠️  Could not determine availability clearly. Assuming available.")
                return True
                
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    def add_to_cart(self) -> bool:
        """Add product to cart."""
        try:
            logger.info("Attempting to add product to cart...")
            
            # Wait a bit for page to fully load
            time.sleep(3)
            
            # Try to find and click add to cart button
            # The Row uses "Add to Shopping Bag" text
            add_to_cart_selectors = [
                (By.XPATH, "//button[contains(text(), 'Add to Shopping Bag')]"),
                (By.XPATH, "//button[contains(text(), 'Add to Cart')]"),
                (By.XPATH, "//button[contains(text(), 'Buy Now')]"),
                (By.CSS_SELECTOR, "button[type='submit'][name='add']"),
                (By.CSS_SELECTOR, "button.product-form__cart-submit"),
                (By.CSS_SELECTOR, "form[action*='/cart/add'] button[type='submit']"),
                (By.CSS_SELECTOR, "form button[type='submit']"),
            ]
            
            for by, selector in add_to_cart_selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    element = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"✅ Successfully clicked add to cart button: {element.text}")
                    time.sleep(5)  # Wait for cart to update and any popups
                    return True
                except TimeoutException:
                    logger.debug(f"Selector {selector} timed out")
                    continue
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            logger.error("❌ Could not find add to cart button")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot("debug_cart_button.png")
                logger.info("Saved screenshot: debug_cart_button.png")
            except:
                pass
            return False
            
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False
    
    def proceed_to_checkout(self) -> bool:
        """Navigate to checkout page."""
        try:
            logger.info("Proceeding to checkout...")
            
            # Wait a bit for any cart drawer/popup to appear
            time.sleep(3)
            
            # First, try to find and click checkout button in cart drawer/popup
            cart_drawer_selectors = [
                (By.XPATH, "//a[contains(text(), 'Checkout')]"),
                (By.XPATH, "//button[contains(text(), 'Checkout')]"),
                (By.XPATH, "//a[contains(text(), 'Proceed to Checkout')]"),
                (By.XPATH, "//a[contains(@href, '/checkout')]"),
                (By.CSS_SELECTOR, "a[href*='/checkout']"),
                (By.CSS_SELECTOR, ".cart-drawer a[href*='/checkout']"),
                (By.CSS_SELECTOR, ".drawer a[href*='/checkout']"),
            ]
            
            for by, selector in cart_drawer_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if element.is_displayed():
                        logger.info(f"Found checkout button in drawer: {element.text}")
                        element.click()
                        time.sleep(5)
                        logger.info("✅ Clicked checkout button from cart drawer")
                        return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If no drawer checkout button, try going directly to cart page
            logger.info("No cart drawer found, navigating directly to cart page...")
            try:
                base_url = self.product_url.split('/products/')[0]
                cart_url = base_url + '/cart'
                logger.info(f"Navigating to: {cart_url}")
                self.driver.get(cart_url)
                time.sleep(5)
                
                # Now look for checkout button on cart page
                checkout_selectors = [
                    (By.XPATH, "//button[contains(text(), 'Checkout')]"),
                    (By.XPATH, "//a[contains(text(), 'Checkout')]"),
                    (By.CSS_SELECTOR, "button[name='checkout']"),
                    (By.CSS_SELECTOR, "a[href*='/checkout']"),
                    (By.CSS_SELECTOR, "form[action*='/checkout'] button"),
                ]
                
                for by, selector in checkout_selectors:
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        element.click()
                        logger.info("✅ Clicked checkout button on cart page")
                        time.sleep(5)
                        return True
                    except TimeoutException:
                        continue
                    except Exception as e:
                        logger.debug(f"Checkout selector {selector} failed: {e}")
                        continue
                
                logger.info("✅ Navigated to cart page (checkout button may be on next page)")
                return True
            except Exception as e:
                logger.error(f"Error navigating to cart: {e}")
            
            logger.error("❌ Could not proceed to checkout")
            return False
            
        except Exception as e:
            logger.error(f"Error proceeding to checkout: {e}")
            return False
    
    def fill_checkout_form(self) -> bool:
        """Fill out the checkout form with user information."""
        try:
            logger.info("Filling checkout form...")
            shipping_info = self.config.get('shipping_info', {})
            
            if not shipping_info:
                logger.error("No shipping information in config!")
                return False
            
            # Wait for checkout form to load
            time.sleep(5)
            
            # Check if we're on Shopify checkout (might be in iframe)
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Try to switch to checkout iframe if it exists
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    if 'checkout' in iframe.get_attribute('src', '').lower():
                        logger.info("Switching to checkout iframe")
                        self.driver.switch_to.frame(iframe)
                        time.sleep(2)
                        break
            except:
                pass
            
            # Fill email - try multiple selectors
            email_selectors = [
                (By.ID, "checkout_email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[name='email']"),
                (By.CSS_SELECTOR, "input[id*='email']"),
                (By.XPATH, "//input[@type='email']"),
            ]
            
            email_filled = False
            for by, selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    email_field.clear()
                    email_field.send_keys(shipping_info.get('email', ''))
                    logger.info(f"✅ Filled email using {selector}")
                    email_filled = True
                    time.sleep(1)
                    break
                except:
                    continue
            
            if not email_filled:
                logger.warning("⚠️  Could not fill email field")
            
            # Fill shipping address fields with multiple selector options
            address_fields = {
                'first_name': [
                    (By.ID, "checkout_shipping_address_first_name"),
                    (By.CSS_SELECTOR, "input[name*='first']"),
                    (By.CSS_SELECTOR, "input[id*='first']"),
                    (By.XPATH, "//input[contains(@name, 'first')]"),
                ],
                'last_name': [
                    (By.ID, "checkout_shipping_address_last_name"),
                    (By.CSS_SELECTOR, "input[name*='last']"),
                    (By.CSS_SELECTOR, "input[id*='last']"),
                    (By.XPATH, "//input[contains(@name, 'last')]"),
                ],
                'address1': [
                    (By.ID, "checkout_shipping_address_address1"),
                    (By.CSS_SELECTOR, "input[name*='address1']"),
                    (By.CSS_SELECTOR, "input[name*='address']"),
                    (By.CSS_SELECTOR, "input[id*='address']"),
                ],
                'city': [
                    (By.ID, "checkout_shipping_address_city"),
                    (By.CSS_SELECTOR, "input[name*='city']"),
                    (By.CSS_SELECTOR, "input[id*='city']"),
                ],
                'zip': [
                    (By.ID, "checkout_shipping_address_zip"),
                    (By.CSS_SELECTOR, "input[name*='zip']"),
                    (By.CSS_SELECTOR, "input[name*='postal']"),
                    (By.CSS_SELECTOR, "input[id*='zip']"),
                ],
                'phone': [
                    (By.ID, "checkout_shipping_address_phone"),
                    (By.CSS_SELECTOR, "input[name*='phone']"),
                    (By.CSS_SELECTOR, "input[type='tel']"),
                ],
            }
            
            filled_count = 0
            for field_name, selectors in address_fields.items():
                value = shipping_info.get(field_name, '')
                if not value:
                    continue
                
                field_filled = False
                for by, selector in selectors:
                    try:
                        element = self.driver.find_element(by, selector)
                        if element.is_displayed():
                            element.clear()
                            element.send_keys(value)
                            logger.info(f"✅ Filled {field_name}: {value}")
                            filled_count += 1
                            time.sleep(0.5)
                            field_filled = True
                            break
                    except:
                        continue
                
                if not field_filled:
                    logger.warning(f"⚠️  Could not fill {field_name}")
            
            # Select country/state if needed
            try:
                country = shipping_info.get('country', 'United States')
                country_selectors = [
                    (By.ID, "checkout_shipping_address_country"),
                    (By.CSS_SELECTOR, "select[name*='country']"),
                    (By.CSS_SELECTOR, "select[id*='country']"),
                ]
                
                for by, selector in country_selectors:
                    try:
                        country_select = self.driver.find_element(by, selector)
                        from selenium.webdriver.support.ui import Select
                        select = Select(country_select)
                        select.select_by_visible_text(country)
                        logger.info(f"✅ Selected country: {country}")
                        time.sleep(1)
                        
                        # Select state/province after country
                        state = shipping_info.get('state', '')
                        if state:
                            state_selectors = [
                                (By.ID, "checkout_shipping_address_province"),
                                (By.CSS_SELECTOR, "select[name*='province']"),
                                (By.CSS_SELECTOR, "select[name*='state']"),
                            ]
                            for s_by, s_selector in state_selectors:
                                try:
                                    state_select = self.driver.find_element(s_by, s_selector)
                                    select = Select(state_select)
                                    # Try full state name first, then abbreviation
                                    try:
                                        select.select_by_visible_text(state)
                                    except:
                                        # Map common abbreviations
                                        state_map = {'WA': 'Washington', 'CA': 'California', 'NY': 'New York'}
                                        full_state = state_map.get(state.upper(), state)
                                        try:
                                            select.select_by_visible_text(full_state)
                                        except:
                                            select.select_by_value(state)
                                    logger.info(f"✅ Selected state: {state}")
                                    break
                                except:
                                    continue
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not select country/state: {e}")
            
            # Switch back to default content if we were in iframe
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
            logger.info(f"✅ Filled {filled_count} address fields")
            time.sleep(2)
            
            # Check for SMS verification requirement
            self.handle_sms_verification()
            
            return True
            
        except Exception as e:
            logger.error(f"Error filling checkout form: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Switch back to default content
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def handle_sms_verification(self) -> bool:
        """Handle SMS verification if required by Shopify."""
        try:
            logger.info("Checking for SMS verification requirement...")
            time.sleep(2)
            
            # Look for SMS verification input fields
            sms_selectors = [
                (By.CSS_SELECTOR, "input[type='tel'][name*='verification']"),
                (By.CSS_SELECTOR, "input[name*='sms']"),
                (By.CSS_SELECTOR, "input[name*='code']"),
                (By.CSS_SELECTOR, "input[placeholder*='code']"),
                (By.CSS_SELECTOR, "input[placeholder*='verification']"),
                (By.XPATH, "//input[contains(@placeholder, 'code')]"),
                (By.XPATH, "//input[contains(@placeholder, 'verification')]"),
                (By.XPATH, "//input[contains(@name, 'verification')]"),
                (By.XPATH, "//input[contains(@name, 'sms')]"),
            ]
            
            sms_field = None
            for by, selector in sms_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for element in elements:
                        if element.is_displayed():
                            sms_field = element
                            logger.warning("=" * 60)
                            logger.warning("⚠️  SMS VERIFICATION DETECTED!")
                            logger.warning("=" * 60)
                            logger.warning("Shopify requires SMS verification.")
                            logger.warning("Please enter the verification code manually in the browser.")
                            logger.warning("The script will wait up to 2 minutes for you to enter the code...")
                            logger.warning("=" * 60)
                            break
                    if sms_field:
                        break
                except:
                    continue
            
            if sms_field:
                # Wait for user to enter SMS code manually
                # Check every 2 seconds if the field has been filled
                max_wait_time = 120  # 2 minutes
                check_interval = 2
                waited = 0
                
                while waited < max_wait_time:
                    try:
                        # Check if field has a value
                        field_value = sms_field.get_attribute('value')
                        if field_value and len(field_value) >= 4:  # Assuming code is at least 4 digits
                            logger.info("✅ SMS verification code detected! Continuing...")
                            time.sleep(2)  # Wait a bit for form to process
                            return True
                        
                        # Check if we've moved past the verification step
                        # (URL changed or verification element is gone)
                        try:
                            if not sms_field.is_displayed():
                                logger.info("✅ SMS verification step appears to be complete!")
                                return True
                        except:
                            # Element no longer exists, verification likely complete
                            logger.info("✅ SMS verification step appears to be complete!")
                            return True
                            
                    except Exception as e:
                        logger.debug(f"Error checking SMS field: {e}")
                    
                    time.sleep(check_interval)
                    waited += check_interval
                    
                    if waited % 10 == 0:  # Log every 10 seconds
                        logger.info(f"Waiting for SMS code entry... ({waited}/{max_wait_time} seconds)")
                
                logger.warning("⚠️  Timeout waiting for SMS verification. Continuing anyway...")
                return False
            else:
                logger.info("No SMS verification required - continuing...")
                return True
                
        except Exception as e:
            logger.debug(f"Error checking for SMS verification: {e}")
            return True  # Continue anyway
    
    def complete_purchase(self) -> bool:
        """Complete the purchase (this will require payment info - user should review)."""
        try:
            logger.warning("=" * 60)
            logger.warning("ATTENTION: Checkout form has been filled!")
            logger.warning("Please review the checkout page in the browser window.")
            logger.warning("Payment information should be entered manually for security.")
            logger.warning("=" * 60)
            
            # Keep browser open and visible
            # Bring window to front
            try:
                self.driver.execute_script("window.focus();")
                # Try to maximize window
                self.driver.maximize_window()
                # Bring Chrome window to front on macOS
                import subprocess
                try:
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of process "Google Chrome" to true'], 
                                 capture_output=True, timeout=2)
                    logger.info("✅ Brought browser window to front")
                except:
                    pass
            except Exception as e:
                logger.debug(f"Could not bring window to front: {e}")
            
            # Check for SMS verification one more time (in case it appeared after form fill)
            self.handle_sms_verification()
            
            # Wait for user to review (60 seconds) - browser stays open
            logger.info("Browser window will stay open for 60 seconds for you to review...")
            logger.info("You can manually complete the payment in the browser.")
            logger.info("If SMS verification is required, enter the code now.")
            time.sleep(60)
            
            # For security, we'll stop here and let the user complete payment
            # If you want full automation, you'd need to add payment info here
            # but that's a security risk
            
            # Uncomment below if you want to auto-fill payment (NOT RECOMMENDED)
            # payment_info = self.config.get('payment_info', {})
            # ... fill payment fields ...
            
            return True
            
        except Exception as e:
            logger.error(f"Error completing purchase: {e}")
            return False
    
    def purchase_product(self) -> bool:
        """Complete the full purchase flow."""
        try:
            logger.info("Starting purchase process...")
            
            # Step 1: Add to cart
            if not self.add_to_cart():
                return False
            
            # Step 2: Go to checkout
            if not self.proceed_to_checkout():
                return False
            
            # Step 3: Fill shipping info
            if not self.fill_checkout_form():
                return False
            
            # Step 4: Complete purchase (user should review)
            if not self.complete_purchase():
                return False
            
            logger.info("Purchase process completed! Please review and confirm payment.")
            return True
            
        except Exception as e:
            logger.error(f"Error in purchase process: {e}")
            return False
    
    def monitor(self):
        """Main monitoring loop."""
        logger.info("Starting product monitor...")
        logger.info(f"Monitoring: {self.product_url}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        self.setup_driver()
        
        try:
            while True:
                try:
                    is_available = self.check_availability()
                    
                    if is_available and self.last_status != 'available':
                        logger.info("=" * 60)
                        logger.info("PRODUCT IS NOW AVAILABLE!")
                        logger.info("=" * 60)
                        
                        # Send notifications only (no automatic purchase)
                        product_name = self.product_url.split('/products/')[-1].replace('-', ' ').title()
                        notification_message = f"🚨 ALERT: {product_name} is NOW AVAILABLE!\n\n🔗 {self.product_url}\n\n⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        # Send Discord notifications
                        self.send_discord_notifications(notification_message, count=10)
                        
                        # Send SMS notifications (if configured)
                        self.send_sms_notifications(notification_message, count=10)
                        
                        logger.info("✅ Notifications sent! You can now purchase manually.")
                        self.last_status = 'available'
                    else:
                        self.last_status = 'available' if is_available else 'sold_out'
                    
                    # Wait before next check
                    logger.info(f"Next check in {self.check_interval} seconds...")
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    logger.info("Monitoring stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(self.check_interval)
                    
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")


def main():
    """Main entry point."""
    import sys
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    
    monitor = ProductMonitor(config_file)
    monitor.monitor()


if __name__ == '__main__':
    main()

