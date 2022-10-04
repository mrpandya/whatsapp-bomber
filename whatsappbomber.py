#############
# LIBRARIES #
#############
import sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
import platform
from colorama import Fore, init as colorama_init
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

###########################
# LIBRARY INITIALIZATIONS #
###########################
colorama_init(autoreset=True)

#############
# VARIABLES #
#############
enable_logs = True

#############
# CONSTANTS #
#############
URL = "https://web.whatsapp.com/"

OS = platform.system()

# Utility colors
COLOR_COLON = Fore.CYAN
COLOR_LINE_SEPARATOR = Fore.MAGENTA
COLOR_PROMPT = Fore.YELLOW
COLOR_TITLE = Fore.GREEN
COLOR_INPUT = Fore.MAGENTA
COLOR_LOG_INFO = Fore.YELLOW
COLOR_LOG_ERROR = Fore.RED
COLOR_LOG_SUCCESS = Fore.GREEN
COLOR_INPUT_DELIMITER = Fore.LIGHTBLUE_EX

# Webdriver
WEBDRIVER_WAIT_TIMEOUT = 60


#############
# FUNCTIONS #
#############
def get_input(message: str) -> str:
    # Get input
    result = input(COLOR_PROMPT + message + f"{COLOR_COLON}:\n  {COLOR_INPUT_DELIMITER}-> {COLOR_INPUT}")

    # Reset the color
    print("", end=Fore.RESET)

    # Return the input
    return result


def log(level: str, message: str, hierarchy_level=0) -> None:
    if enable_logs:
        # Color if no defined level
        color = Fore.WHITE

        # Check the level and assign the respective colors to color
        if level.lower() == "info":
            color = COLOR_LOG_INFO
        elif level.lower() == "error":
            color = COLOR_LOG_ERROR
        elif level.lower() == "success":
            color = COLOR_LOG_SUCCESS

        # New line length for when there is a new line in message
        new_line_length = len(level) + 4

        # Split messages into lines
        messages = message.split("\n")

        # Calculating amount of space to print for hierarchy
        hierarchy_space = " " * (4 * hierarchy_level) if hierarchy_level > 0 else ""

        # Loop through the list of messages
        for i, msg in enumerate(messages):
            # If first time printing message
            if i == 0:
                # print the message with the level
                print(f"{hierarchy_space}{color}[ {level.upper()} ] {msg.title()}")
            else:
                # ignore the level and print the message only
                print(f" " * new_line_length + f"{hierarchy_space}" + f"{Fore.YELLOW} {msg.title()}")


def clear_screen() -> None:
    if OS.lower().startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


def separate_line() -> None:
    print(f"{COLOR_LINE_SEPARATOR}------------------------------")


