import os
import re
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

#--------------------------------
#Suppress TensorFlow or Chrome logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'#suppress TensorFlow warnings

# Kill any leftover chrome/chromedriver processes from a previous crashed run
os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
os.system("taskkill /f /im chrome.exe >nul 2>&1")
time.sleep(1)

#Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")#start maximized
chrome_options.add_argument("--force-device-scale-factor=0.75")
chrome_options.add_argument("--log-level=3")#suppress ChromeDriver logs
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) #remove extra logs
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")


# ChromeDriver version for installed Chrome
driver = webdriver.Chrome(options=chrome_options)
#---------------------------------
#Open the login page
driver.get("https://incarnage.com/")
driver.set_page_load_timeout(240) 
WebDriverWait(driver, 240).until(
   EC.visibility_of_element_located((By.CSS_SELECTOR, "img.header__logo-image"))
)
print("Logo display success")

def add_to_cart(driver, search_term, product_type, preferred_size=None, timeout=60):
    try:
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search-toggle"))
        )
        search_button.click()
        print ("Search button clicked")

        try:
            # Wait until the search input is visible
            search_form = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "form.search-modal__form"))
            )

            print("Search input Displayed")

            try:
                # wait for the input to be interactable
                search_input = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.ID, "search-input"))
                )
                search_input.send_keys(search_term)

                print(f"Entered: {search_term}")

                search_input.send_keys(Keys.ENTER)
                try:
                    WebDriverWait(driver, 60).until(
                        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "h1.search-page__title"), "SEARCH")
                    )
                    print("Results page is visible")

                    try:
                        #-----------------------------------------------------------------------
                        find_and_click_product(driver, product_type, timeout=timeout)
                        #------------------------------------------------------------------------
                        try:
                            add_to_cart_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.product-page__add-to-cart"))
                            )

                            print("Add to cart icon is visible")

                            product_title_element = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.product-page__title"))
                            )
                            product_name = product_title_element.text
                            print(f"Product name: {product_name}")
                            added_product_names.append(product_name)

                            try:
                                # Wait until the size options is visible
                                WebDriverWait(driver, 10).until(
                                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.product-page__size-options"))
                                )

                                # Get all size buttons that are NOT sold out
                                available_sizes = driver.find_elements(
                                    By.CSS_SELECTOR,
                                    "button.product-page__size-btn:not(.is-sold-out)"
                                )

                                if not available_sizes:
                                    print(f"No available sizes for '{search_term}'")
                                    return

                                chosen_button = None

                                if preferred_size:
                                    # Try to find the specific size requested
                                    for btn in available_sizes:
                                        if btn.get_attribute("data-value") == preferred_size:
                                            chosen_button = btn
                                            break
                                    if chosen_button is None:
                                        print(f"Preferred size '{preferred_size}' not available for '{search_term}', picking first available instead")

                                if chosen_button is None:
                                    chosen_button = available_sizes[0]

                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_button)
                                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(chosen_button))
                                chosen_button.click()
                                print(f"Size '{chosen_button.get_attribute('data-value')}' was selected for '{product_type}'")

                                try:
                                    add_to_cart_btn = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.product-page__add-to-cart"))
                                    )
                                    add_to_cart_btn.click()
                                    print("Add to cart button clicked")
                                    return True
                                except Exception as e:
                                    print(f"Add to cart button click failed: {e}")
                            except Exception as e:
                                print(f"Size not selected: {e}")
                        except Exception as e:
                            print(f"Product page not loaded: {e}")
                    except Exception as e:
                        print(f"Pruductt link click failed: {e}")
                except Exception as e:
                    print(f"results page not visible: {e}")
            except Exception as e:
                print(f"{search_term} not entered: {e}")
        except Exception as e:
            print(f"input field is not visible: {e}")
    except Exception as e:
        print(f"Search button click failed: {e}")


