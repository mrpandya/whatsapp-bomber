#############
# LIBRARIES #
#############
import sys

import colorama
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

TERMINAL_SIZE = os.get_terminal_size()

VERSION = "0.6.8"

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

# APP TITLE COLORS
APP_VERSION_COLOR = Fore.YELLOW

APP_INPUT_COLOR = Fore.LIGHTYELLOW_EX
APP_INPUT_SEPARATOR_COLOR = Fore.BLUE

# MAIN MENU COLORS
MAIN_MENU_TITLE_COLOR = Fore.BLUE

MAIN_MENU_OPTIONS_NUMBER_COLOR = Fore.LIGHTBLUE_EX
MAIN_MENU_OPTIONS_TEXT_COLOR = Fore.LIGHTMAGENTA_EX

MAIN_MENU_DISCLAIMER_WARNING_COLOR = Fore.RED

MAIN_MENU_EXIT_MESSAGE_COLOR = Fore.YELLOW

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
                pretty_print(f"{hierarchy_space}{color}[ {level.upper()} ] {msg.title()}", align="left", back_separator=False, front_separator=False)
            else:
                # ignore the level and print the message only
                pretty_print(f" " * new_line_length + f"{hierarchy_space}" + f"{Fore.YELLOW} {msg.title()}")


def clear_screen() -> None:
    if OS.lower().startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


def separate_line() -> None:
    columns = os.get_terminal_size().columns

    print(f"{Fore.CYAN}| {COLOR_LINE_SEPARATOR}{'-' * (columns-4)} {Fore.CYAN}|")


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

    pretty_print(f"{Fore.YELLOW}Press {Fore.CYAN}ENTER to exit!", align="left", back_separator=False, front_separator=False)
    pretty_print("")


def main() -> None:
    # Global vars
    global enable_logs

    # Clearing the screen before running
    clear_screen()

    # Print title
    print_title()

    # Get required data

    # Get names of contacts/groups to send the message to
    names = pretty_input(f"{Fore.BLUE}Enter the contact/group names separated by a comma(,)")
    messages = pretty_input(f"{Fore.BLUE}Enter the message(s) that you want to send separated by a comma(,)")
    enable_logs = pretty_input(f"{Fore.BLUE}Enable logs to view progress of the bot? [ True/False ]").lower()
    browser = pretty_input(f"{Fore.BLUE}Which browser to use?/What browser do you have installed? [ Chrome/FireFox ]").lower()

    # Convert enable logs to boolean
    if enable_logs.startswith("t") or enable_logs == "1":
        enable_logs = True
    elif enable_logs.startswith("f") or enable_logs == "0":
        enable_logs = False
    else:
        enable_logs = True

    clear_screen()

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


def check_color_string_in_dict(string: str, dictionary: dict, pattern_look_len: int) -> (bool, int):
    count = 0
    for index, char in enumerate(string):
        if char == "\x1b":
            full_pattern = string[index: index+pattern_look_len]

            if full_pattern in dictionary.values():
                count += 1

    if count == 0:
        return False, count
    else:
        return True, count


def pretty_input(prompt: str):
    if not prompt.strip() == "":
        pretty_print(prompt, align="left", back_separator=False, front_separator=False)
    user_input = input(f"{Fore.CYAN}| {APP_INPUT_SEPARATOR_COLOR}-> {APP_INPUT_COLOR}").lower()
    separate_line()
    return user_input