def start_bot(names: list, messages: list, driver: any) -> None:
    # Local variables
    wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT)

    # Logic/Actual Code
    log("info", "bot starting...")
    driver.maximize_window()

    log("info", "Opening whatsapp...")
    driver.get(URL)
    log("success", "Successfully opened whatsapp!")

    # @Wait for person to verify the link
    log("info", "Awaiting manual authentication...")
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/header/div[1]/div/img")))
    log("success", "Authentication successful!")

    # Pause for page to load and syncing
    log("info", "Waiting for synchronization and full page...")
    time.sleep(15)

    # Get the chat list container
    log("info", "Getting chat list...")
    chat_list_container = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/div/div")))

    chat_list = chat_list_container.find_elements(by=By.XPATH, value="./child::*")

    log("success", "Found chat list!")

    # make all names lower case
    names = [name.lower() for name in names]

    log("info", "Iterating over list...")
    for i, contact in enumerate(chat_list):
        log("info", f" ITERATION#{i+1}", hierarchy_level=1)

        contact_name = contact.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span").text
        log(f"info", f"Name: {contact_name.title()}", hierarchy_level=2)

        # if i >= 0:
        if contact_name.lower() in names:
            log("info", "Clicking on contact...", hierarchy_level=2)
            contact.click()

            log("info", "Clicking on text box", hierarchy_level=2)
            text_box = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]")))
            text_box.click()

            # Loop through messages list and send them one by one
            log("info", "Sending messages", hierarchy_level=2)
            for message in messages:
                log(f"info", f"Writing: {message}", hierarchy_level=3)
                text_box.send_keys(message)

                # Wait for brief moment before sending to ensure full reliability
                log(f"info", f"WAITING", hierarchy_level=4)
                time.sleep(0.4)

                log(f"info", f"Sending the message...", hierarchy_level=4)
                # Get send button element
                send_button = wait.until(EC.presence_of_element_located(("xpath", "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button")))
                wait.until(EC.element_to_be_clickable(send_button))
                # send the message
                send_button.click()
                log("success", "Message sent successfully", hierarchy_level=4)

            # Remove the current name from the list
            names.remove(contact_name.lower())

            # Delay for x seconds before moving on to next person
            time.sleep(0.5)

    # Check if there are still contacts in the list
    if len(names) > 0:
        log("error", f"need to send messages to: {names}")
        log("info", "Using other method for remaining people...")

        # Get the search box
        log("info", "Getting search box...")
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/div/div/div[2]/div/div[2]")))
        log("success", "Successfully got search box!")

        log('info', "Iterating over remaining contacts...")
        # Loop through remaining contact names
        names = [name.lower() for name in names]

        for i, name in enumerate(names):
            log("info", f"Remaining Contact#{i+1}: {name}", hierarchy_level=1)

            # Clear search box text
            log("info", "Clearing search text...", hierarchy_level=2)

            # Click on search box three times to select all text
            search_box.click()
            search_box.clear()

            log("success", "Search text clear!", hierarchy_level=2)

            # Type the name in the search box
            log("info", f"Typing '{name.title()}' in the search box...", hierarchy_level=2)
            search_box.send_keys(name)

            # Search
            log("info", f"Searching...", hierarchy_level=2)
            search_box.send_keys(Keys.ENTER)

            # Pause for everything to load
            log("info", "WAITING", hierarchy_level=2)
            time.sleep(1)
            log("success", "Search successful!", hierarchy_level=2)

            # If no contact name appears, print error and go to next iteration
            try:
                if driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/span").text == "No chats, contacts or messages found":
                    log("error", f"Contact(Name: {name}) was not found!", hierarchy_level=2)
                    if not i == len(names) - 1:
                        log("info", "Skipping to next iteration!", hierarchy_level=2)
                    time.sleep(0.5)
                    # Skip to next iteration
                    continue
            except Exception as e:
                pass

            # Get results
            search_results_container = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="pane-side"]')))
            search_results = search_results_container.find_elements(by=By.XPATH, value="./child::*")

            print(f"SEARCH RESULTS: {search_results}\nLENGTH: {len(search_results)}")

            # Pressing enter automatically selects first contact, so no need to reselect it
            log("success", "Contact selected successfully!", hierarchy_level=3)

            # Send messages to that contact
            log("info", "Clicking on text box", hierarchy_level=3)
            text_box = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                  "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]")))
            text_box.click()

            log("info", "Sending messages", hierarchy_level=3)
            for message in messages:
                log(f"info", f"Writing: {message}", hierarchy_level=4)
                text_box.send_keys(message)

                # Wait for brief moment before sending to ensure full reliability
                log(f"info", f"WAITING", hierarchy_level=5)
                time.sleep(0.4)

                log(f"info", f"Sending the message...", hierarchy_level=5)
                # Get send button element
                send_button = wait.until(EC.presence_of_element_located(("xpath", "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button")))
                wait.until(EC.element_to_be_clickable(send_button))
                # send the message
                send_button.click()
                log("success", "Message sent successfully", hierarchy_level=5)

            # Sleep for brief moment
            log("info", "WAITING", hierarchy_level=2)
            time.sleep(0.7)


def main() -> None:
    # Global vars
    global enable_logs

    # Clearing the screen before running
    clear_screen()

    # Logo
    separate_line()
    print(f"{COLOR_TITLE}W H A T S A P P    B O M B E R")
    separate_line()

    # Get required data

    # Get names of contacts/groups to send the message to
    names = get_input(f"Enter the contact/group names separated by a comma(,)")
    messages = get_input("Enter the message(s) that you want to send separated by a comma(,)")
    enable_logs = get_input("Enable logs to view progress of the bot? [ True/False ]").lower()
    browser = get_input("Which browser to use?/What browser do you have installed? [ Chrome/FireFox ]").lower()

    # Convert enable logs to boolean
    if enable_logs.startswith("t") or enable_logs == "1":
        enable_logs = True
    elif enable_logs.startswith("f") or enable_logs == "0":
        enable_logs = False
    else:
        enable_logs = True

    # clear_screen()

    # Convert names and messages to list if they are not singular

    # Check if there are more names
    if "," in names:
        names = names.split(",")

    # Check if there are more than one messages
    if "," in messages:
        messages = messages.split(",")

    # Remove unnecessary spaces from names list and messages list
    names = [name.strip() for name in names]
    messages = [msg.strip() for msg in messages]

    # Initialize the driver
    log("info", "Initializing web driver...")
    log("info", "Installing the web driver...")

    # Check what browser user wished and initialize driver accordingly
    if browser.startswith("ch"):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser.startswith("fir"):
        try:
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        except Exception as e:
            log("error", "Unable to automatically install geckodriver!\nTrying manual mode instead...")
            try:
                # Use geckodriver, assuming it is in same path
                path = "./geckodriver" if OS.lower().startswith("lin") else "geckodriver.exe"
                service = FirefoxService(executable_path=path)
                driver = webdriver.Firefox(service=service)
            except Exception as e:
                log("error", "Unable to get geckodriver manually!")
                log("info", "Quitting...")
                sys.exit()
    else:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    log("success", "Successfully initialized web driver!")

    # Start the bot
    start_bot(names, messages, driver)


#####################
# PROGRAM EXECUTION #
#####################
if __name__ == "__main__":
    # Run main function
    main()
