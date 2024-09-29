import logging
import time
import random
### Importing the necessary telegram modules ###
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

### Selenium the boss
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global variables
user_cookies = {}
user_platforms = {}
active_drivers = {}


executor = ThreadPoolExecutor(max_workers=4)  # To run Selenium tasks in a separate thread

# Conversation states
CHOOSING_PLATFORM, RECEIVING_COOKIE = range(2)

# Keyboard for platform selection
PLATFORM_KEYBOARD = [['LinkedIn', 'Internshala']]

# Start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(PLATFORM_KEYBOARD, one_time_keyboard=True)
    await update.message.reply_text(
        "Welcome! Please choose the platform you want to submit cookies for:",
        reply_markup=reply_markup
    )
    return CHOOSING_PLATFORM

# Handle platform selection
async def choose_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    platform = update.message.text.lower()

    if platform in ['linkedin', 'internshala']:
        user_platforms[chat_id] = platform
        await update.message.reply_text(f"Platform '{platform}' chosen. Now, please send your cookie.")
        return RECEIVING_COOKIE
    else:
        await update.message.reply_text("Invalid platform. Please choose either LinkedIn or Internshala.")
        return CHOOSING_PLATFORM

# Handle cookie reception
async def receive_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    cookie_value = update.message.text.strip()

    # Store the cookie for the chosen platform
    platform = user_platforms.get(chat_id)
    if platform:
        user_cookies[chat_id] = {
            'platform': platform,
            'cookie_value': cookie_value
        }
        await update.message.reply_text(f"Cookie for {platform} received! You can now use /apply to start the application process or /stop to stop the application process.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please choose a platform first using /start.")
        return RECEIVING_COOKIE

# Apply for jobs based on the chosen platform
async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data = user_cookies.get(chat_id)

    if not user_data:
        await update.message.reply_text("Please send your cookie first using /start.")
        return

    platform = user_data['platform']
    cookie_value = user_data['cookie_value']

    if platform == 'linkedin':
        executor.submit(apply_for_linkedin_jobs, cookie_value, chat_id)
        await update.message.reply_text("LinkedIn application process Ongoing.")

    elif platform == 'internshala':
        executor.submit(apply_for_internshala_jobs, cookie_value, chat_id)
        await update.message.reply_text("Internshala application process Ongoing.")

    else:
        await update.message.reply_text("Internshala application process started.")
        await update.message.reply_text("Unknown platform.")

# Stop the process and clear user data
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in active_drivers:
        active_drivers[chat_id].quit()  # Quit WebDriver session
        del active_drivers[chat_id]
    if chat_id in user_cookies:
        del user_cookies[chat_id]
    if chat_id in user_platforms:
        del user_platforms[chat_id]
    await update.message.reply_text("Process stopped. You can start again using /start.")

def click_until_input_fields_or_submit(driver, chat_id):
    while True:
        if chat_id not in user_cookies:
            break
        try:
            continue_button = driver.find_element(By.CSS_SELECTOR, "button.artdeco-button--primary")
            continue_button.click()
            time.sleep(2)
            
            # Check for input fields to answer
            try:
                questions = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--input")
                if questions:
                    print("Answering questions...")
                    for question in questions:
                        if question.get_attribute('value') == '':
                            question.send_keys(random.randint(1, 99))  # Example of answering with random number
                        else:
                            question.clear()
                            question.send_keys(random.choice(['yes', 'no']))

            except NoSuchElementException:
                print("No questions found, continuing...")

            # Try selecting checkboxes
            try:

                checkbox_3_years = driver.find_elements(By.TAG_NAME, 'label')
                for checkbox in checkbox_3_years:
                    if "Upload resume" not in checkbox.text:
                        if checkbox.text:
                            checkbox.click()
            except:
                pass

            # Handle dropdowns
            try:
                select_elements = driver.find_elements(By.TAG_NAME, 'select')
                for select in select_elements:
                    dropdown = Select(select)
                    options = dropdown.options
                    valid_options = [option for option in options if option.text != "Select an option"]
                    if valid_options:
                        chosen_option = random.choice(valid_options)
                        dropdown.select_by_visible_text(chosen_option.text)
                        print(f"Selected option: {chosen_option.text}")

            except:
                pass

        except NoSuchElementException:
            print("No more 'Continue' buttons found.")
            break

