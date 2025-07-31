
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Function to go to the BC Parks page and click on the 'Book a pass for Joffre Lakes' button
def GoToBCParksPage(driver):
    driver.get("https://reserve.bcparks.ca/dayuse/")
    
    try:
        # Wait until the button with aria-label containing 'Joffre' is clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Joffre')]"))
        )

        # Scroll the button into view before clicking it
        driver.execute_script("arguments[0].scrollIntoView(true);", button)

        # Wait for the button to become clickable again after scrolling
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(button)
        )

        # Click the button to proceed
        driver.execute_script("arguments[0].click();", button)

        print("Navigated to the Joffre Lakes page!")

    except Exception as e:
        print(f"An error occurred while navigating to the page: {e}")

# Function to select the "Joffre Lakes - Trail" pass type from the dropdown
def SelectPass(driver):
    try:
        # Wait for the select dropdown to appear (after clicking the button)
        pass_type_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "passType"))
        )

        # Create a Select object for the dropdown
        select = Select(pass_type_select)

        # Select the first option by index (1 for "Joffre Lakes - Trail")
        select.select_by_index(1)  # Index 1 will select the "Joffre Lakes - Trail" option

        print("Selected 'Joffre Lakes - Trail' option!")

    except Exception as e:
        print(f"An error occurred while selecting the pass: {e}")

# Function to check if the pass availability is "Full"
def CheckPassAvailability(driver):
    try:
        # Wait for the availability element to appear
        availability_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-testid='day-availability-text']"))
        )

        # Check if the class 'Full' is present in the <span> tag
        full_status = availability_text.find_element(By.CSS_SELECTOR, "span.Full")

        if full_status:
            print("Pass availability is Full!")
            return True

    except Exception as e:
        print(f"An error occurred while checking availability: {e}")
        return False

    return False

# Function to play a sound using afplay (macOS only)
def PlaySound(sound_type="full"):
    if sound_type != "full":
        # Play a sound when the pass is full
        os.system("afplay /System/Library/Sounds/Blow.aiff")  # Sound when pass is full
    #else:
        # Play a different sound when the pass is not available (e.g., unavailable)
        # os.system("afplay /System/Library/Sounds/Funk.aiff")  # Sound when pass is not available

def SetDate(driver):
    try:
        # Open the datepicker
        calendar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Select a Date']"))
        )
        #calendar_btn.click()
        driver.execute_script("arguments[0].click();", calendar_btn)
        print("Opened calendar")

        next_month_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next month']"))
        )

        time.sleep(0.5)  # Just to ensure smooth transition
        driver.execute_script("arguments[0].click();", next_month_btn)
        print("Clicked next month")

        # Wait and click the date with aria-label "Thursday, July 31, 2025" (change to Saturday, August 2, 2025 to test on the day)
        target_label = "Saturday, August 2, 2025"
        date_cell = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"div[aria-label='{target_label}']"))
        )
        #date_cell.click()
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", date_cell)
        print(f"Selected Date {target_label}")

    except Exception as e:
        print(f"Failed to select date: {e}")

# Function to refresh the page and repeat the process every 3 minutes
def MonitorPassAvailability():
    while True:

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        # Go to the BC Parks page
        GoToBCParksPage(driver)

        # SetDate
        # Select the pass
        SelectPass(driver)

        SetDate(driver)

        driver.delete_all_cookies()
        driver.refresh()
        driver.delete_all_cookies()
        time.sleep(0.1)

        SelectPass(driver)

        SetDate(driver)
        # Check pass availability
        if CheckPassAvailability(driver):
            # If pass is Full, play a sound for "Full"
            PlaySound("full")
        else:
            # If pass is not Full, play a sound for "available"
            PlaySound("available")

            try:
                # this portion is untested as I couldn't find exact element tags for when a ticket becomes available
                # Wait until the radio button becomes clickable (i.e., enabled)
                day_radio = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "visitTimeDAY"))
                )
                driver.execute_script("arguments[0].click();", day_radio)
                print("Clicked the DAY radio button!")

                # Wait for the #passCount select dropdown to appear
                pass_count_select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "passCount"))
                )

                # Create Select object and get all available options
                select = Select(pass_count_select)
                options = select.options

                if len(options) > 1:
                    # Select the last option (skipping placeholder at index 0)
                    select.select_by_index(len(options) - 1)
                    print(f"Selected {options[-1].text} pass(es)")
                else:
                    print("No valid pass options available.")

                # stall for 7 mins so we can book manually 
                time.sleep(420)
            except Exception as e:
                print(f"Error while selecting time or number of passes: {e}")


        driver.quit()

        # Wait for 3 minutes before refreshing and checking again
        print("Waiting for 1 seconds before checking again...")
        time.sleep(1)  # Wait for 3 minutes (180 seconds)
        

# Main function to run the script
def main():
    MonitorPassAvailability()


# Execute the main function when the script is run
if __name__ == "__main__":
    main()
