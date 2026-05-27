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
    # ── Import regulations, tariffs, quotas ──
    "Asia Pacific IT hardware import regulation tariff customs duty",
    "Asia Pacific technology equipment import quota restriction ban",
    "Australia technology import customs duty regulation",
    "Japan IT equipment import tariff regulation",
    "India IT hardware import duty regulation customs DPIIT",
    "Singapore Malaysia technology import licensing restriction",
    "South Korea Taiwan semiconductor import export regulation",
    "Vietnam Thailand IT equipment import regulation customs",
    "APAC ICT equipment import quota tariff trade restriction",
    "China APAC technology import restriction ban hardware",
    # ── Distributor, reseller, system integrator licensing ──
    "Asia Pacific IT distributor license requirement regulation",
    "APAC technology reseller wholesaler licensing compliance",
    "Asia Pacific system integrator certification accreditation requirement",
    "APAC IT channel partner authorized distributor regulation",
    "Australia Singapore India technology reseller license permit",
    "Asia Pacific value-added reseller VAR certification requirement",
    "APAC IT vendor channel compliance distributor accreditation",
    "Asia Pacific government IT procurement vendor certification",
]

# ── Localised Google News queries (non-English) ──────────────────────────────
# Local-language queries catch regulatory announcements that never appear in
# English news. Each entry specifies the query text and the Google News locale.
LOCALIZED_QUERIES = [
    # ── Japan (Japanese) ──
    {"q": "サイバーセキュリティ 規制 法律 ガイドライン",      "hl": "ja", "gl": "JP", "ceid": "JP:ja"},
    {"q": "データ保護 個人情報 プライバシー 法律 規制",       "hl": "ja", "gl": "JP", "ceid": "JP:ja"},
    {"q": "デジタル庁 AI 人工知能 規制 法案",               "hl": "ja", "gl": "JP", "ceid": "JP:ja"},
    {"q": "IT機器 輸入規制 ライセンス 流通 卸売 販売代理店", "hl": "ja", "gl": "JP", "ceid": "JP:ja"},
    {"q": "金融庁 経済産業省 IT クラウド 規制 指針",         "hl": "ja", "gl": "JP", "ceid": "JP:ja"},
    # ── South Korea (Korean) ──
    {"q": "사이버보안 정보보호 규제 법률 정책",               "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    {"q": "개인정보보호법 데이터 규제 IT",                   "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    {"q": "인공지능 AI 규제 법안 정책",                     "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    {"q": "IT 유통 총판 리셀러 라이선스 인증 규정",           "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
    # ── Taiwan (Traditional Chinese) ──
    {"q": "資安 網路安全 法規 規定 台灣",                    "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
    {"q": "個人資料保護法 數位 AI 規定",                    "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
    {"q": "IT 進口 關稅 通路 代理商 法規",                   "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
    # ── Hong Kong (Traditional Chinese) ──
    {"q": "網絡安全 數據保護 私隱 法規 香港",                "hl": "zh-HK", "gl": "HK", "ceid": "HK:zh-Hant"},
    {"q": "人工智能 AI 科技 監管 規定 香港",                 "hl": "zh-HK", "gl": "HK", "ceid": "HK:zh-Hant"},
    # ── Malaysia (Malay) ──
    {"q": "keselamatan siber regulasi undang-undang Malaysia",       "hl": "ms", "gl": "MY", "ceid": "MY:ms"},
    {"q": "perlindungan data peribadi PDPA lesen peraturan",         "hl": "ms", "gl": "MY", "ceid": "MY:ms"},
    {"q": "pengedar pemborong reseller IT lesen keperluan peraturan", "hl": "ms", "gl": "MY", "ceid": "MY:ms"},
    # ── Vietnam (Vietnamese) ──
    {"q": "an ninh mạng quy định pháp luật công nghệ thông tin",    "hl": "vi", "gl": "VN", "ceid": "VN:vi"},
    {"q": "bảo vệ dữ liệu cá nhân quy định AI trí tuệ nhân tạo",   "hl": "vi", "gl": "VN", "ceid": "VN:vi"},
    {"q": "nhập khẩu thiết bị CNTT giấy phép phân phối quy định",   "hl": "vi", "gl": "VN", "ceid": "VN:vi"},
    # ── Thailand (Thai) ──
    {"q": "ความปลอดภัยไซเบอร์ กฎหมาย พระราชบัญญัติ",             "hl": "th", "gl": "TH", "ceid": "TH:th"},
    {"q": "PDPA คุ้มครองข้อมูลส่วนบุคคล กฎหมาย ระเบียบ",          "hl": "th", "gl": "TH", "ceid": "TH:th"},
    {"q": "นำเข้าอุปกรณ์ IT ใบอนุญาต ผู้จัดจำหน่าย กฎระเบียบ",   "hl": "th", "gl": "TH", "ceid": "TH:th"},
    # ── India (Hindi) ──
    {"q": "साइबर सुरक्षा नियम कानून भारत",                       "hl": "hi", "gl": "IN", "ceid": "IN:hi"},
    {"q": "डेटा संरक्षण गोपनीयता कानून डिजिटल",                  "hl": "hi", "gl": "IN", "ceid": "IN:hi"},
    {"q": "आईटी उपकरण आयात लाइसेंस वितरक नियम",                  "hl": "hi", "gl": "IN", "ceid": "IN:hi"},
    # ── Indonesia (Bahasa Indonesia) ──
    {"q": "keamanan siber regulasi undang-undang teknologi Indonesia",      "hl": "id", "gl": "ID", "ceid": "ID:id"},
    {"q": "perlindungan data pribadi PDP regulasi digital Indonesia",       "hl": "id", "gl": "ID", "ceid": "ID:id"},
    {"q": "kecerdasan buatan AI regulasi kebijakan Indonesia",              "hl": "id", "gl": "ID", "ceid": "ID:id"},
    {"q": "importir distributor reseller lisensi izin teknologi IT",        "hl": "id", "gl": "ID", "ceid": "ID:id"},
    {"q": "Kominfo BSSN OJK regulasi teknologi digital Indonesia",          "hl": "id", "gl": "ID", "ceid": "ID:id"},
]

# ── Relevance keywords ────────────────────────────────────────────────────────
RELEVANCE_KEYWORDS = [
    # Regulatory / legal process words
    "regulation", "regulations", "regulatory", "legislation", "legislative",
    "law", "laws", "legal", "act", "acts", "bill", "bills",
    "directive", "circular", "guideline", "guidelines", "framework",
    "requirement", "requirements", "standard", "standards",
    "compliance", "mandate", "mandated", "mandatory", "enforcement",
    "amendment", "amendments", "consultation", "draft", "proposal",
    "policy", "policies", "rule", "rules", "ruling", "order", "decree",
    "code", "codes", "notice", "notification", "gazette",
    "enacted", "enacted", "passed", "signed", "implemented", "proposed",
    "approved", "prohibited", "banned", "restricted",
    # Technology domains
    "cybersecurity", "cyber security", "cyber", "cyber law", "cyber rules",
    "data protection", "data privacy", "privacy", "personal data",
    "cloud", "cloud computing", "cloud services",
    "artificial intelligence", "AI", "machine learning", "generative AI",
    "data centre", "data center", "data centers", "data centres",
    "semiconductor", "chip", "chips", "hardware", "software",
    "network", "networking", "telecoms", "telecommunications", "telecom",
    "5G", "broadband", "internet", "digital",
    "encryption", "cryptography", "quantum",
    "critical infrastructure", "supply chain", "fintech",
    "open banking", "CBDC", "digital currency", "blockchain",
    "IoT", "internet of things", "edge computing",
    # Regulatory bodies / actors
    "government", "ministry", "minister", "authority", "agency",
    "regulator", "regulates", "regulated", "parliament", "congress",
    "cabinet", "senate", "commission", "committee", "bureau", "department",
    # Import / trade / customs
    "import", "imports", "imported", "importing",
    "export", "exports", "exported",
    "customs", "tariff", "tariffs", "quota", "quotas",
    "duty", "duties", "trade", "trade restriction", "trade barrier",
    "border", "procurement", "tender", "sanctions",
    # Distribution / channel licensing
    "distributor", "distributors", "distribution",
    "reseller", "resellers", "wholesaler", "wholesalers", "dealer", "dealers",
    "channel partner", "channel partners", "system integrator",
    "value-added reseller", "VAR", "authorized dealer",
    "licence", "licences", "license", "licenses", "licensing",
    "permit", "permits", "accreditation", "certified", "certification",
    "registered", "registration", "approved vendor",
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
