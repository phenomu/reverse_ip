import requests
import socket
import sys
import re
import threading

class ReturnableThread(threading.Thread):
    def __init__(self, target, args):
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
        self.result = None

    def run(self):
        self.result = self.target(*self.args)


argv = sys.argv

def helpUsage() -> None:
    print("[+] Usage\t: python3 exploit.py https://website.com\n[+] Example2\t: python3 exploit.py target_list.txt\n[?] info \t: [-r reverse] [-o file to write output to]")
    quit()

def verifyArgs(argv) -> None:
    if len(argv) <= 1:
        helpUsage()

def openfile(file_: list) -> list:
    file = open(file_,'r').readlines()
    th = [ReturnableThread(target=domain_to_ip, args=(parseurl(x.strip()), )) for x in file]
    print(f"Total Site {len(th)}")
    results = []
    for t in th:
        t.start()

    for t in th:
        t.join()
        if t.result.startswith("[+] "):
            results.append(t.result)
    results = list(set(results))
    print(f"{len(results)} Converted to IP, {len(th)-len(results)} Sites fail")

    return results

def revip(ip: str, arg: list) -> str:
    ip = ip.split("[+] ")[1]
    try:
        save = arg[arg.index("-o")+1]
    except Exception as er:
        save = None
    url = f"https://rapiddns.io/sameip/{ip}?full=1#result"
    head: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
    if '-r' in arg:
        req = requests.get(url, headers=head, timeout=15).content.decode('utf-8')
        regx: list = re.findall("</th>\n<td>(.*?)</td>",req)
        if save != None:
            for res in regx:
                open(save,'a').write(f"{res}\n")
            print(f"[+] {ip} -> {len(regx)} Sites")
        else:
            for res in regx:
                print(res)
    else:
        print(ip)

def domain_to_ip(domain: str) -> str:
    try:
        ip: str = socket.gethostbyname(domain)
        if ip == '0.0.0.0' or ip == '202.3.218.138':
            return f"[-] {domain}"
        else:
            return f"[+] {ip}"

    except Exception as er:
        return f"[-] {domain} {er}"

def parseurl(string: str) -> str:
    if string.startswith("http"):
        get_site = re.findall("//(.*)",string)[0]
        if "/" in get_site:
            get_site = get_site.split('/')[0]
            return get_site
        else:
            return get_site
    return string
    
verifyArgs(argv)
user_input: str = argv[1]

def main():

    try:
        listip: list = openfile(user_input)
        for ips in listip:
            try:
                if ips.startswith("[+] "):
                    revip(ips,sys.argv)
                else:
                    print(ips)
            except Exception as er:
                print(er)

    except Exception:
        ip: str = domain_to_ip(parseurl(user_input))
        try:
            if ip.startswith("[+] "):
                revip(ip,sys.argv)
            else:
                print(ip)
        except Exception as er:
            print(er)
    
if __name__ == '__main__':
    main()