def find_and_click_product(driver, product_type, timeout=10, max_pages=30):
    target = product_type.strip().lower()

    for page_num in range(1, max_pages + 1):
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-card"))
        )

        found_on_this_page = False
        scrolled_position = 0
        scroll_step = 800

        while True:
            # Re-query fresh each time — never reuse a stored element reference
            product_cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card")

            match_index = None
            for idx, card in enumerate(product_cards):
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, "p.product-card__title")
                    card_title = title_el.text.replace("\xa0", " ").strip().lower()
                    if card_title == target:
                        match_index = idx
                        break
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue

            if match_index is not None:
                found_on_this_page = True
                break

            new_height = driver.execute_script("return document.body.scrollHeight")
            if scrolled_position >= new_height:
                break  # reached bottom, stop scrolling on this page

            scrolled_position += scroll_step
            driver.execute_script(f"window.scrollTo(0, {scrolled_position});")
            time.sleep(0.3)

        if found_on_this_page:
            print(f"Found '{product_type}' on page {page_num}")

            # Relocate before interacting
            def get_target_card():
                cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card")
                for card in cards:
                    title_el = card.find_element(By.CSS_SELECTOR, "p.product-card__title")
                    card_title = title_el.text.replace("\xa0", " ").strip().lower()
                    if card_title == target:
                        return card
                return None

            # Retry the click a few times
            for attempt in range(3):
                try:
                    fresh_card = get_target_card()
                    if fresh_card is None:
                        raise ValueError(f"Lost track of '{product_type}' card on retry")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fresh_card)
                    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(fresh_card))
                    fresh_card.click()
                    print(f"Clicked product: {product_type}")
                    return True
                except StaleElementReferenceException:
                    print(f"Stale element on click attempt {attempt + 1}, retrying...")
                    time.sleep(0.5)
                    continue

            raise RuntimeError(f"Failed to click '{product_type}' after retries due to repeated staleness")

        # Not found on this page — go to next page
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.search-page__page--next")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            next_button.click()
            print(f"'{product_type}' not found on page {page_num}, moving to next page")
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-card"))
            )
        except Exception:
            raise ValueError(f"No product card found matching product_type='{product_type}' "
                              f"after searching {page_num} page(s)")

    raise ValueError(f"No product card found matching product_type='{product_type}' within {max_pages} pages")

def close_cart(driver, timeout=60):
    
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.cart-drawer.is-open"))
    )

    cart_close_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cart-drawer__close"))
    )
    cart_close_btn.click()
    print("Cart close button clicked")

def open_the_cart(driver):
    try:
        cart_trigger = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-cart-trigger]"))
        )
        cart_trigger.click()
        print("Cart is open for validation")
    except Exception as e:
        print(f"Error open cart for validation: {e}")

def parse_price(price_text):
    cleaned = re.sub(r"[^\d.]", "", price_text.replace("LKR", "").replace("\xa0", ""))
    return float(cleaned)

def get_cart_item_data(driver, timeout=10, max_retries=3):
    """
    Safely extract (title, price, qty) for every cart item, retrying the
    whole extraction if a stale element is hit mid-read.
    """
    for attempt in range(max_retries):
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#cart-items .cart-item"))
            )
            cart_items = driver.find_elements(By.CSS_SELECTOR, "#cart-items .cart-item")

            items_data = []
            for item in cart_items:
                title = item.find_element(By.CSS_SELECTOR, "p.cart-item__title").text
                price_text = item.find_element(By.CSS_SELECTOR, "span.cart-item__price").text
                qty_text = item.find_element(By.CSS_SELECTOR, "span.cart-item__qty-value").text

                items_data.append({
                    "title": title.replace("\xa0", " ").strip(),
                    "price": parse_price(price_text),
                    "qty": int(qty_text.strip())
                })

            return items_data  # success

        except StaleElementReferenceException:
            print(f"Stale element while reading cart (attempt {attempt + 1}/{max_retries}), retrying...")
            time.sleep(0.5)
            continue

    raise RuntimeError("Failed to read cart items after repeated stale element errors")

