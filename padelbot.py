import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Use new headless mode for Chrome 109+
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    # Disable images for faster page loads
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

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

def check_availability():
    wait = WebDriverWait(driver, 10)
    preferred_times = ["18:00", "19:00", "20:00", "21:00", "22:00"]
    while True:
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

def process_reservation():
    wait = WebDriverWait(driver, 30)
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

        dummy_card = {
            "number": "4785541004106510",
            "expiry": "05/25",
            "cvc": "637"
        }
        card_number_input.send_keys(dummy_card["number"])
        expiry_input.send_keys(dummy_card["expiry"])
        cvc_input.send_keys(dummy_card["cvc"])
        print("Filled in dummy card details.")

        driver.switch_to.default_content()

        final_pay_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='submit' and contains(., 'Valider et payer')]")
        ))
        final_pay_button.click()
        print("Clicked on 'Valider et payer' button. Payment process initiated.")
    except Exception as e:
        print("Error during reservation processing:", str(e))

def main():
    email = "clarence-dion@orange.fr"
    password = "Claclapadel2002!"
    login(email, password)
    clicked_slot = check_availability()
    print(f"Reservation clicked: {clicked_slot}")
    process_reservation()

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
