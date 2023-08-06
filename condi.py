#!/usr/bin/python3

import os
import sys
import time
import json
import socket
import argparse

from queue import Queue
from threading import Thread, active_count

# External libraries
import requests
from termcolor import colored

title = f"{'-'*9} condi.py || version: 0.0 || by @non {'-'*9}"

banner = f"""
    \r{"="*len(title)}
    
    \r               either it's there or not                
    \r  the breath and the height, of an undiscovered first     
    
    \r{"="*len(title)}
    \r{title}
    \r{"="*len(title)}
"""

helpmsg = f"""\r{banner}
    \rUsage example: condi.py -u <target url> -w <wordlist path>

    \r  -h help         --->  Show this message
    \r  -u url          --->  Target URL to scan
    \r  -o output       --->  Output results to a file
    \r  -w wordlist     --->  Path of the wordlist to use
    \r  -t threads      --->  Number of threads. Default is 10
    \r  -x extensions   --->  Comma separated extensions to include
    \r  -r restore      --->  Restore session from ".condi.restore" in your home folder
    \r  -a user-agent   --->  Custom User-Agent string
"""

class Condi_files:
    def __init__(self):

        self.restore_file = "{}/.condi.restore".format(os.path.expanduser('~'))
        self.msg = f"Restoring session from: {colored(self.restore_file, attrs=['bold', 'underline'])}"

    def save_file(self, contents, filename):


        if filename == "condi.restore":
            save_msg = f"Saving session to file: {colored(self.restore_file, 'cyan')}"
            print(save_msg)
            with open(self.restore_file, 'w') as r:
                json.dump(contents, r, indent=2)
        else:
            try:
                with open(filename, 'w') as w:
                    for data in contents:
                        results = "{}\t\t(code: {} | size: {})\n".format(
                            data['url'],data['code'],data['size'])
                        w.write(results)
                    print(f"Saving scan results at: {colored(filename, 'cyan')}")
            except PermissionError:
                recover = f"{os.path.expanduser('~')}/condi_results.txt"
                msg = f"Could not write: {filename} (Permission denied). Saving at: {colored(recover, attrs=['bold', 'underline'])}"
                print(colored(msg, 'red'))
                with open(recover, 'w') as w:
                    for data in contents:
                        w.write(f"{data}\n")

    def open_file(self, givenfile):

        try:
            if givenfile == self.restore_file:
                
                with open(givenfile) as rgf:
                    opts = json.load(rgf)
                return opts
            else:
                with open(givenfile) as gf:
                    words = gf.readlines()
                return words

        except FileNotFoundError:
            print(colored(f'\nFile {givenfile} not found!\n', 'red', attrs=['bold']))
            sys.exit()