def validate_cart(driver, search_items, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.cart-drawer.is-open"))
    )

    items_data = get_cart_item_data(driver, timeout=timeout)

    # --- Check item count ---
    expected_count = len(search_items)
    actual_count = len(items_data)
    check1 = (expected_count == actual_count)
    print(f"[Check 1] Expected items: {expected_count}, Actual items: {actual_count} -> {'OK' if check1 else 'MISMATCH'}")

    # --- Check product names match search_items' product_type ---
    expected_product_types = [entry["product_type"] for entry in search_items]
    expected_names_sorted = sorted(name.strip().lower() for name in expected_product_types)
    cart_names_sorted = sorted(d["title"].lower() for d in items_data)
    check2 = (expected_names_sorted == cart_names_sorted)
    print(f"[Check 2] Expected products: {expected_names_sorted}")
    print(f"[Check 2] Cart products:     {cart_names_sorted} -> {'OK' if check2 else 'MISMATCH'}")

    # --- Check price sum vs total ---
    calculated_sum = sum(d["price"] * d["qty"] for d in items_data)
    total_text = driver.find_element(By.ID, "cart-total-price").text
    cart_total = parse_price(total_text)
    check3 = abs(calculated_sum - cart_total) < 0.01
    print(f"[Check 3] Calculated sum: {calculated_sum:.2f}, Cart total: {cart_total:.2f} -> {'OK' if check3 else 'MISMATCH'}")

    if check1 and check2 and check3:
        print("PASS")
        return True
    else:
        print("FAIL")
        return False
    
def checkout(driver, email_address):
    try:
        #Click checkout button
        checkout_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cart-drawer__checkout"))
        )
        checkout_btn.click()
        print("Checkout button clicked")
    except Exception as e:
        print(f"Checkout button not found: {e}")
        return False

    #Try to close the popup
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.lb-addon-popup-header"))
        )
        close_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.lb-addon-popup-close-icon"))
        )
        close_icon.click()
        print("Buy more popup closed")
    except Exception:
        print("Buy more popup did not appear — continuing")

    #Wait for checkout page header and enter the email
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "header[data-inspector-id='header']"))
        )

        email_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "email"))
        )
        email_input.clear()
        email_input.send_keys(email_address)
        print(f"Email entered: {email_address}")
        return True

    except Exception as e:
        print(f"Checkout page / email entry failed: {e}")
        return False
    
def enter_checkout_details(driver, details, timeout=20):
    """
    Enter checkout form details using Tab to move between fields.
    `details` is a single dict, e.g. Checkout_details[0].
    """
    try:
        #Click checkout button
        checkout_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cart-drawer__checkout"))
        )
        checkout_btn.click()
        print("Checkout button clicked")
    except Exception as e:
        print(f"Checkout button not found: {e}")
        return False

    # Try to close the popup
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.lb-addon-popup-header"))
        )
        close_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.lb-addon-popup-close-icon"))
        )
        close_icon.click()
        print("Buy more popup closed")
    except Exception:
        print("Buy more popup did not appear — continuing")

    #Wait for checkout page header
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "header[data-inspector-id='header']"))
        )
        
        # Start by locating and clicking the email field to establish initial focus
        email_input = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "email"))
        )
        email_input.click()
        email_input.clear()
        email_input.send_keys(details["email_address"])
        print("Email address entered")

        
        # Tab to Country dropdown
        try:
            for i in range(3):
                active = driver.switch_to.active_element
                active.send_keys(Keys.TAB)
                print("tab to country")
            time.sleep(0.3)
        except Exception as e:
            print("tab to country failed: {e}")

        active = driver.switch_to.active_element
        #typing the visible option text and select
        active.send_keys(details["country"])
        time.sleep(0.3)
        
        # Tab to First name
        for i in range(2):
            active.send_keys(Keys.TAB)
            print("Tab to first name")
        time.sleep(0.3)
        active = driver.switch_to.active_element
        active.send_keys(details["first_name"])

        # Tab to Last name
        active.send_keys(Keys.TAB)
        time.sleep(0.3)
        active = driver.switch_to.active_element
        active.send_keys(details["last_name"])

        # Tab to Address
        active.send_keys(Keys.TAB)
        time.sleep(0.3)
        active = driver.switch_to.active_element
        active.send_keys(details["address"])

        #move to city
        active.send_keys(Keys.TAB)
        time.sleep(0.2)
        active = driver.switch_to.active_element
        active.send_keys(Keys.TAB)  # skip apartment field, move to City
        time.sleep(0.3)
        active = driver.switch_to.active_element
        active.send_keys(details["city"])

        # Tab to Postal code
        active.send_keys(Keys.TAB)
        time.sleep(0.3)
        active = driver.switch_to.active_element
        active.send_keys(details["postal_code"])

        # Tab to Phone
        active.send_keys(Keys.TAB)
        time.sleep(0.3)
        active = driver.switch_to.active_element
        active.send_keys(details["phone_number"])

        print("Checkout details entered")
    except Exception as e:
        print(f"enter checkout details failed: {e}")

