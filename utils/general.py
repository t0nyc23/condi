import os
from datetime import datetime
from termcolor import colored

DEFAULT_USER_AGENT = 'Mozilla/5.0'
#title = f"{'-'*9} Condi || version: 1.0.0 || by @t0nyc {'-'*9}"

banner=f"""
  ██████╗  ██████╗  ███╗   ██╗ ██████╗  ██╗           
 ██╔════╝ ██╔═══██╗ ████╗  ██║ ██╔══██╗ ██║           
 ██║      ██║   ██║ ██╔██╗ ██║ ██║  ██║ ██║           
 ██║      ██║   ██║ ██║╚██╗██║ ██║  ██║ ██║  v1.0.0   
 ╚██████╗ ╚██████╔╝ ██║ ╚████║ ██████╔╝ ██║  by @t0nyc
  ╚═════╝  ╚═════╝  ╚═╝  ╚═══╝ ╚═════╝  ╚═╝           """

def printScanDetails(arguments):
    details = "="*55
    details += f"\n[{colored('+', 'cyan')}] " + "Target Url:".ljust(23) + arguments.url
    details += f"\n[{colored('+', 'cyan')}] " + "Wordlist File:".ljust(23) + arguments.wordlist
    details += f"\n[{colored('+', 'cyan')}] " + "Threads Number:".ljust(23) + str(arguments.threads_num)
    details += f"\n[{colored('+', 'cyan')}] " + "User-Agent:".ljust(23) + arguments.user_agent
    if arguments.headers:
        for header in arguments.headers:
            details += f"\n[{colored('+', 'cyan')}] " + "Custom Header:".ljust(23) + header
    if arguments.extensions:
        details += f"\n[{colored('+', 'cyan')}] " + "Extensions:".ljust(23) + " ".join(arguments.extensions)
    if arguments.outfile:
        details += f"\n[{colored('+', 'cyan')}] " + "Output File:".ljust(23) + arguments.outfile
    if arguments.sleep:
        details += f"\n[{colored('+', 'cyan')}] " + "Sleep Time:".ljust(23) + str(arguments.sleep) + "ms"
    if arguments.proxies_args:
        details += f"\n[{colored('+', 'cyan')}] " + "Proxy Url:".ljust(23) + arguments.proxies_args
    if arguments.follow_redirect:
        details += f"\n[{colored('+', 'cyan')}] " + "Follow Redirects:".ljust(23) + str(arguments.follow_redirect)
    if arguments.positive_codes:
        details += f"\n[{colored('+', 'cyan')}] " + "Positive Status:".ljust(23) + " ".join(arguments.positive_codes)
    if arguments.positive_sizes:
        details += f"\n[{colored('+', 'cyan')}] " + "Positive Sizes:".ljust(23) + " ".join(arguments.positive_sizes)
    if arguments.negative_codes:
        details += f"\n[{colored('+', 'cyan')}] " + "Negative Status:".ljust(23) + " ".join(arguments.negative_codes)
    if arguments.negative_sizes:
        details += f"\n[{colored('+', 'cyan')}] " + "Negative Sizes:".ljust(23) + " ".join(arguments.negative_sizes)
    details += "\n" + "="*55
    if not arguments.quiet:
        print(details)

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
