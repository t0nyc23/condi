import os
from datetime import datetime
from termcolor import colored

DEFAULT_USER_AGENT = 'Mozilla/5.0'

title = f"{'-'*9} Condi || version: 1.0.0 || by @t0nyc {'-'*9}"

banner = f"""\r{"="*len(title)}
    \r{title}
    \r{"="*len(title)}"""

def openFile(givenfile):
    if os.path.exists(givenfile):
        with open(givenfile) as file:
            return file.readlines()

def createFile(filename):
    if not os.path.isfile(filename):
        print(f"[{colored('+', 'green')}] Saving results to {filename}")
        with open(filename, "w") as _:
            pass
    else:
        timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        new_name = f"{timestamp}_{filename}"
        print(f"[{colored('!', 'yellow')}] already exists, creating backup {new_name}")
        os.rename(filename, new_name)

def addToFile(filename, contents):
    with open(filename, "a") as file:
        file.write(f"{contents}\n")
