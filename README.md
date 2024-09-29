# Telegram-BO-for-Automatic-Job-application-for-linkedin-and-Telegram
This bot automates the process of applying for jobs on LinkedIn and Internshala using Selenium WebDriver. Users can submit their cookies for either platform, and the bot will handle job applications, including answering questions and submitting applications automatically
## Features 
. User-friendly interface through Telegram.  
. Supports LinkedIn and Internshala for job applications.
. Receives user cookies securely.  
. Asynchronous job application handling using a thread pool.

## Requirements
. Python 3.x
. Libraries:
. python-telegram-bot
. selenium
. concurrent.futures
. logging
. Setup Instructions
. Install Required Libraries:
. bash
. Copy code
. pip install python-telegram-bot selenium


Set Up Selenium WebDriver:
Ensure you have the Chrome WebDriver installed and accessible in your system PATH.
Modify the path in Service(executable_path="/usr/bin/chromedriver") if necessary.
Get Your Bot Token:
Create a new bot on Telegram using BotFather and obtain the bot token.
Run the Bot:
Execute the script and interact with the bot through Telegram.
Code Structure
Main Components
Imports and Logging Configuration:
Standard Python libraries and Telegram bot libraries are imported.
Logging is configured for debugging.
Global Variables:
user_cookies: Stores user cookies for different chat IDs.
user_platforms: Maps user chat IDs to their chosen platforms.
active_drivers: Tracks active Selenium WebDriver instances for users.
Conversation States:
CHOOSING_PLATFORM and RECEIVING_COOKIE: Used to manage the conversation flow with users.
Keyboards:
PLATFORM_KEYBOARD: A simple keyboard layout for platform selection.
## Bot Handlers
### start(update, context):
Initiates the conversation and prompts the user to select a platform.
### choose_platform(update, context):
Handles user platform selection and prompts for cookie submission.
### receive_cookies(update, context):
Receives and stores the user's cookie for the selected platform.
### apply(update, context):
Initiates the job application process for the selected platform using the stored cookie.
### stop(update, context):
Stops the current job application process, quitting the Selenium driver and clearing user data.

## Selenium Automation Functions
click_until_input_fields_or_submit(driver, chat_id):
Clicks buttons and fills in input fields until the job application is complete.
apply_for_linkedin_jobs(linkedin_cookie, chat_id):
Automates job applications on LinkedIn using the provided cookie.
apply_for_internshala_jobs(internshala_cookie, chat_id):
Automates job applications on Internshala using the provided cookie.
### Main Function
main():
Initializes the bot and adds command handlers for starting conversations, applying for jobs, and stopping processes.
## Usage

### Start the Bot:
Type /start to initiate the conversation.
### Select Platform:
Choose between LinkedIn or Internshala.
### Submit Cookie:
Provide your session cookie for the selected platform.
### Apply for Jobs:
Use the /apply command to start the application process.
### Stop Process:
Use the /stop command to terminate any ongoing job application processes.

## Logging

Logs are generated during the bot's execution, providing insights into the application's flow and errors. Monitor the console output for debugging and operational status.
## Conclusion
This bot streamlines the job application process on LinkedIn and Internshala, making it easier for users to apply for positions without manual input. For any issues or feature requests, please check the codebase or open an issue in the repository.
