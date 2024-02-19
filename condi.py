#!/usr/bin/python3
import time
import argparse
import requests
from queue import Queue
from threading import Thread
from utils.general import *
from scanner.scanner import ScannerCondi

class Tool:
    def __init__(self, arguments):
        self.totalWords    = 0
        self.threadsList   = []
        self.progressLoop  = True
        self.wordsQueue    = Queue()
        self.arguments     = arguments
        self.outputFile    = arguments.outfile
        self.wordlistFile  = arguments.wordlist
        self.extensions    = arguments.extensions
        self.threadsNumber = arguments.threads_num

    def createWordlist(self):
        wordlistList = openFile(self.wordlistFile)
        for word in wordlistList:
            word = word.strip()
            self.wordsQueue.put(word)
            self.totalWords += 1
            if self.extensions:
                for extension in self.extensions:
                    extendedWord = f"{word}.{extension.strip()}"
                    self.wordsQueue.put(extendedWord)
                    self.totalWords += 1

    def doCheckRequest(self):
        # make first request to check all is ok
        _ = requests.get(
                self.arguments.url,
                headers=self.condiClass.customHeaders,
                allow_redirects=self.condiClass.followRedirects,
                proxies=self.condiClass.customProxies,
                verify=False)

    def run(self):
        self.createWordlist()
        self.condiClass = ScannerCondi(self.arguments, self.wordsQueue)
        self.condiClass.setCustomHeaders()
        self.condiClass.setUserProxy()
        if self.outputFile:
            createFile(self.outputFile)
        try:
            self.doCheckRequest()
            for _ in range(self.threadsNumber):
                self.threadsList.append(Thread(target=self.condiClass.doScanCondi))
            for thread in self.threadsList:
                thread.start()
            self.condiClass.printProgress()
            for joinThread in self.threadsList:
                joinThread.join()
            print(" " * len(self.condiClass.prog))
            print(f"Finished. Found a total of {self.condiClass.totalUrlsFound} out of {self.totalWords} urls")
        except KeyboardInterrupt:
            print(colored("Got Keyboard Interrupt. Bye...".ljust(90, " "), 'red'))
            self.progressLoop = False
            self.condiClass.scannerLoop = False
            time.sleep(1.5)
        except requests.exceptions.ProxyError:
            proxy_error = f"Cannot connect to proxy {self.condiClass.userProxy}"
            print(colored(proxy_error, "red"))
        except requests.exceptions.ConnectionError as err:
            not_found_msg = f"Error with \"{self.arguments.url}\". Name or service not known."
            print(colored(not_found_msg, 'red'))
            print(colored(err, 'red'))
        except requests.exceptions.InvalidProxyURL:
            invalid_url_msg = f"Invalid proxy URL: \"{self.condiClass.userProxy}\"."
            print(colored(invalid_url_msg, 'red'))
        except requests.exceptions.InvalidURL:
            invalid_url_msg = f"Invalid target URL: \"{self.arguments.url}\"."
            print(colored(invalid_url_msg, 'red'))
        except requests.exceptions.MissingSchema:
            invalid_url_msg = f"Invalid target URL: \"{self.arguments.url}\"."
            print(colored(invalid_url_msg, 'red'))


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(usage="./condi.py -u <target> -w <wordlist> (options)")
    parser.add_argument('-u', dest="url", type=str, 
        help="target url for content discovery (e.g. -u http://example.com)")
    parser.add_argument('-w', dest="wordlist", type=str, 
        help="wordlist to use for content discovery (e.g. -w wordlist.txt)")
    parser.add_argument('-H', dest="headers", default=[], nargs="*", 
        help="headers to use (e.g. -H 'Header1: Value' 'Header2: value')")
    parser.add_argument('-t', dest='threads_num', type=int, default=10, 
        help="number of threads to use. default is 10 (e.g. -t 30)")
    parser.add_argument('-x', dest='extensions', nargs="*", 
        help="extentsions to check in content discovery (e.g. -x php jsp)")
    parser.add_argument('-o', dest='outfile', type=str, 
        help='save discovery results to a file (e.g. -o results.txt)')
    parser.add_argument('-a', dest='user_agent', default=DEFAULT_USER_AGENT, type=str, 
        help="use custom User-Agent string (e.g. -a \"MyUA /0.1\")")
    parser.add_argument('-s', dest="sleep", type=int, default=0, 
        help="milliseconds to wait before each request (e.g. -s 1000)")
    parser.add_argument('-p', dest="proxies_args", default=None,
        help="http proxy to use (e.g. -p 'http://127.0.0.1:8080')")
    parser.add_argument('-fr', dest="follow_redirect", action="store_true", 
        help="Follow redirects. (Defaults to False)")
    parser.add_argument('-pc', dest="positive_codes", nargs="*", 
        help="positive response status codes to match (e.g. -pc 403 200).")
    parser.add_argument('-nc', dest="negative_codes", nargs="*", default=["404"], 
        help="negative response status codes to filter (e.g. -pc 404 301)")
    parser.add_argument('-ps', dest="positive_sizes", nargs="*", 
        help="positive response size values to match (e.g. -ps 1234 3210)")
    parser.add_argument('-ns', dest="negative_sizes", nargs="*", 
        help="negative response size values to filter (e.g. -ns 3210 332)")
    parser.add_argument("-q", dest="quiet", action="store_true",
        help="quiet mode, don't display banner")
    arguments = parser.parse_args()

    if not arguments.quiet:
        print(banner)

    if not arguments.url or not arguments.wordlist:
        print()
        parser.print_help()
    else:
        print("_" * 55)
        tool = Tool(arguments)
        tool.run()