class Condi:

    def __init__(self, opts):

        self.count          = 0
        self.total_words    = 0
        self.total_found    = 0
        self.urls_found     = []
        self.threads        = []
        self.worker_loop    = True
        self.negative_codes = [404]
        
        self.qwords         = Queue()
        self.condi_files    = Condi_files()
        
        self.url            = opts['url']
        self.outfile        = opts['outfile']
        self.wordlist_file  = opts['wordlist']
        self.extensions     = opts['extensions']
        self.threads_num    = opts['threads_num']
        self.user_agent     = opts['user_agent']
        
        self.found_url_str  = "--- code: {} -> {} (size: {})"

        self.make_checks()
        self.create_wordlist()

        self.headers = {'User-Agent': self.user_agent}
        
        self.check_host()

    def make_checks(self):
        if 'last_used' in opts:
            self.count = int(opts['last_used'])

        if 'found' in opts:
            for i in opts['found']:
                self.urls_found.append(i)
            self.total_found = len(self.urls_found)

        if "http" not in self.url[:5]:
            self.url = f"http://{self.url}"
        
        if self.url[-1] != "/":
            self.url += "/"

        if self.user_agent == 'default':
            self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

    def check_host(self):
        # Check for errors in the target host
        try:
            r = requests.get(self.url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            not_found_msg = f"Error with \"{self.url}\". Name or service not known."
            print(colored(not_found_msg, 'red'))
            quit()
        except requests.exceptions.InvalidURL:
            invalid_url_msg = f"Invalid target URL: \"{self.url}\"."
            print(colored(invalid_url_msg, 'red'))
            quit()
        except requests.exceptions.MissingSchema:
            invalid_url_msg = f"Invalid target URL: \"{self.url}\"."
            print(colored(invalid_url_msg, 'red'))
            quit()

    def print_discovered(self, found):
        
        code_colors = {"1":"magenta", "2":"green", "3":"blue" ,"4":"red", "5":"yellow"}
        selected_color = code_colors[str(found['code'])[0]]
        word = "/{}".format(found['word'])
        found_message = "\r[+]  {}  ==>  (status: {} | size: {}) ==> {}{}".format(
            colored(word, selected_color),
            found['code'],
            found['size'],
            colored(found['url'], selected_color, attrs=['dark']),
            ' '*100
        )
        print(found_message, end=" ")
    
    def print_progress(self):
        while self.worker_loop:
            prec = 100 * float(self.count)/float(self.total_words)
            prec_s = "%.1f" % prec
            prog = "\r[Words tested: {}/{}](Progress: {})".format(self.count, self.total_words, prec_s)
            print(colored(prog, attrs=['dark']),end = "\r")

        print(f"\r{' '* 100}", end="\r")
        print(f"\nFinished. Found a total of {self.total_found} out of {self.total_words} urls")

    def create_wordlist(self):

        tmp_wordlist = self.wordlist_file
        wordlist = self.condi_files.open_file(tmp_wordlist)

        if len(self.extensions) > 1:
            self.extensions = self.extensions.replace(",", " .")
            self.extensions = self.extensions.split(" ")
            self.extensions[0] = f".{self.extensions[0]}"
            self.extensions.insert(0, "")

        for word in wordlist:
            for x in self.extensions:
                self.total_words += 1
                if self.total_words < self.count:
                    pass
                else:
                    word_ext = f"{word.strip()}{x}"
                    self.qwords.put(word_ext)

    def worker(self):

        while self.worker_loop:
            word = self.qwords.get_nowait()
            if self.qwords.empty():
                self.worker_loop = False
                continue
            else:
                url = "{}{}".format(self.url, word)
                req = requests.get(url, headers=self.headers, allow_redirects=False)
                self.count += 1
                if req.status_code not in self.negative_codes:
                    if self.found_url_str.format(req.status_code, url, len(req.content)) in self.urls_found:
                        continue
                    else:
                        self.total_found += 1
                        url_found_dict = {
                            "word":word,
                            "code":req.status_code,
                            "size":len(req.content),
                            "url":url
                        }

                        self.urls_found.append(url_found_dict)
                        if self.worker_loop:
                            self.print_discovered(url_found_dict)

    def run_scan(self):
        print(banner)

        # Print found urls from previous session
        if len(self.urls_found) > 0:
            msg = Condi_files().msg
            print(f"{colored(msg, 'cyan')}\n")
            for i in self.urls_found:
                self.print_discovered(i)
        try:
            for _ in range(self.threads_num):
                self.threads.append(Thread(target=self.worker))
    
            for thread in self.threads:
                thread.start()

            self.print_progress()

            for join_thread in self.threads:
                join_thread.join()

        except KeyboardInterrupt:
            print(f"\r{' '*100}")
            kbi = f"\rKeyboard Interrupt detected. Waiting for threads to terminate...{' '*100}"
            print(colored(kbi, 'red'))
            self.worker_loop = False
            opts['last_used'] = self.count
            opts['found'] = self.urls_found
            # Create a session restore file if the current session is "Keyboard Interrupted"
            self.condi_files.save_file(opts, "condi.restore")

        finally:
            if self.outfile:
                self.condi_files.save_file(self.urls_found, self.outfile)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', dest="url", type=str, help="Target url to scan")
    parser.add_argument('-w', dest="wordlist", type=str, help="Path of the wordlist to use")
    parser.add_argument('-h', '--help', action="store_true")
    parser.add_argument('-t', dest='threads_num', type=int, default=10)
    parser.add_argument('-x', dest='extensions', default=[""], type=str)
    parser.add_argument('-o', dest='outfile', type=str)
    parser.add_argument('-r', dest='restore', action="store_true")
    parser.add_argument('-a', dest='user_agent', default='default', type=str)
    args = parser.parse_args()

    if args.restore:
        # Restrore session
        restore_session = Condi_files()
        r_file = restore_session.restore_file
        opts = restore_session.open_file(r_file)
        condi = Condi(opts).run_scan()
    elif not args.url or not args.wordlist or args.help:
        print(helpmsg)
        sys.exit()
    else:
        # return a dictionary from parsed arguments
        opts = vars(args)
        condi = Condi(opts).run_scan()
