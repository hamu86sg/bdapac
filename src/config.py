"""
Source definitions, search queries, and configuration for the APAC regulatory monitor.
"""

# ── Official RSS/Atom feeds ───────────────────────────────────────────────────
# Only feeds verified to return valid RSS. Most government agencies do not
# publish RSS; they are covered instead via targeted Google News queries below.
OFFICIAL_FEEDS = {
    "India": [
        {"name": "RBI Press Releases",   "url": "https://www.rbi.org.in/scripts/rss.aspx?Id=34"},
        {"name": "CERT-In Advisories",   "url": "https://www.cert-in.org.in/RSS/CERT-In-News.rss"},
    ],
    "New Zealand": [
        {"name": "CERT NZ Advisories",   "url": "https://www.cert.govt.nz/it-specialists/advisories/feed/"},
    ],
    "Philippines": [
        {"name": "NPC Philippines News", "url": "https://www.privacy.gov.ph/category/news/feed/"},
    ],
}

# ── Aggregator and analysis feeds ────────────────────────────────────────────
AGGREGATOR_FEEDS = [
    {"name": "GovInsider Asia",   "url": "https://govinsider.asia/feed"},
    {"name": "IAPP Asia Pacific", "url": "https://iapp.org/news/rss/?region=asia-pacific"},
    {"name": "The Register Security", "url": "https://www.theregister.com/security/headlines.atom"},
    {"name": "Mondaq Technology", "url": "https://www.mondaq.com/rss/rssFeed.asp?fp=39&indStry=21"},
]

# ── Google News RSS queries ───────────────────────────────────────────────────
# Primary collection mechanism — reliable, no API key, covers all jurisdictions.
# Also includes agency-specific queries to replace broken official RSS feeds.
GOOGLE_NEWS_QUERIES = [
    # ── Australia ──
    "Australia cybersecurity regulation IT law",
    "Australia data protection privacy legislation",
    "Australia critical infrastructure security law",
    "ACSC Australian Cyber Security Centre advisory regulation",
    "APRA ASIC OAIC technology regulation Australia",
    # ── Japan ──
    "Japan cybersecurity regulation data privacy law",
    "Japan Digital Agency technology regulation",
    "Japan FSA financial technology regulation",
    "Japan semiconductor export control IT",
    # ── Singapore ──
    "MAS Monetary Authority Singapore technology regulation fintech",
    "Singapore CSA cybersecurity regulation",
    "Singapore PDPC data protection Personal Data Protection Act",
    "Singapore IMDA digital regulation telecoms",
    "Singapore data centre regulation cloud",
    # ── India ──
    "India DPDP data protection technology regulation",
    "India CERT-In cybersecurity regulation IT",
    "India MeitY digital infrastructure regulation",
    "India RBI technology banking regulation",
    "India telecom regulation TRAI technology",
    # ── South Korea ──
    "South Korea cybersecurity regulation data protection KISA",
    "South Korea FSS financial technology regulation",
    "South Korea AI regulation semiconductor policy",
    "South Korea personal information protection act",
    # ── Hong Kong ──
    "Hong Kong HKMA technology regulation fintech",
    "Hong Kong cybersecurity regulation PCPD data protection",
    "Hong Kong SFC technology regulation",
    # ── Taiwan ──
    "Taiwan cybersecurity regulation data protection",
    "Taiwan semiconductor technology export control",
    "Taiwan NCC digital regulation telecoms",
    # ── Malaysia ──
    "Malaysia cybersecurity regulation data protection PDPA",
    "Malaysia MCMC digital regulation",
    "Malaysia BNM technology banking regulation",
    # ── Vietnam ──
    "Vietnam cybersecurity law data localization regulation",
    "Vietnam technology regulation IT requirement",
    # ── Thailand ──
    "Thailand PDPA data protection regulation",
    "Thailand cybersecurity regulation ETDA",
    # ── Philippines ──
    "Philippines data privacy NPC regulation technology",
    "Philippines BSP fintech regulation cybersecurity",
    "Philippines DICT digital technology regulation",
    # ── New Zealand ──
    "New Zealand cybersecurity CERT regulation privacy law",
    "New Zealand GCSB technology regulation",
    # ── Macau ──
    "Macau data protection technology regulation",
    # ── Cross-cutting APAC themes ──
    "Asia Pacific AI regulation artificial intelligence governance",
    "Asia Pacific data sovereignty cloud regulation",
    "Asia Pacific critical infrastructure cybersecurity regulation",
    "Asia Pacific data centre regulation hyperscaler",
    "Asia Pacific supply chain security technology hardware",
    "Asia Pacific digital currency CBDC regulation",
    "Asia Pacific fintech open banking regulation",
    "Asia Pacific cloud computing localization regulation",
    "Asia Pacific semiconductor export control",
    "Asia Pacific telecom 5G regulation",
]

# ── Relevance keywords ────────────────────────────────────────────────────────
RELEVANCE_KEYWORDS = [
    "regulation", "legislation", "law", "act", "bill", "directive", "circular",
    "guideline", "framework", "requirement", "standard", "compliance", "mandate",
    "enforcement", "amendment", "consultation", "draft", "proposal", "policy",
    "cybersecurity", "cyber security", "data protection", "data privacy",
    "cloud", "artificial intelligence", "AI", "machine learning", "data centre",
    "data center", "semiconductor", "hardware", "software", "network",
    "telecommunications", "telecom", "encryption", "cryptography",
    "critical infrastructure", "supply chain", "digital", "fintech",
    "open banking", "CBDC", "digital currency", "privacy",
    "government", "ministry", "authority", "agency", "regulator",
    "banned", "prohibited", "required", "mandatory", "approved", "enacted",
    "passed", "signed", "implemented", "proposed", "consulted", "rules",
]

# ── Jurisdictions tracked ─────────────────────────────────────────────────────
JURISDICTIONS = [
    "Australia", "Japan", "India", "Singapore", "South Korea",
    "Hong Kong", "Taiwan", "Malaysia", "Vietnam", "Thailand",
    "Macau", "New Zealand", "Philippines",
]

# ── IT categories ─────────────────────────────────────────────────────────────
IT_CATEGORIES = [
    "cybersecurity", "data_protection_privacy", "cloud_sovereignty",
    "ai_ml_governance", "telecommunications", "critical_infrastructure",
    "hardware_supply_chain", "fintech_digital_payments",
    "data_centre_regulation", "semiconductor_export_controls",
    "digital_identity", "network_equipment",
]

# ── Industry verticals ────────────────────────────────────────────────────────
VERTICALS = [
    "financial_services", "healthcare", "government_public_sector",
    "manufacturing_industrial", "telecommunications", "energy_utilities",
    "data_centre_ecosystem", "retail_ecommerce", "education",
]

# ── Thresholds ────────────────────────────────────────────────────────────────
DAILY_FLASH_MIN_HIGH_ITEMS = 1
DAILY_FLASH_MIN_ITEMS      = 5

# ── Schedules ────────────────────────────────────────────────────────────────
WEEKLY_CRON = "0 4 * * 6"    # Saturday 04:00 UTC = Saturday 12:00 SGT
DAILY_CRON  = "0 23 * * *"   # Daily    23:00 UTC = Daily    07:00 SGT

# ── Lookback windows ─────────────────────────────────────────────────────────
WEEKLY_LOOKBACK_DAYS  = 7
DAILY_LOOKBACK_HOURS  = 26

# ── Models ───────────────────────────────────────────────────────────────────
FILTER_MODEL   = "llama-3.3-70b-versatile"
ANALYSIS_MODEL = "llama-3.3-70b-versatile"
