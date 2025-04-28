import ssl
import random
import socket
import time
import math
import re
import urllib.request
import urllib.error
import urllib.parse
from urllib.parse import urlparse
import whois

class Abductor:
    def __init__(self, ufonet, debug=True):
        self.ufonet = ufonet
        self.start = None
        self.stop = None
        self.port = None
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.wafs_file = "core/txt/wafs.txt"
        self.debug = debug

    def validate_url(self, target):
        if not target.startswith(('http://', 'https://')):
            raise ValueError(f"[Error] [AI] Invalid URL format: {target}")
        parsed = urlparse(target)
        if not parsed.netloc:
            raise ValueError(f"[Error] [AI] URL missing domain: {target}")
        return True

    def proxy_transport(self, proxy):
        proxy_url = self.ufonet.extract_proxy(proxy)
        proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

    def establish_connection(self, target):
        self.validate_url(target)
        self.ufonet.user_agent = random.choice(self.ufonet.agents).strip()
        headers = {'User-Agent': self.ufonet.user_agent, 'Referer': self.ufonet.referer}

        if self.debug:
            print(f"[DEBUG] Attempting connection to: {target}")
            print(f"[DEBUG] Using User-Agent: {self.ufonet.user_agent}")

        req = urllib.request.Request(target, headers=headers)

        try:
            if self.ufonet.options.proxy:
                if self.debug:
                    print(f"[DEBUG] Using Proxy: {self.ufonet.options.proxy}")
                self.proxy_transport(self.ufonet.options.proxy)

            self.start = time.time()
            response = urllib.request.urlopen(req, context=self.ctx)
            header = response.getheaders()
            content = response.read().decode('utf-8')
            self.stop = time.time()

            return content, header

        except Exception as e:
            print('[Error] [AI] Unable to connect -> [Exiting!]')
            if self.debug:
                print(f"[DEBUG] Reason: {repr(e)}")
            return None

    @staticmethod
    def convert_size(size):
        if size == 0:
            return '0B'
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return f'{s} {size_name[i]}'

    @staticmethod
    def convert_time(duration):
        return f'{duration:.2f}'

    @staticmethod
    def extract_banner(header):
        banner = via = "NOT found!"
        try:
            for h in header:
                if h[0] == "Server":
                    banner = h[1]
                if h[0] == "Via":
                    via = h[1]
        except Exception:
            pass
        return banner, via

    def extract_whois(self, domain):
        try:
            d = whois.query(domain, ignore_returncode=True)
            if d and d.creation_date:
                print(f" -Registrant   : {d.registrar}")
                print(f" -Creation date: {d.creation_date}")
                print(f" -Expiration   : {d.expiration_date}")
                print(f" -Last update  : {d.last_updated}")
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Whois lookup failed for {domain}: {repr(e)}")

    def extract_cve(self, banner):
        url = 'https://cve.mitre.org/cgi-bin/cvekey.cgi?'
        query_string = urllib.parse.urlencode({'keyword': str(banner)})
        target = url + query_string

        try:
            self.ufonet.user_agent = random.choice(self.ufonet.agents).strip()
            headers = {'User-Agent': self.ufonet.user_agent, 'Referer': self.ufonet.referer}
            req = urllib.request.Request(target, headers=headers)

            if self.ufonet.options.proxy:
                self.proxy_transport(self.ufonet.options.proxy)

            response = urllib.request.urlopen(req, context=self.ctx)
            content = response.read().decode('utf-8')

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] CVE search failed: {repr(e)}")
            return None

        if not content or "<b>0</b> CVE entries" in content:
            return "NOT found!"

        regex_s = '<td valign="top" nowrap="nowrap"><a href="(.+?)">'
        return re.findall(re.compile(regex_s), content)

    def waf_detection(self, banner, content):
        waf = "FIREWALL NOT PRESENT (or not discovered yet)! ;-)\n"

        try:
            with open(self.wafs_file) as f:
                wafs = f.readlines()
        except Exception as e:
            wafs = []
            if self.debug:
                print(f"[DEBUG] WAF detection file missing: {repr(e)}")

        sep = "##"
        for w in wafs:
            if sep in w:
                signature, vendor = w.strip().split(sep)
                if signature in content or signature in banner:
                    waf = f"VENDOR -> {vendor}"
                    break

        return waf

    def abducting(self, target):
        try:
            result = self.establish_connection(target)
            if result is None:
                print("[Error] [AI] Something wrong abducting... Not any data stream found!\n")
                return
            target_reply, header = result
        except Exception as e:
            print("[Error] [AI] Something wrong abducting... Not any data stream found!\n")
            if self.debug:
                print(f"[DEBUG] Abducting failure reason: {repr(e)}")
            return

        print(' -Target URL:', target, "\n")

        self.port = "80" if target.startswith("http://") else "443" if target.startswith("https://") else "Error!"

        try:
            domain = urlparse(target).netloc.replace("www.", "")
        except Exception:
            domain = "OFF"

        ipv4, ipv6 = "OFF", "OFF"

        try:
            ipv4 = socket.gethostbyname(domain)
        except Exception:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                r.nameservers = ['8.8.8.8', '8.8.4.4']
                a_records = r.resolve(domain, 'A')
                ipv4 = str(a_records[0])
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] IPv4 resolution failed: {repr(e)}")

        try:
            ipv6_info = socket.getaddrinfo(domain, int(self.port), socket.AF_INET6, socket.IPPROTO_TCP)
            ipv6 = ipv6_info[0][4][0]
        except Exception:
            pass

        print(' -IP    :', ipv4)
        print(' -IPv6  :', ipv6)
        print(' -Port  :', self.port)
        print(' \n -Domain:', domain)

        self.extract_whois(domain)

        try:
            size = self.convert_size(len(target_reply))
        except Exception:
            size = "Error!"

        try:
            load = self.convert_time(self.stop - self.start)
        except Exception:
            load = "Error!"

        try:
            banner, via = self.extract_banner(header)
        except Exception:
            banner, via = "NOT found!", "NOT found!"

        print('\n---------')
        print("\nTrying single visit broadband test (using GET)...\n")
        print(' -Bytes in :', size)
        print(' -Load time:', load, "seconds\n")
        print('---------')
        print("\nDetermining webserver fingerprint (note that this value can be a fake)...\n")
        print(' -Banner:', banner)
        print(' -Vía   :', via, "\n")
        print('---------')
        print("\nSearching for extra Anti-DDoS protections...\n")

        waf = self.waf_detection(banner, target_reply)
        print(' -WAF/IDS:', waf)

        if 'VENDOR' in waf:
            print(' -NOTICE : This FIREWALL probably is using Anti-(D)DoS measures!\n')

        print('---------')

        if banner != "NOT found!":
            print("\nSearching at CVE (https://cve.mitre.org) for vulnerabilities...\n")
            try:
                cve_entries = self.extract_cve(banner)
                if not cve_entries or cve_entries == "NOT found!":
                    print(' -Last Reports:', cve_entries or 'NOT found!')
                else:
                    print(' -Last Reports:')
                    for i, c in enumerate(cve_entries[:10], start=1):
                        cve_info = c.replace("/cgi-bin/cvename.cgi?name=", "")
                        print(f"\n        + {cve_info} -> https://cve.mitre.org{c}")
                print('\n---------')
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] CVE search block failure: {repr(e)}")

        print("\n[Info] [AI] Abduction finished! -> [OK!]\n")