def pretty_print(text: str, align="center", blank_character=" ", back_separator=True, front_separator=True) -> None:
    """Print function, with alignment and aesthetics - Made by IamMU with 💗 for Whatsapp Bomber in Hacktoberfest"""

    align = align.lower()

    colored_text = text

    for color in Fore.__dict__:
        text = text.replace(Fore.__dict__[color], "")

    uncolored_text = text

    # Get updated terminal size
    terminal_size_h = os.get_terminal_size().columns

    # Lengths
    colored_text_length = len(colored_text)
    uncolored_text_length = len(uncolored_text)

    # Buffers
    uncolored_text_buffer = list()
    colored_text_insertion_buffer = list()
    finalized_text_buffer = list()

    # Calculating buffers
    available_char_space = terminal_size_h - 4
    if len(uncolored_text) >= available_char_space:
        # Variables for calculation
        position_counter = 0
        last_position = position_counter
        current_text_buffer = str()

        # Calculate uncolored buffer
        for index, unc_char in enumerate(uncolored_text):
            position_counter = (index + 1) - last_position

            # Add the character to the current text buffer
            current_text_buffer += unc_char

            # Check if position counter is greater than available space
            if position_counter >= available_char_space:
                # Add the character in the current_text_buffer to the uncolored buffer
                uncolored_text_buffer.append(current_text_buffer)

                # Set last position to current
                last_position = position_counter + last_position

                # Reset the position counter
                position_counter = 0

                # Reset current text buffer
                current_text_buffer = ""

            # Check if position counter(+ last position to make it current) is last character
            if position_counter + last_position >= uncolored_text_length:
                # Add the character in the current_text_buffer to the uncolored buffer
                uncolored_text_buffer.append(current_text_buffer)

                # Set last position to 0 because end of loop
                last_position = 0

                # Reset the position counter
                position_counter = 0

                # Reset current text buffer
                current_text_buffer = ""

        color_code_chars_length = 5
        without_color_index = 0
        # Calculate color insertion buffer
        for index, c_char in enumerate(colored_text):
            if c_char == "\x1b":
                if not without_color_index - color_code_chars_length <= 0:
                    without_color_index -= color_code_chars_length

                colored_text_insertion_buffer.append(((without_color_index, without_color_index+color_code_chars_length), c_char + colored_text[index+1:index+color_code_chars_length]))

                without_color_index += 1
                continue

            without_color_index += 1
    else:
        uncolored_text_buffer.append(uncolored_text)
        colored_text_insertion_buffer.append(colored_text)

        finalized_text_buffer.append(colored_text)

    if len(uncolored_text) >= available_char_space:

        last_color = ""
        for unc_text in uncolored_text_buffer:
            res = ""
            skip_parent_iteration = False
            last_index = 0
            for index, char in enumerate(unc_text):
                if len(colored_text_insertion_buffer) > 0:
                    for color_insertion in colored_text_insertion_buffer:
                        i = color_insertion[0][0]
                        v = color_insertion[1]

                        if index == i:
                            res += v + char
                            last_color = v
                            colored_text_insertion_buffer.remove(color_insertion)
                            skip_parent_iteration = True

                if skip_parent_iteration:
                    skip_parent_iteration = False
                    continue

                res += char

            if not index == last_index:
                res = last_color + res
                last_index = index

            finalized_text_buffer.append(res)

    for ftext in finalized_text_buffer:
        if len(ftext) > 5:
            is_color, color_count = check_color_string_in_dict(ftext, Fore.__dict__, 5)
            if is_color:
                length_of_text = int(len(ftext) - (color_count * 5))
            else:
                length_of_text = len(ftext)
        else:
            length_of_text = len(ftext)

        # Calculate the amount of space, taking alignment into consideration
        if align == "center":
            # Amount of space is the half of the screen width - the length of the side separators - the half of the text length
            amount_of_space = int((terminal_size_h - 2)/2 - length_of_text/2)

            # Make spacing variables
            space_left = blank_character * amount_of_space
            space_right = blank_character * amount_of_space
        elif align == "right":
            # Amount of space is the screen width - the side separator's length - the text length
            amount_of_space = int((terminal_size_h - 2) - length_of_text)

            space_left = blank_character * (amount_of_space - 1)
            space_right = " "
        elif align == "left":
            # Amount of space is the screen width - the side separator's length - the text length
            amount_of_space = int((terminal_size_h - 2) - length_of_text)

            space_left = " "
            space_right = blank_character * (amount_of_space - 1)

        if len(space_left) + len(space_right) + length_of_text <= terminal_size_h:
            if align == "center":
                space_right = space_right + blank_character * ((terminal_size_h - 2) - (len(space_left) + len(space_right) + length_of_text))
            elif align == "right":
                space_left = space_left + blank_character * ((terminal_size_h - 2) - (len(space_left) + len(space_right) + length_of_text))
            elif align == "left":
                space_right = space_right + blank_character * ((terminal_size_h - 2) - (len(space_left) + len(space_right) + length_of_text))

        result = f"{Fore.CYAN}|{Fore.RESET}" + space_left + ftext + space_right + f"{Fore.CYAN}|"

        finalized_text_buffer[finalized_text_buffer.index(ftext)] = result


    if back_separator:
        separate_line()

    # Print text in finalized text buffer
    for msg in finalized_text_buffer:
        print(msg)

    if front_separator:
        separate_line()


