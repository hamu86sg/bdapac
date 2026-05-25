"""
Source definitions, search queries, and configuration for the APAC regulatory monitor.
"""

# ── Official RSS/Atom feeds from regulatory bodies ─────────────────────────
OFFICIAL_FEEDS = {
    "Australia": [
        {"name": "ACSC Advisories", "url": "https://www.cyber.gov.au/sites/default/files/news-and-events/rss.xml"},
        {"name": "OAIC News", "url": "https://www.oaic.gov.au/news-and-events/news/feed"},
        {"name": "APRA News", "url": "https://www.apra.gov.au/news-and-publications/apra-news/rss"},
        {"name": "ASIC News", "url": "https://asic.gov.au/news-centre/rss-feeds/"},
    ],
    "Singapore": [
        {"name": "MAS News", "url": "https://www.mas.gov.sg/news/rss"},
        {"name": "CSA News", "url": "https://www.csa.gov.sg/News-Events/News-Articles/feed"},
        {"name": "PDPC News", "url": "https://www.pdpc.gov.sg/news-and-events/news-articles/rss"},
        {"name": "IMDA News", "url": "https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/rss"},
    ],
    "Hong Kong": [
        {"name": "HKMA News", "url": "https://www.hkma.gov.hk/eng/news-and-media/press-releases/rss/"},
        {"name": "PCPD News", "url": "https://www.pcpd.org.hk/english/news/news.html"},
        {"name": "SFC News", "url": "https://www.sfc.hk/en/News-and-announcements/Press-releases"},
    ],
    "New Zealand": [
        {"name": "CERT NZ Advisories", "url": "https://www.cert.govt.nz/it-specialists/advisories/feed/"},
        {"name": "GCSB News", "url": "https://www.gcsb.govt.nz/news/"},
        {"name": "NZ Privacy Commissioner", "url": "https://www.privacy.org.nz/news-and-publications/news-media/rss/"},
    ],
    "Malaysia": [
        {"name": "BNM Press Releases", "url": "https://www.bnm.gov.my/press-releases?type=rss"},
        {"name": "MCMC News", "url": "https://www.mcmc.gov.my/en/media/press-clippings/rss"},
    ],
    "India": [
        {"name": "CERT-In Advisories", "url": "https://www.cert-in.org.in/RSS/CERT-In-News.rss"},
        {"name": "RBI Press Releases", "url": "https://www.rbi.org.in/scripts/rss.aspx?Id=34"},
        {"name": "SEBI Press Releases", "url": "https://www.sebi.gov.in/sebi_data/rss/rss_press_release.xml"},
    ],
    "South Korea": [
        {"name": "KISA News (English)", "url": "https://www.kisa.or.kr/eng/news/news_View.jsp"},
        {"name": "FSS Press Releases", "url": "https://www.fss.or.kr/eng/bbs/B0000021/list.do?menuNo=500014"},
    ],
    "Japan": [
        {"name": "FSA Japan (English)", "url": "https://www.fsa.go.jp/en/news/"},
        {"name": "NISC News", "url": "https://www.nisc.go.jp/eng/"},
    ],
    "Philippines": [
        {"name": "NPC Philippines", "url": "https://www.privacy.gov.ph/category/news/feed/"},
        {"name": "BSP Circular", "url": "https://www.bsp.gov.ph/SitePages/MediaAndResearch/MediaReleases.aspx"},
    ],
}

# ── Google News RSS queries (free, no API key, covers hard-to-scrape markets) ──
# Format: https://news.google.com/rss/search?q={query}&hl=en&gl=SG&ceid=SG:en
GOOGLE_NEWS_QUERIES = [
    # Australia
    "Australia cybersecurity regulation IT law",
    "Australia data protection privacy legislation",
    "Australia critical infrastructure security",
    # Japan
    "Japan cybersecurity regulation data privacy law",
    "Japan digital agency regulation technology",
    "Japan semiconductor export control IT",
    # Singapore
    "Singapore MAS technology regulation fintech",
    "Singapore cybersecurity Personal Data Protection Act",
    "Singapore data centre regulation cloud",
    # India
    "India data protection technology regulation DPDP",
    "India CERT cybersecurity regulation IT",
    "India digital infrastructure cloud regulation",
    # South Korea
    "South Korea cybersecurity regulation data protection",
    "South Korea KISA technology regulation",
    "South Korea AI regulation semiconductor",
    # Hong Kong
    "Hong Kong cybersecurity regulation technology law",
    "Hong Kong HKMA technology fintech regulation",
    "Hong Kong data protection PDPO",
    # Taiwan
    "Taiwan cybersecurity regulation data protection",
    "Taiwan semiconductor technology export control",
    "Taiwan digital economy regulation",
    # Malaysia
    "Malaysia cybersecurity regulation data protection",
    "Malaysia MCMC technology regulation",
    "Malaysia digital economy regulation",
    # Vietnam
    "Vietnam cybersecurity law regulation data localization",
    "Vietnam technology regulation IT requirement",
    # Thailand
    "Thailand PDPA data protection regulation technology",
    "Thailand cybersecurity regulation IT",
    # Philippines
    "Philippines data privacy regulation technology",
    "Philippines BSP fintech regulation cybersecurity",
    # New Zealand
    "New Zealand cybersecurity regulation privacy law",
    "New Zealand technology regulation IT",
    # Macau
    "Macau technology regulation data protection IT",
    # Cross-cutting APAC
    "Asia Pacific AI regulation artificial intelligence governance",
    "Asia Pacific data sovereignty cloud regulation",
    "Asia Pacific critical infrastructure cybersecurity regulation",
    "Asia Pacific data centre regulation hyperscaler",
    "Asia Pacific supply chain security technology regulation",
    "Asia Pacific digital currency CBDC regulation",
    "Asia Pacific fintech open banking regulation",
    "Asia Pacific cloud computing localization regulation",
]

