#!/usr/bin/env python3

import os
import time
import requests
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")

TARGETS_FILE = "targets.txt"
RESULTS_DIR = "results"

# ─────────────── Sources (APIs) ───────────────

def fetch_crtsh(domain):
    try:
        r = requests.get(f"https://crt.sh/?q={domain}&output=json", timeout=30)
        if r.status_code != 200:
            return set()

        subs = set()
        for i in r.json():
            for s in i.get("name_value", "").split("\n"):
                s = s.strip().lower().lstrip("*.")
                if s.endswith(domain):
                    subs.add(s)
        return subs
    except:
        return set()


def fetch_hackertarget(domain):
    try:
        r = requests.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=20)
        if r.status_code != 200:
            return set()

        return {line.split(",")[0].strip() for line in r.text.splitlines() if domain in line}
    except:
        return set()


# ─────────────── Tools (CLI) ───────────────

def run_tools(domain):
    subs = set()

    try:
        subprocess.run(f"subfinder -d {domain} -silent -o sub1.txt", shell=True)
        subprocess.run(f"assetfinder --subs-only {domain} > sub2.txt", shell=True)
        subprocess.run(f"findomain -t {domain} -u sub3.txt", shell=True)
        subprocess.run(f"chaos -d {domain} -o sub4.txt", shell=True)
        subprocess.run(f"python3 dnscan/dnscan.py -d {domain} -w dnscan/subdomains-1000.txt -t 100 > sub5.txt", shell=True)

        for f in ["sub1.txt", "sub2.txt", "sub3.txt", "sub4.txt", "sub5.txt"]:
            if Path(f).exists():
                for line in open(f):
                    s = line.strip().lower()
                    if domain in s:
                        subs.add(s)

    except Exception as e:
        print("tools error:", e)

    return subs


# ─────────────── Storage ───────────────

def load_old(domain):
    f = Path(RESULTS_DIR) / f"{domain.replace('.', '_')}.txt"
    if not f.exists():
        return set()
    return set(f.read_text().splitlines())


def save(domain, subs):
    Path(RESULTS_DIR).mkdir(exist_ok=True)
    f = Path(RESULTS_DIR) / f"{domain.replace('.', '_')}.txt"
    f.write_text("\n".join(sorted(subs)))


# ─────────────── Discord ───────────────

def send_discord(domain, new):
    if not DISCORD_WEBHOOK or not new:
        return

    msg = "\n".join(f"• {x}" for x in list(new)[:20])

    requests.post(DISCORD_WEBHOOK, json={
        "content": f"🔥 New Subdomains for {domain}:\n{msg}"
    })


# ─────────────── Main ───────────────

def run(domain):
    old = load_old(domain)

    api_subs = fetch_crtsh(domain) | fetch_hackertarget(domain)
    tool_subs = run_tools(domain)

    all_subs = api_subs | tool_subs
    new = all_subs - old

    if new:
        print("[+] New:", len(new))
        send_discord(domain, new)
    else:
        print("[-] No new subdomains")

    save(domain, all_subs)


if __name__ == "__main__":
    domain = os.getenv("DOMAIN", "")

    if not domain:
        print("No DOMAIN set")
        exit(1)

    run(domain)