def print_title() -> None:
    # Print version and logo/name
    pretty_print(f"{Fore.GREEN}W H A T S {Fore.LIGHTGREEN_EX}A P P  {Fore.LIGHTMAGENTA_EX}B {Fore.LIGHTYELLOW_EX}O M B {Fore.GREEN}E R", align="center", front_separator=False)
    pretty_print(f"{APP_VERSION_COLOR}version {VERSION}", align="center", back_separator=False)


def customizations_menu() -> None:
    pass


def credits_menu() -> None:
    clear_screen()

    contributors = ["IamMU", "pathikg", "rushabhgandhi13", "b-Istiak-s"]

    # Print credits
    pretty_print(f"{Fore.YELLOW}INFORMATION", align="center")
    pretty_print(f"Whatsapp Bomber is an open-source project made to automate whatsapp messages so you can prioritize tasks, other than managing whatsapp groups.",
                 back_separator=False, align="center")
    pretty_print(f"{Fore.YELLOW}AUTHOR/OWNER", align="center", back_separator=False)
    pretty_print(f"Manan Pandya[ https://github.com/mrpandya ]", align="center", back_separator=False)
    pretty_print(f"{Fore.YELLOW}CONTRIBUTORS", align="center", back_separator=False)

    for contributor in contributors:
        pretty_print(f"{contributor} [ https://github.com/{contributor} ]", align="center", back_separator=False, front_separator=False)

    separate_line()
    input(f"{Fore.CYAN}| {APP_INPUT_COLOR}Press ENTER to return")


def main_menu() -> None:
    clear_screen()

    user_input = str()

    possible_quit_commands = ["exit", "quit", "q", "end", "4", "e"]

    options = ["1", "2", "3", "4", "start bot", "customizations", "credits"]

    error_messages = []

    while not user_input in possible_quit_commands:
        print_title()

        # Print Main Menu Options
        pretty_print(f"{MAIN_MENU_TITLE_COLOR}Main Menu", align="center", back_separator=False)
        pretty_print(f"{MAIN_MENU_OPTIONS_NUMBER_COLOR}1) {MAIN_MENU_OPTIONS_TEXT_COLOR}Start Bot", align="center", back_separator=False, front_separator=False)
        pretty_print(f"{MAIN_MENU_OPTIONS_NUMBER_COLOR}2) {MAIN_MENU_OPTIONS_TEXT_COLOR}Customizations/Settings", align="center", back_separator=False, front_separator=False)
        pretty_print(f"{MAIN_MENU_OPTIONS_NUMBER_COLOR}3) {MAIN_MENU_OPTIONS_TEXT_COLOR}Credits", align="center", back_separator=False, front_separator=False)
        pretty_print(f"{MAIN_MENU_OPTIONS_NUMBER_COLOR}4) {MAIN_MENU_OPTIONS_TEXT_COLOR}Exit", align="center", back_separator=False)

        # Print Disclaimer
        pretty_print(f"{MAIN_MENU_DISCLAIMER_WARNING_COLOR}DO NOT USE FOR SPAM OR ANY OTHER MALICIOUS USE", align="center", back_separator=False)

        # Print all errors if any
        lines_used = 15
        if len(error_messages) > 0:
            if len(error_messages) > TERMINAL_SIZE.lines - lines_used:
                error_messages.pop(0)

            for error in error_messages:
                pretty_print("[ ERROR ] " + error, align="center", back_separator=False, front_separator=False)

            separate_line()

        # Print User Input Prompt
        user_input = pretty_input("")

        # TODO: Options
        # TODO: Make pretty print print big text on different lines
        if user_input in options:
            if user_input.startswith("1") or user_input.startswith("s"):
                main()
            elif user_input.startswith("2") or user_input.startswith("cu"):
                customizations_menu()
            elif user_input.startswith("3") or user_input.startswith("cr"):
                credits_menu()
        else:
            error_messages.append(f"{Fore.YELLOW}Please choose a correct option! {Fore.LIGHTYELLOW_EX}Your previous option '{user_input}' is not valid!")

        # Clear the screen
        clear_screen()

    # Goodbye message
    pretty_print(f"{MAIN_MENU_EXIT_MESSAGE_COLOR}Goodbye!")


