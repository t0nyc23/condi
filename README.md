# Condi

A simple Content Discovery/Directory Brute-forcing tool written in python3. Nothing new or special about it.

### TO DO
- change banner to display details about scan
  - e.g. display threads wordlist filtered codes e.t.c.
  - add a quiet mode. meaning do not display the banner just the results
- use a restore file

### Install Requirements

```bash
sudo apt install python3-requests python3-termcolor
```

### Options
```
options:
  -h, --help            show this help message and exit

  -u URL                target url for content discovery (e.g. -u http://example.com)

  -w WORDLIST           wordlist to use for content discovery (e.g. -w wordlist.txt)

  -H [HEADERS ...]      headers to use (e.g. -H 'Header1: Value' 'Header2: value')

  -t THREADS_NUM        number of threads to use. default is 10 (e.g. -t 30)

  -x [EXTENSIONS ...]   extentsions to check in content discovery (e.g. -x php jsp)

  -o OUTFILE            save discovery results to a file (e.g. -o results.txt)

  -a USER_AGENT         use custom User-Agent string (e.g. -a "MyUA /0.1")

  -s SLEEP              milliseconds to wait before each request (e.g. -s 1000)

  -p PROXIES_ARGS       http proxy to use (e.g. -p 'http://127.0.0.1:8080')

  -fr                   Follow redirects. (Defaults to False)

  -pc [POSITIVE_CODES ...] positive response status codes to match (e.g. -pc 403 200).

  -nc [NEGATIVE_CODES ...] negative response status codes to filter (e.g. -pc 404 301)

  -ps [POSITIVE_SIZES ...] positive response size values to match (e.g. -ps 1234 3210)

  -ns [NEGATIVE_SIZES ...] negative response size values to filter (e.g. -ns 3210 332)
```