def verify_checkout_details(driver, details, timeout=20):
    """
    Read back the values from each field and compare against `details`.
    Prints PASS/FAIL for each field and an overall result.
    """
    field_map = {
        "email_address": (By.ID, "email"),
        "first_name": (By.NAME, "firstName"),
        "last_name": (By.NAME, "lastName"),
        "address": (By.NAME, "address1"),
        "city": (By.NAME, "city"),
        "postal_code": (By.NAME, "postalCode"),
        "phone_number": (By.NAME, "phone"),
    }

    all_passed = True

    for key, (by, locator) in field_map.items():
        try:
            field = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            actual_value = field.get_attribute("value").strip()
            expected_value = str(details[key]).strip()

            if key == "phone_number":
                actual_digits = re.sub(r"\D", "", actual_value)
                expected_digits = re.sub(r"\D", "", expected_value)
                match = (actual_digits == expected_digits)
            else:
                match = (actual_value == expected_value)

            if match:
                print(f"[{key}] Expected: '{expected_value}', Actual: '{actual_value}' -> PASS")
            else:
                print(f"[{key}] Expected: '{expected_value}', Actual: '{actual_value}' -> FAIL")

        except Exception as e:
            print(f"[{key}] Could not verify field: {e} -> FAIL")
            all_passed = False

    # verify
    try:
        country_select = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "SelectP0-47"))
        )
        selected_value = country_select.get_attribute("value")
        
        selected_text = driver.execute_script(
            "return arguments[0].options[arguments[0].selectedIndex].text;", country_select
        )
        expected_country = details["country"].strip()

        if selected_text.strip() == expected_country:
            print(f"[country] Expected: '{expected_country}', Actual: '{selected_text}' -> PASS")
        else:
            print(f"[country] Expected: '{expected_country}', Actual: '{selected_text}' -> FAIL")
            all_passed = False

    except Exception as e:
        print(f"[country] Could not verify field: {e} -> FAIL")
        all_passed = False

    print("PASS" if all_passed else "FAIL")
    return all_passed


search_items = [
    {"search_term": "tee", "product_type": "Seamless crew neck", "size": "M"},
    {"search_term": "shorts", "product_type": "Carnage retro short", "size": "L"}
]

Checkout_details = [
    {"email_address":"jithmi328@gmail.com", "country":"Sri Lanka", "first_name":"Jithmi", "last_name":"Nanayakkara", "address":"180B, Mabodala, Veyangoda",
     "city":"Gampaha","postal_code":"11114", "phone_number":"0762443450"}
]

added_product_names = []

for item in search_items:
    try:
        success = add_to_cart(
            driver,
            search_term=item["search_term"],
            product_type=item["product_type"],
            preferred_size=item.get("size")
        )
        if success:
            close_cart(driver, timeout=60)
        else:
            print(f"Skipping cart close for '{item['product_type']}' — add to cart did not succeed")
    except Exception as e:
        print(f"Error processing '{item['product_type']}': {e}")

open_the_cart(driver)
validate_cart(driver, search_items)

details = Checkout_details[0]
enter_checkout_details(driver, details)
verify_checkout_details(driver, details)