#####################
# PROGRAM EXECUTION #
#####################
if __name__ == "__main__":
    clear_screen()
    # Run main function
    # main()

    main_menu()

    ####################
    # TESTS FOR LOGGER #
    ####################
    # pretty_print("-" * TERMINAL_SIZE.columns)
    # pretty_print(f"{Fore.CYAN}" + "*" * int(TERMINAL_SIZE.columns/2))
    # string = Fore.YELLOW + " ".join([str(i) for i in range(100)])
    # pretty_print(string)
    # pretty_print(f"{Fore.YELLOW}Alignment Tests", align="center")
    # pretty_print("[ LEFT ]", align="left", back_separator=False, front_separator=False)
    # pretty_print("[ RIGHT ]", align="right", back_separator=False, front_separator=False)
    # pretty_print("[ CENTER ]", align="center", back_separator=False)
    # pretty_print(f"{Fore.YELLOW}Longer Alignment Tests", back_separator=False)
    # pretty_print("[ THIS TEXT IS ALIGNED TO THE LEFT ]", align="left", back_separator=False, front_separator=False)
    # pretty_print("[ THIS TEXT IS ALIGNED TO THE RIGHT ]", align="right", back_separator=False, front_separator=False)
    # pretty_print("[ THIS TEXT IS ALIGNED TO THE CENTER ]", align="center", back_separator=False)
    # pretty_print(f"{Fore.YELLOW}Color Tests Without Alignment", align="center", back_separator=False)
    # pretty_print(f"{Fore.GREEN}I am supposed to be green", back_separator=False, front_separator=False)
    # pretty_print(f"{Fore.RED}I am supposed to be red", back_separator=False, front_separator=False)
    # pretty_print(f"And I am supposed to be {Fore.GREEN}green {Fore.RESET}+ {Fore.RED}red", back_separator=False)
    # pretty_print(f"{Fore.YELLOW}Color Tests With Alignment", align="center", back_separator=False)
    # pretty_print(f"{Fore.CYAN}[ THIS IS ALIGNED TO LEFT ]", align="left", back_separator=False, front_separator=False)
    # pretty_print(f"{Fore.MAGENTA}[ THIS IS ALIGNED TO RIGHT ]", align="right", back_separator=False, front_separator=False)
    # pretty_print(f"{Fore.GREEN}[ THIS IS ALIGNED TO THE CENTER ]", align="center", back_separator=False)

    # pretty_print(f"{Fore.YELLOW}[ TESTING ] {Fore.CYAN}This is some testing text!")
    # # separate_line()
    # pretty_print(f"{Fore.YELLOW}[ TESTING # 2 ] {Fore.CYAN}This is some testing text! This is some addition to the testing text!")
    # # separate_line()
    # pretty_print(f"{Fore.YELLOW}[ TESTING # 3 ] {Fore.CYAN}This is some testing text with an addition to the texting test with another addition to the testing text!")
    # # separate_line()
    # pretty_print(f"{Fore.YELLOW}[ TESTING # 4] {Fore.CYAN}This is some testing text with an addition to the texting test with another addition to the testing text! With MOAR TEXT, YEEEEEEEETT!!!!!")
    # separate_line()
    # #
    # final_test_string = f"{Fore.GREEN}[ FINAL TEST # 0 ]{Fore.CYAN}"
    # for i in range(100):
    #     final_test_string += f" {i}"
    #
    # pretty_print(final_test_string, back_separator=False)

    # separate_line()
    # separate_line()
    #
    # pretty_print(f"{Fore.YELLOW}[ COLOR TEST # 1 ]{Fore.CYAN}CYAN {Fore.RED}RED {Fore.GREEN}GREEN {Fore.BLUE}B{Fore.MAGENTA}L{Fore.RED}-{Fore.LIGHTGREEN_EX}W{Fore.WHITE}H{Fore.LIGHTYELLOW_EX}A{Fore.CYAN}T ------------------------------------------------------------------------------------------------------------------------------------------------")
    #
    # pretty_print(
    #     f"{Fore.YELLOW}[ COLOR TEST # 1 ]{Fore.CYAN}CYAN {Fore.RED}RED {Fore.GREEN}GREEN {Fore.BLUE}B{Fore.MAGENTA}L{Fore.RED}-{Fore.LIGHTGREEN_EX}W{Fore.WHITE}H{Fore.LIGHTYELLOW_EX}A{Fore.CYAN}T")