def apply_for_linkedin_jobs(linkedin_cookie,chat_id):
    PHONE = '654930195'  # Your phone number
    options = Options()
    options.add_argument("--disable-web-security")
    options.add_argument("--user-data-dir=/tmp/user-data")
    options.add_argument("--allow-running-insecure-content")
    options.headless = False
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    active_drivers[chat_id] = driver  # Store the active driver
    try:
        driver.get("https://www.linkedin.com")
        driver.add_cookie({"name": "li_at", "value": linkedin_cookie})
        driver.refresh()

        # Navigate to jobs
        driver.get("https://www.linkedin.com/jobs/search/?currentJobId=2988959962&f_WT=2&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true&start=25")
        time.sleep(3)

        while True:
            element = driver.find_element(By.CLASS_NAME, "global-footer-compact")
            driver.execute_script("arguments[0].scrollIntoView();", element)
            all_listings = driver.find_elements(By.CSS_SELECTOR, "a.job-card-container__link")
            if not all_listings:
                break
            for listing in all_listings:
                try:
                    listing.click()
                    time.sleep(2)
                    apply_button = driver.find_element(By.CSS_SELECTOR, "button.jobs-apply-button")
                    if 'Easy Apply' in apply_button.text:
                        apply_button.click()
                        time.sleep(2)
                        
                        try:
                            phone_input = driver.find_element(By.CLASS_NAME, "artdeco-text-input--input")
                            if not phone_input.get_attribute('value'):
                                phone_input.send_keys(PHONE)
                        except NoSuchElementException:
                            pass

                        click_until_input_fields_or_submit(driver, chat_id)
                        
                        submit_button = driver.find_element(By.CSS_SELECTOR, "button.artdeco-button--primary")
                        submit_button.click()
                        time.sleep(5)
                        close_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Dismiss"]')
                        close_button.click()
                    else:
                        continue
                except Exception as e:
                    print(f"Error during job application: {e}")
                    continue
    finally:
        driver.quit()


def apply_for_internshala_jobs(internshala_cookie,chat_id):
    options = Options()
    options.add_argument("--disable-web-security")
    options.add_argument("--user-data-dir=/tmp/user-data")
    options.add_argument("--allow-running-insecure-content")
    options.headless = False
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    active_drivers[chat_id] = driver  # Store the active driver

    try:
        driver.get("https://internshala.com/")  ### loading internshala 
        driver.add_cookie({"name": "PHPSESSID", "value": internshala_cookie}) ## Here we are using the PHPSESSID as a cookie name
        driver.refresh()

        # Navigate to jobs
        driver.get("https://internshala.com/jobs/work-from-home/")
        time.sleep(3)
        ### Now let's start the application process
        while True:
            # element = driver.find_element(By.CSS_SELECTOR, "a.hideUndoOnClick")
            # driver.execute_script("arguments[0].scrollIntoView();", element)
            all_listings = driver.find_elements(By.CLASS_NAME, "internship-heading-container")
            if not all_listings:
                break
            time.sleep(2)
            for listing in all_listings:
                time.sleep(2)
                listing.click()
                time.sleep(2)
                try: 
                    apply_button = driver.find_elementfind_element(By.ID,"continue_button")
                    apply_button.click()
                    time.sleep(2)
                except:
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.ID, "continue_button")))
                    apply_button = driver.find_element(By.ID, "continue_button")
                    apply_button.click()
                    time.sleep(2)
                

                    #### NOw, let's check if we are being asked a question before moving forward

                try:
                    print("na here i dey ")
                    question_button = driver.find_elements(By.CLASS_NAME, "question-heading")
                    store = ""
                    for q in question_button:
                        store += q.text         ## store all the texts gotten from the page
                    if  'Assessment' in store:
                            wait  = WebDriverWait(driver, 10)
                            exit = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="easy_apply_modal_close"]')))
                            exit.click()
                            print("found it")
                            time.sleep(2)
                            exit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="easy_apply_modal_close_confirm_exit"]')))
                            exit_button.click()
                            print('QWEQWEQWEWQE')
                            time.sleep(2)


                            ### easy apply button
                    else:
                            try:       ### cover letter clicking
                                cover_letter_button = driver.find_element(By.CLASS_NAME, "copyCoverLetterTitle")
                                cover_letter_button.click()
                                time.sleep(2)
                            except:
                                pass

                            try:  ### clicking the submit button
                                submit = driver.find_element(By.NAME, "submit")
                                submit.click()
                                time.sleep(2)
                                print("trying to submit ")

                            except:
                                pass

                            try:

                                close_button = driver.find_element(By.ID, "dismiss_similar_job_modal")
                                close_button.click()
                                time.sleep(2)
                            except:
                                close_button = driver.find_element(By.ID, "dismiss_similar_job_modal")  
                                close_button.click()
                                time.sleep(2)
                                continue

                except:
                   ### CONTINUING THE PROCESS ####

                    pass
    finally:
        driver.quit()
                

                


def main():
    BOT = 'ENTER-YOURS-HERE'
    app = Application.builder().token(BOT).build()

    # Conversation handler for platform selection and cookie submission
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_platform)],
            RECEIVING_COOKIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_cookies)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    # Add handlers
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("apply", apply))
    app.add_handler(CommandHandler("stop", stop))

    # Start polling for updates
    app.run_polling()

if __name__ == '__main__':
    main()
