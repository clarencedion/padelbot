import time
import datetime
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from dotenv import load_dotenv

# Load .env only if running locally
if os.getenv("REPLIT_ENV") is None:
    load_dotenv()

os.environ["PATH"] += os.pathsep + "/run/current-system/sw/bin"


def create_driver():
    # Set correct paths for Chrome and ChromeDriver
    CHROME_BINARY_PATH = "/usr/bin/google-chrome"
    CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

    os.environ["CHROME_BINARY"] = CHROME_BINARY_PATH
    os.environ["CHROMEDRIVER_PATH"] = CHROMEDRIVER_PATH

    # Debugging: Check if files exist
    if not os.path.exists(CHROME_BINARY_PATH):
        raise Exception(f"Chrome binary not found at: {CHROME_BINARY_PATH}. Available PATH: {os.environ['PATH']}")
    
    if not os.path.exists(CHROMEDRIVER_PATH):
        raise Exception(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")

    # Debugging: Print system versions
    print("Checking Chrome version...")
    os.system(f"{CHROME_BINARY_PATH} --version")

    print("Checking ChromeDriver version...")
    os.system(f"{CHROMEDRIVER_PATH} --version")

    # Configure Selenium options
    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_BINARY_PATH
    options.add_argument("--headless")  # Required for running in Koyeb
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    return driver

# Initialize driver
driver = create_driver()


def send_keys_retry(by_locator, text, wait, attempts=3):
    for i in range(attempts):
        try:
            element = wait.until(EC.element_to_be_clickable(by_locator))
            element.clear()
            element.send_keys(text)
            return True
        except StaleElementReferenceException:
            print("Stale element encountered while sending keys. Retrying...")
            time.sleep(0.5)
    return False

def login(email, password):
    """Login to the website using credentials stored in environment variables"""
    email = os.getenv("EMAIL")  # Load email from Replit Secrets
    password = os.getenv("PASSWORD")  # Load password from Replit Secrets

    if not email or not password:
        raise ValueError("Missing EMAIL or PASSWORD environment variable.")

    driver.get("https://www.anybuddyapp.com/login?redirectUrl=%2Faccount")
    wait = WebDriverWait(driver, 10)
    
    # Use helper function for reliable input
    if not send_keys_retry((By.XPATH, "//input[@placeholder='E-mail']"), email, wait):
        raise Exception("Failed to interact with the email input.")
    if not send_keys_retry((By.XPATH, "//input[@placeholder='Mot de passe']"), password, wait):
        raise Exception("Failed to interact with the password input.")
    
    time.sleep(0.5)
    attempts = 0
    while attempts < 3:
        try:
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Connexion')]")))
            login_button.click()
            break
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(0.5)
            print("Stale element encountered while clicking login. Retrying...")
    time.sleep(0.5)

def check_availability(stop_event):
    wait = WebDriverWait(driver, 10)
    preferred_times = ["18:00", "19:00", "20:00", "21:00", "22:00"]
    while not stop_event.is_set():
        target_date = (datetime.date.today() + datetime.timedelta(days=5)).strftime("%d %b %Y")
        url = f"https://www.anybuddyapp.com/club-aquaboulevard-de-paris/reservation/padel?date={target_date}"
        driver.get(url)
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        available_sessions = driver.find_elements(By.XPATH, "//p[contains(@class, 'time')]")
        for session in available_sessions:
            session_text = session.text.strip()
            for time_slot in preferred_times:
                if time_slot in session_text:
                    print(f"Found available slot: {session_text}")
                    parent_section = session.find_element(By.XPATH, "ancestor::div[contains(@class, 'session')]")
                    reserve_button = parent_section.find_element(By.XPATH, ".//p[contains(text(), 'Réserver')]")
                    reserve_button.click()
                    print(f"Clicked on reservation for time slot: {time_slot}")
                    return time_slot
        print("No available slots at preferred times. Retrying...")
        time.sleep(2)
    # If stop_event is set, return None to signal the bot to exit.
    return None


def process_reservation():
    wait = WebDriverWait(driver, 30)

    # Load card details securely
    card_number = os.getenv("CARD_NUMBER")
    card_expiry = os.getenv("CARD_EXPIRY")
    card_cvc = os.getenv("CARD_CVC")

    if not card_number or not card_expiry or not card_cvc:
        raise ValueError("Missing credit card details in environment variables.")
    
    try:
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "checkboxConfirmation")))
        checkbox.click()
        print("Checked confirmation checkbox.")

        payer_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Payer')]")))
        payer_button.click()
        print("Clicked on 'Payer' button.")

        renseigner_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='submit' and contains(., 'Renseigner les informations et payer')]")
        ))
        renseigner_button.click()
        print("Clicked on 'Renseigner les informations et payer' button.")

        # Switch to the payment iframe
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//iframe[@title='Secure payment input frame']")
        ))
        print("Switched to payment iframe.")

        card_number_input = wait.until(EC.visibility_of_element_located((By.ID, "Field-numberInput")))
        expiry_input = wait.until(EC.visibility_of_element_located((By.ID, "Field-expiryInput")))
        cvc_input = wait.until(EC.visibility_of_element_located((By.ID, "Field-cvcInput")))

        driver.execute_script("arguments[0].value = '';", card_number_input)
        driver.execute_script("arguments[0].value = '';", expiry_input)
        driver.execute_script("arguments[0].value = '';", cvc_input)


        card_number_input.send_keys(card_number)
        expiry_input.send_keys(card_expiry)
        cvc_input.send_keys(card_cvc)

        print("Filled in credit card details.")

        driver.switch_to.default_content()

        final_pay_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='submit' and contains(., 'Valider et payer')]")
        ))
        final_pay_button.click()
        print("Clicked on 'Valider et payer' button. Payment process initiated.")
    except Exception as e:
        print("Error during reservation processing:", str(e))

def main():
    clicked_slot = check_availability()
    print(f"Reservation clicked: {clicked_slot}")
    process_reservation()

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
