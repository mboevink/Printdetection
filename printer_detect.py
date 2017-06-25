import re
import sys
import socket
import requests
import netifaces as ni
from ipaddress import ip_network
from contextlib import closing


def get_ip(ip4: str) -> ip_network:
    if ip4:
        return ip_network(ip4, False)
    for i in ni.interfaces()[::-1]:
        try:
            ip = ni.ifaddresses(i)[ni.AF_INET][0]
            return ip_network(f"{ip['addr']}/{ip['netmask']}", False)
        except:
            pass


def check_printer(host: str, port: int = 631) -> tuple:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.15)
        if sock.connect_ex((str(host), port)) == 0:
            print_page = requests.get(f'http://{host}')
            pc = print_page.status_code == 401 or re.search(r"fax|photocopier", print_page.text, re.IGNORECASE) is True
            return host, pc


def printer_detect(ip4: str) -> list:
    printers = []
    for ip in get_ip(ip4):
        print(f"Checking IP: {ip}", end='\r')
        _printer = check_printer(ip)
        if _printer:
            printers.append(_printer)
    return printers


if __name__ == '__main__':
    ipv4 = sys.argv[1] if len(sys.argv) > 1 else False
    found_printers = printer_detect(ipv4)
    for p in found_printers:
        print(f"Printer found on {p[0]}, photocopier: {p[1]}")
