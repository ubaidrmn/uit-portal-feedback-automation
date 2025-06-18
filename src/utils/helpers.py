import os
import time
import chromedriver_autoinstaller

from dotenv import load_dotenv
from utils.exceptions import EnvironmentNotConfiguredError
from typing import Tuple
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_environment() -> Tuple[str, str, str]:
    load_dotenv()

    uit_portal_url = os.getenv("UIT_PORTAL_URL")
    uit_portal_username = os.getenv("UIT_PORTAL_USERNAME")
    uit_portal_password = os.getenv("UIT_PORTAL_PASSWORD")

    if not uit_portal_url or not uit_portal_username or not uit_portal_password:
        raise EnvironmentNotConfiguredError(
            "You have not properly set the environment variables required to run this program! Please refer to the README.md file present in the root of the project."
        )

    return uit_portal_url, uit_portal_username, uit_portal_password


def create_selenium_instance(headless: bool = False):
    chromedriver_autoinstaller.install()

    options = Options()

    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1250,1000")

    if headless:
        options.add_argument("--headless=old")

    driver = webdriver.Chrome(options=options)

    return driver


def solve_and_submit_feedback(driver: webdriver.Chrome):

    # Solve the form

    driver.execute_script(
        """
            const questions = document.querySelectorAll('div.ansMainDiv');
            const responses = [
            "Good!",
            "Great job!",
            "Well done!",
            "Excellent work!",
            "Keep it up!",
            "Nice effort!",
            "You're doing awesome!",
            "Fantastic!",
            "Outstanding!",
            "Impressive!",
            "Superb!",
            "You're on the right track!",
            "Nice progress!",
            "That’s the way to go!",
            "Perfect!",
            "Awesome work!"
        ];
            questions.forEach(question => {
                let inputEl = question.querySelectorAll('input')[Math.floor(Math.random() * 4)];
                let textEl = question.querySelector('textarea');
                if (inputEl) {
                    inputEl.click();
                } else if (textEl) {
                    textEl.value = responses[Math.floor(Math.random() * responses.length)];
                }
            })
        """
    )

    # Click on the submit button

    submit_btn = driver.find_element(By.CSS_SELECTOR, "#btnSubmit")
    submit_btn.click()

    time.sleep(2)

    # Wait for the window alert & accept it

    WebDriverWait(driver, 15).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()

    time.sleep(2)

    # Wait for the proceed to portal button and then click on it

    proceed_to_portal_btn = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#btnbackToPortal"))
    )
    proceed_to_portal_btn.click()