# ── Aggregator and analysis sources ─────────────────────────────────────────
AGGREGATOR_FEEDS = [
    {"name": "Mondaq Technology (APAC)", "url": "https://www.mondaq.com/rss/rssFeed.asp?fp=39&indStry=21"},
    {"name": "Lexology Technology", "url": "https://www.lexology.com/rss/topic/technology"},
    {"name": "Lexology Privacy & Data", "url": "https://www.lexology.com/rss/topic/data-protection-and-privacy"},
    {"name": "GovInsider Asia", "url": "https://govinsider.asia/feed"},
    {"name": "IAPP Asia Pacific", "url": "https://iapp.org/news/rss/?region=asia-pacific"},
    {"name": "ZDNet Asia", "url": "https://www.zdnet.com/topic/asia/rss.xml"},
    {"name": "The Register Security", "url": "https://www.theregister.com/security/headlines.atom"},
]

# ── Relevance keywords (used for fast pre-filter before Claude call) ─────────
RELEVANCE_KEYWORDS = [
    # Regulatory actions
    "regulation", "legislation", "law", "act", "bill", "directive", "circular",
    "guideline", "framework", "requirement", "standard", "compliance", "mandate",
    "enforcement", "amendment", "consultation", "draft", "proposal",
    # IT domains
    "cybersecurity", "cyber security", "data protection", "data privacy",
    "cloud", "artificial intelligence", "AI", "machine learning", "data centre",
    "data center", "semiconductor", "hardware", "software", "network",
    "telecommunications", "telecom", "encryption", "cryptography",
    "critical infrastructure", "supply chain", "digital", "fintech",
    "open banking", "CBDC", "digital currency",
    # Government/agency
    "government", "ministry", "authority", "agency", "regulator",
    # Actions
    "banned", "prohibited", "required", "mandatory", "approved", "enacted",
    "passed", "signed", "implemented", "proposed", "consulted",
]

# ── Jurisdictions tracked ────────────────────────────────────────────────────
JURISDICTIONS = [
    "Australia", "Japan", "India", "Singapore", "South Korea",
    "Hong Kong", "Taiwan", "Malaysia", "Vietnam", "Thailand",
    "Macau", "New Zealand", "Philippines",
]

# ── IT categories for classification ────────────────────────────────────────
IT_CATEGORIES = [
    "cybersecurity", "data_protection_privacy", "cloud_sovereignty",
    "ai_ml_governance", "telecommunications", "critical_infrastructure",
    "hardware_supply_chain", "fintech_digital_payments",
    "data_centre_regulation", "semiconductor_export_controls",
    "digital_identity", "network_equipment",
]

# ── Industry verticals for classification ───────────────────────────────────
VERTICALS = [
    "financial_services", "healthcare", "government_public_sector",
    "manufacturing_industrial", "telecommunications", "energy_utilities",
    "data_centre_ecosystem", "retail_ecommerce", "education",
]

# ── Significance thresholds ─────────────────────────────────────────────────
DAILY_FLASH_MIN_HIGH_ITEMS = 1   # Send flash if this many HIGH items found today
DAILY_FLASH_MIN_ITEMS = 5        # Or if this many total relevant items found today

# ── Schedule reference ───────────────────────────────────────────────────────
# Weekly: Saturday 04:00 UTC  = Saturday 12:00 SGT (UTC+8)
# Daily:  Daily   23:00 UTC   = Daily    07:00 SGT (UTC+8)
WEEKLY_CRON = "0 4 * * 6"
DAILY_CRON  = "0 23 * * *"

# ── Article age limits ───────────────────────────────────────────────────────
WEEKLY_LOOKBACK_DAYS = 7
DAILY_LOOKBACK_HOURS = 26    # slightly over 24h to avoid gaps between runs

# ── Claude model selection ───────────────────────────────────────────────────
FILTER_MODEL  = "claude-haiku-4-5-20251001"   # fast + cheap for relevance filter
ANALYSIS_MODEL = "claude-sonnet-4-6"           # quality for full analysis + writing
