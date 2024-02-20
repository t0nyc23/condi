# Condi

A simple threaded Content Discovery/Directory Brute-forcing tool written in Python3.

### Install Requirements (Debian based disrtos)

```shell
sudo apt -y install python3-{requests,termcolor}
```

### Install and run Condi

```
git clone https://github.com/t0nyc23/condi
cd condi && chmod +x condi.py
./condy.py -u http://target.com -w yourwordlist.txt
```

### Condi usage examples
---
You can run `./condi.py --help` to se all available options.
1. Setting threads and sleep time
```
./condi.py -u http://target.com -w wordlist.txt -t 20 -s 1000
```
2. Custom headers and user-agent
```
./condi.py -u http://target.com -w wordlist.txt -H "Custom-Header: CustomValue"
./condi.py -u http://target.com -w wordlist.txt -a "MyCustomUserAgent/1.0"
```

3. Check for extensions, follow redirects and save to file
```
./condi.py -u http://target.com -w wordlist.txt -x php jsp -fr -o condi-results.txt
```
4. Filter negative status codes and use proxy requests
```
./condi.py -u http://target.com -w wordlist.txt -nc 404 403 401 -p http://127.0.0.1:8080
```


### TO DO
- add docker support
- add resume functionality using a restore file
