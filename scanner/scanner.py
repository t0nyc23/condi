import time
import urllib3
import requests
from queue import Empty
from termcolor import colored
from urllib.parse import urljoin

import sys
sys.path.append("..")
from utils.general import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ScannerCondi:

	def __init__(self, arguments, wordsQueue):
		self.totalRequestsCount = 0
		self.totalUrlsFound     = 0
		self.scannerLoop        = True
		self.wordsQueue         = wordsQueue
		self.baseUrl            = arguments.url
		self.outputFile         = arguments.outfile
		self.headersList        = arguments.headers
		self.customUserAgent    = arguments.user_agent
		self.userProxy          = arguments.proxies_args
		self.sleepTime          = arguments.sleep / 1000
		self.positiveCodes      = arguments.positive_codes
		self.negativeCodes      = arguments.negative_codes
		self.negativeSizes      = arguments.negative_sizes
		self.positiveSizes      = arguments.positive_sizes
		self.followRedirects    = arguments.follow_redirect
		self.totalWords         = self.wordsQueue.qsize()

	def printProgress(self):
		while self.scannerLoop:
			prec = 100 * float(self.totalRequestsCount)/float(self.totalWords)
			prec_s = "%.1f" % prec
			prog = "[Words tested: {}/{}](Progress: {}%)".format(self.totalRequestsCount, self.totalWords, prec_s)
			print(prog,end = "\r")			

	def setCustomHeaders(self):
		self.customHeaders = {"User-Agent": self.customUserAgent}
		for header in self.headersList:
			key, value = header.split(":")
			self.customHeaders[key] = value.strip()

	def setUserProxy(self):
		if self.userProxy:
			self.customProxies = {"http":self.userProxy, "https":self.userProxy}
		else:
			self.customProxies = self.userProxy

	def printResults(self):
		self.totalUrlsFound += 1
		statusCodeColors = {"1":"magenta", "2":"green", "3":"blue", "4":"red", "5":"yellow"}
		selectedColor = statusCodeColors[self.responseStatusCode[0]]
		statusCodeStr = self.responseStatusCode
		responseLengthStr = self.responseSize
		currentUrlStr = self.currentUrl
		output = f"STATUS::{statusCodeStr} SIZE::{responseLengthStr} PATH::{currentUrlStr}"
		outputColored = f"{colored(statusCodeStr.ljust(11, ' '), selectedColor)}{responseLengthStr.ljust(11)}{currentUrlStr}"
		if statusCodeStr[0] == '3':
			location = urljoin(self.baseUrl, self.responseHeaders['Location'])
			output = output + f" LOCATION::{location}"
			outputColored = outputColored + colored(f" ({location})", selectedColor)
		if self.scannerLoop:
			print(outputColored)
		if self.outputFile: # Will probably change the save output format
			addToFile(self.outputFile, output)

	def filterResponseSize(self):
		if self.negativeSizes:
			if not self.responseSize in self.negativeSizes:
				self.printResults()
		elif self.positiveSizes:
			if self.responseSize in self.positiveSizes:
				self.printResults()
		else:
			self.printResults()		

	def doScanCondi(self):
		try:
			while self.scannerLoop:
				time.sleep(self.sleepTime)
				currentWord = self.wordsQueue.get(block=False)
				currentUrl = urljoin(self.baseUrl, currentWord)
				self.totalRequestsCount += 1
				response = requests.get(
					currentUrl,
					headers=self.customHeaders,
					allow_redirects=self.followRedirects,
					proxies=self.customProxies,
					verify=False)				
				self.responseStatusCode = str(response.status_code)
				self.responseSize = str(len(response.content))
				self.currentUrl = currentUrl
				self.responseHeaders = response.headers
				if self.positiveCodes:
					if self.responseStatusCode in self.positiveCodes:
						self.filterResponseSize()
				elif self.negativeCodes:
					if self.responseStatusCode not in self.negativeCodes:
						self.filterResponseSize()
				else:
					self.filterResponseSize()
		except Empty:
			self.scannerLoop = False
		except requests.exceptions.ProxyError:
			proxy_error = f"Cannot connect to proxy {self.userProxy}"
			print(colored(proxy_error, "red"))
		except requests.exceptions.ConnectionError as err:
			not_found_msg = f"Error with \"{currentUrl}\". Name or service not known."
			print(colored(not_found_msg, 'red'))
			print(colored(err, 'red'))
		except requests.exceptions.InvalidProxyURL:
			invalid_url_msg = f"Invalid proxy URL: \"{self.userProxy}\"."
			print(colored(invalid_url_msg, 'red'))
		except requests.exceptions.InvalidURL:
			invalid_url_msg = f"Invalid target URL: \"{currentUrl}\"."
			print(colored(invalid_url_msg, 'red'))
		except requests.exceptions.MissingSchema:
			invalid_url_msg = f"Invalid target URL: \"{currentUrl}\"."
			print(colored(invalid_url_msg, 'red'))
