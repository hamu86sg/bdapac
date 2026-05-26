# APAC Regulatory Intelligence Monitor

Automated weekly memo and daily flash digest covering regulatory changes across
13 Asia Pacific markets that may affect IT requirements for government agencies
and enterprises.

## Schedule

| Report | When | Trigger |
|--------|------|---------|
| Weekly PDF Memo | Saturday 12:00 SGT | GitHub Actions cron |
| Daily Flash Digest | Daily 07:00 SGT (only when HIGH items found) | GitHub Actions cron |

## What it monitors

**Jurisdictions:** Australia, Japan, India, Singapore, South Korea, Hong Kong,
Taiwan, Malaysia, Vietnam, Thailand, Macau, New Zealand, Philippines

**Sources (~40):** Official government/regulator RSS feeds, Google News per
jurisdiction, Mondaq, Lexology, GovInsider Asia, IAPP, ZDNet

**IT categories:** Cybersecurity, data protection & privacy, cloud sovereignty,
AI/ML governance, telecom, critical infrastructure, hardware supply chain,
fintech, data centre regulation, semiconductor export controls

**Verticals:** Financial services, healthcare, government/public sector,
manufacturing, telco, energy, data centre ecosystem, retail

---

## One-time setup (do this once)

### Step 1 — GitHub account
Create a free account at https://github.com if you don't have one.

### Step 2 — Create the repository
1. Go to https://github.com/new
2. Name it `apac-reg-monitor`
3. Set to **Private**
4. Click **Create repository**

### Step 3 — Upload the code
Ask Claude Code to push the code to your new repository.
Provide Claude with your GitHub username when asked.

### Step 4 — Anthropic API key
1. Go to https://console.anthropic.com
2. Sign up and add a payment method (pay-per-use, ~$1–3/week)
3. Click **API Keys** → **Create Key** → name it `apac-monitor`
4. Copy the key (starts with `sk-ant-...`)

### Step 5 — Gmail app password
1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Search for **App passwords** → select **Other** → name it `apac-monitor`
4. Copy the 16-character password

### Step 6 — Add secrets to GitHub
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret name | Value |
|-------------|-------|
| `GROQ_API_KEY` | Your `gsk_...` key from console.groq.com |
| `RESEND_API_KEY` | Your `re_...` key from resend.com |
| `RECIPIENT_EMAIL` | `hamilton.lau@wwt.com` |

### Step 7 — Test run
1. Go to **Actions** tab in your GitHub repository
2. Click **Weekly APAC Regulatory Report**
3. Click **Run workflow** → **Run workflow**
4. Watch the logs — should complete in ~5 minutes
5. Check your inbox for the PDF

---

## Maintenance

Claude Code can update any part of this system — sources, prompts, PDF layout,
thresholds — by editing files in this repository. No other tools required.

To add a new source: edit `src/config.py` and add to `OFFICIAL_FEEDS` or
`GOOGLE_NEWS_QUERIES`.

To adjust the flash threshold: edit `DAILY_FLASH_MIN_HIGH_ITEMS` in `src/config.py`.
