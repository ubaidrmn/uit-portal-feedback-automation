import time

from utils.exceptions import FeedbackFormNotAvailableError
from utils.helpers import (
    fetch_environment,
    create_selenium_instance,
    solve_and_submit_feedback,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

UIT_PORTAL_URL, UIT_PORTAL_USERNAME, UIT_PORTAL_PASSWORD = fetch_environment()

if __name__ == "__main__":
    driver = create_selenium_instance()

    driver.get(UIT_PORTAL_URL)

    # Enter the username & password values

    username_input = driver.find_elements(
        By.CSS_SELECTOR, "#updatepanel > div.form-group > input"
    )[0]
    username_input.send_keys(UIT_PORTAL_USERNAME)

    password_input = driver.find_elements(
        By.CSS_SELECTOR, "#updatepanel > div.form-group > input"
    )[1]
    password_input.send_keys(UIT_PORTAL_PASSWORD)

    # Press login

    login_button = driver.find_element(By.CSS_SELECTOR, "#btnlgn")
    login_button.click()

    # Open the feedback page if available else throw error

    general_list = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#ctl00_leftAccordion li:nth-child(2)")
        )
    )
    li_elements = general_list.find_elements(By.CSS_SELECTOR, "div > ul > li")

    time.sleep(2)

    feedback_form_not_available = True

    for li in li_elements:
        try:
            li_anchor_element = li.find_element(By.CSS_SELECTOR, "a")
            li_anchor_element_text = li_anchor_element.get_attribute(
                "innerText"
            ).lower()
            li_anchor_element_href = li_anchor_element.get_attribute("href")

            if (
                "feedback" in li_anchor_element_text
                and li_anchor_element_href
                and li_anchor_element_href != "#"
            ):
                feedback_form_not_available = False
                driver.get(li_anchor_element_href)

        except Exception as err:
            pass

    if feedback_form_not_available:
        raise FeedbackFormNotAvailableError("No feedback form found :(")

    # Open individual feedback pages from feedback table

    feedback_table = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "table.rgMasterTable"))
    )
    feedback_table_rows = feedback_table.find_elements(By.CSS_SELECTOR, "tr")

    all_feedbacks_already_submitted = True
    solved_feedbacks = 0

    for x in range(0, len(feedback_table_rows)):
        for row in feedback_table_rows[1:]:
            cols = row.find_elements(By.CSS_SELECTOR, "td")

            if "not submitted" in cols[7].get_attribute("innerText").lower():
                all_feedbacks_already_submitted = False
                print("[FEEDBACK_AUTOMATION: Found an unsubmitted feedback!]")
                cols[8].click()

                # Wait for feedback page to load

                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#btnSubmit"))
                )

                # Solve & submit the feedback

                solve_and_submit_feedback(driver)
                print("[FEEDBACK_AUTOMATION: Feedback submitted!]")
                solved_feedbacks += 1
                time.sleep(2)

                break

        # Update feedback_table as it has become stale now

        feedback_table = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "table.rgMasterTable"))
        )
        feedback_table_rows = feedback_table.find_elements(By.CSS_SELECTOR, "tr")

    if all_feedbacks_already_submitted:
        print("[FEEDBACK_AUTOMATION: No unsubmitted feedbacks found!]")

    print(f"[FEEDBACK_AUTOMATION: {solved_feedbacks} feedbacks solved]")
    print("[FEEDBACK_AUTOMATION: Finished!]")
