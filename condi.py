#!/usr/bin/python3

import os
import sys
import time
import json
import requests
import argparse

from queue import Queue
from termcolor import colored
from threading import Thread, active_count

title = f"{'-'*9} condi.py || version: 0.0 || by @h0pper {'-'*9}"

banner = f"""
    \r{"="*len(title)}
    
    \r               either it's there or not                
    \r  the breadth and the height, of an undiscovered first     
    
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
                        w.write(f"{data}\n")
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
        
        self.found_url_str  = "--- code: {} -> {} (size: {})"

        self.make_checks()
        self.create_wordlist()
    

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

    def print_discovered(self, code, url, urlsize):
        ccolors = {"1":"magenta", "2":"green", "3":"blue" ,"4":"red", "5":"yellow"}
        color = ccolors[str(code)[0]]
        c = f"code: {colored(code, color)}"
        print(f"\r[{colored('*', 'cyan')}] {c} ==> {colored(url, color)} => (size:{urlsize}){' '*100}", end=" ")
    
    def print_progress(self):
        while self.worker_loop:
            prec = 100 * float(self.count)/float(self.total_words)
            prec_s = "%.1f" % prec
            print(f"\r{colored(f'[Words tested: {self.count}/{self.total_words}](Progress: {prec_s}%)', attrs=['dark'])}", end="\r")
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
                req = requests.get(url, allow_redirects=False)
                self.count += 1
                if req.status_code not in self.negative_codes:
                    self.total_found += 1
                    self.urls_found.append(self.found_url_str.format(req.status_code, url, len(req.content)))
                    if self.worker_loop:
                        self.print_discovered(req.status_code, url, len(req.content))

    def run_scan(self):
        print(banner)
        if len(self.urls_found) > 0:
            msg = Condi_files().msg
            print(f"{colored(msg, 'cyan')}\n")
            for i in self.urls_found:
                tmp = i.split(" ")
                self.print_discovered(tmp[2], tmp[4], tmp[6][:-1])
        try:
            for _ in range(self.threads_num):
                self.threads.append(Thread(target=self.worker))
    
            for thread in self.threads:
                thread.start()
            
            #progress_thread = Thread(target=self.print_progress)
            #progress_thread.start()
            #progress_thread.join()
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
    args = parser.parse_args()

    if args.restore:
        restore_session = Condi_files()
        r_file = restore_session.restore_file
        opts = restore_session.open_file(r_file)
        condi = Condi(opts).run_scan()
    elif not args.url or not args.wordlist or args.help:
        print(helpmsg)
        sys.exit()
    else:
        opts = vars(args)
        condi = Condi(opts).run_scan()