# 🔍 Subdomain Monitor

Monitor new subdomains automatically using GitHub Actions and get notified on Discord.

## How it works

1. Runs on a schedule (every 6 hours by default)
2. Enumerates subdomains from 4 sources: `crt.sh`, `hackertarget`, `alienvault`, `anubis`
3. Compares results against the last known list (stored in `results/`)
4. Sends **only new subdomains** to Discord
5. Commits the updated results back to the repo

---

## Setup (5 minutes)

### 1. Fork or clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/subdomain-monitor
cd subdomain-monitor
```

### 2. Add your targets

Edit `targets.txt` and add your domains (one per line):

```
example.com
tesla.com
```

### 3. Add your Discord Webhook

In your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | Value |
|------|-------|
| `DISCORD_WEBHOOK` | `https://discord.com/api/webhooks/...` |

> **How to get a Discord Webhook URL:**
> Discord Server Settings → Integrations → Webhooks → New Webhook → Copy URL

### 4. Enable Actions

Go to the **Actions** tab in your repo and enable workflows if prompted.

### 5. Test it manually

Go to **Actions** → **Subdomain Monitor** → **Run workflow**

---

## Change the schedule

Edit `.github/workflows/monitor.yml` and update the cron line:

```yaml
- cron: '0 */6 * * *'   # every 6 hours  ← default
- cron: '0 * * * *'     # every hour
- cron: '0 */12 * * *'  # every 12 hours
- cron: '0 8 * * *'     # every day at 8am UTC
```

---

## Discord Notification Example

When new subdomains are found, you'll get a message like:

> **🆕 New Subdomains Found — example.com**
> • `api.example.com`
> • `staging.example.com`
> • `dev.example.com`

When nothing is found:

> **✅ Scan Complete — No New Subdomains**

---

## Sources used

| Source | Type |
|--------|------|
| [crt.sh](https://crt.sh) | Certificate Transparency |
| [HackerTarget](https://hackertarget.com) | DNS lookup |
| [AlienVault OTX](https://otx.alienvault.com) | Passive DNS |
| [Anubis](https://jldc.me) | Passive DNS |

---

## File structure

```
subdomain-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml     ← GitHub Actions schedule
├── results/                ← known subdomains (auto-updated)
│   └── example_com.txt
├── monitor.py              ← main script
├── targets.txt             ← your domains
├── requirements.txt
└── README.md
```

---

> ⚠️ Use responsibly. Only monitor domains you own or have permission to scan.
