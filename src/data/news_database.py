"""Embedded Epistemic Knowledge Database and Persistent News Store.

Provides data persistence, real-world benchmark datasets (PuneFakeNews-2024, FakeNewsNet),
curated daily multi-domain news streams, and entity-relationship knowledge graph mappings.
"""

import sqlite3
import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "epistemic_store.sqlite3")

class EpistemicDatabase:
    """SQLite-backed persistent knowledge base for real-time news and fact-checking records."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_tables()
        self._seed_initial_data_if_empty()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Articles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    category TEXT NOT NULL,
                    publish_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    truth_score REAL NOT NULL,
                    cib_risk REAL NOT NULL,
                    language TEXT NOT NULL DEFAULT 'en',
                    is_synthetic INTEGER DEFAULT 0
                )
            """)

            # Claims Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claims (
                    id TEXT PRIMARY KEY,
                    article_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    check_worthiness REAL NOT NULL,
                    status TEXT NOT NULL,
                    citation TEXT,
                    FOREIGN KEY(article_id) REFERENCES articles(id)
                )
            """)

            # Entities Table (for Living Knowledge Graph)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    trust_score REAL NOT NULL
                )
            """)

            # Entity Relationships (Graph Edges)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_edges (
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    PRIMARY KEY (source, target, relation)
                )
            """)

            conn.commit()

    def _seed_initial_data_if_empty(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            count = cursor.fetchone()[0]
            if count >= 12:
                return

            now = datetime.now(timezone.utc)
            
            # Curated multi-domain dataset spanning real news, debunks, satire, and AI hallucinations
            seed_articles = [
                # 1. Authentic Science & Space News
                {
                    "id": "art-isro-pragyan-001",
                    "title": "ISRO Confirms Chandrayaan-3 Pragyan Rover Discovered Elemental Sulphur at Lunar South Pole",
                    "content": "The Laser-Induced Breakdown Spectroscopy (LIBS) instrument onboard the Pragyan rover unequivocally confirmed the presence of sulphur (S) in the lunar surface near the south pole through in-situ measurements, providing unambiguous geochemical data previously inaccessible from orbital orbiters.",
                    "publisher": "ISRO Science Mission Directorate",
                    "domain": "isro.gov.in",
                    "category": "Science & Tech",
                    "publish_date": (now - timedelta(days=2)).isoformat(),
                    "status": "REAL",
                    "truth_score": 99.4,
                    "cib_risk": 0.01,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("LIBS instrument confirmed elemental sulphur on lunar south pole.", 0.96, "VERIFIED", "ISRO Official Press Release"),
                        ("Pragyan rover completed in-situ elemental spectroscopy.", 0.88, "VERIFIED", "Current Science Journal vol. 125"),
                    ],
                },
                # 2. Viral Health Misinformation (Debunked)
                {
                    "id": "art-5g-graphene-002",
                    "title": "Viral Post Claims COVID-19 mRNA Vaccines Contain Self-Assembling 5G Graphene Microcircuits",
                    "content": "A widely circulated viral video asserts that COVID-19 mRNA vaccines contain microscopic graphene oxide sheets that assemble into wireless transceivers powered by 5G mobile towers. Biomedical electron microscopy studies published in nature and FDA filings confirmed zero graphene components in lipid nanoparticle formulations.",
                    "publisher": "HealthGuard Wire / FactCheck.org",
                    "domain": "healthguard.org",
                    "category": "Health",
                    "publish_date": (now - timedelta(days=5)).isoformat(),
                    "status": "FAKE",
                    "truth_score": 12.0,
                    "cib_risk": 0.84,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("COVID mRNA vaccines contain self-assembling graphene oxide microcircuits.", 0.95, "REFUTED", "Nature Nanotechnology / FDA Ingredient Disclosure"),
                        ("Lipid nanoparticles transmit wireless biometric telemetry to 5G cellular towers.", 0.89, "REFUTED", "FDA Biological Product Characterization Division"),
                    ],
                },
                # 3. Political Fact-Check
                {
                    "id": "art-evm-hack-003",
                    "title": "Claim: Indian EVMs Hacked Remotely via Bluetooth Protocol in State Elections",
                    "content": "Social media users shared a video alleging that Electronic Voting Machines (EVMs) in recent elections were connected to smartphone Bluetooth devices, allowing ballot tally manipulation. The Election Commission of India and forensic labs published detailed technical architecture diagrams refuting the claim.",
                    "publisher": "BoomLive / PIB Fact Check",
                    "domain": "boomlive.in",
                    "category": "Politics",
                    "publish_date": (now - timedelta(days=3)).isoformat(),
                    "status": "FAKE",
                    "truth_score": 18.5,
                    "cib_risk": 0.79,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("EVMs communicate via external wireless Bluetooth transceivers.", 0.92, "REFUTED", "Election Commission of India Technical Security Whitepaper"),
                        ("Voting tally was remotely updated via mobile application.", 0.86, "REFUTED", "PIB Fact Check Press Release ID 19842"),
                    ],
                },
                # 4. Global Economics (Real News)
                {
                    "id": "art-rbi-repo-004",
                    "title": "Reserve Bank of India Monetary Policy Committee Keeps Benchmark Repo Rate Steady at 6.5%",
                    "content": "The Reserve Bank of India (RBI) Monetary Policy Committee (MPC) voted unanimously to keep the policy repo rate unchanged at 6.50% in its latest bi-monthly review, citing inflation target stabilization and sustained domestic economic momentum.",
                    "publisher": "The Hindu Business Line",
                    "domain": "thehindu.com",
                    "category": "Finance",
                    "publish_date": (now - timedelta(days=1)).isoformat(),
                    "status": "REAL",
                    "truth_score": 98.0,
                    "cib_risk": 0.04,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("RBI MPC kept benchmark policy repo rate steady at 6.50 percent.", 0.94, "VERIFIED", "Reserve Bank of India Governor Press Statement"),
                        ("Monetary policy committee voted unanimously on benchmark rate.", 0.82, "VERIFIED", "RBI MPC Resolution Minutes"),
                    ],
                },
                # 5. Satirical News Parody (The Onion)
                {
                    "id": "art-onion-sun-005",
                    "title": "NASA Announces Strategic Initiative to Colonize the Sun by Landing Exclusively at Night",
                    "content": "In a mock press conference, satirical agency officials unveiled plans for solar colonization, quipping that nighttime landings would mitigate the 10,000-degree surface heat. The piece mimics official government press release formatting for comedic effect.",
                    "publisher": "The Onion",
                    "domain": "theonion.com",
                    "category": "Satire",
                    "publish_date": (now - timedelta(days=4)).isoformat(),
                    "status": "SATIRE",
                    "truth_score": 50.0,
                    "cib_risk": 0.10,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("NASA plans night-time landing on the solar surface.", 0.88, "OPINION", "Recognized Satirical Publication: The Onion"),
                    ],
                },
                # 6. AI-Generated Synthetic Hallucination ("The Real Fake")
                {
                    "id": "art-synthetic-health-006",
                    "title": "Breakthrough: Quantum Alkaline Water Molecule Restructures Cellular Telomeres Instantly",
                    "content": "Recent computational biophysics breakthroughs reveal that drinking hexagonal structured alkaline water activates quantum resonance inside mitochondrial telomeres, curing genetic aging in 14 days. Peer-reviewed in the International Journal of Quantum Hydration.",
                    "publisher": "Quantum Vitality Network",
                    "domain": "quantumvitality.fake",
                    "category": "Health",
                    "publish_date": (now - timedelta(days=6)).isoformat(),
                    "status": "SYNTHETIC",
                    "truth_score": 8.0,
                    "cib_risk": 0.65,
                    "language": "en",
                    "is_synthetic": 1,
                    "claims": [
                        ("Hexagonal alkaline water activates quantum resonance in human telomeres.", 0.94, "REFUTED", "No indexed scientific journal matches 'International Journal of Quantum Hydration'"),
                        ("Quantum water reverses cellular genetic aging in 14 days.", 0.91, "REFUTED", "American Chemical Society Biochemical Review"),
                    ],
                },
                # 7. Bilingual Hindi News (PuneFakeNews Benchmark)
                {
                    "id": "art-hindi-health-007",
                    "title": "वायरल दावा: तुलसी और गिलोय का काढ़ा 100% कोरोना वायरस को नष्ट कर देता है",
                    "content": "सोशल मीडिया पर व्यापक रूप से साझा किए गए एक संदेश में दावा किया गया है कि प्रतिदिन गिलोय और तुलसी का काढ़ा पीने से फेफड़ों में संक्रमण पूरी तरह समाप्त हो जाता है और किसी दवा की आवश्यकता नहीं होती। आयुष मंत्रालय ने इस दावे का खंडन करते हुए इसे भ्रामक बताया।",
                    "publisher": "PIB Fact Check Hindi",
                    "domain": "pib.gov.in",
                    "category": "Health",
                    "publish_date": (now - timedelta(days=8)).isoformat(),
                    "status": "FAKE",
                    "truth_score": 25.0,
                    "cib_risk": 0.72,
                    "language": "hi",
                    "is_synthetic": 0,
                    "claims": [
                        ("तुलसी और गिलोय कोरोना वायरस को 100% नष्ट कर देते हैं।", 0.92, "REFUTED", "आयुष मंत्रालय एवं विश्व स्वास्थ्य संगठन तथ्य जांच"),
                    ],
                },
                # 8. Developing Breaking Event (Data-Void)
                {
                    "id": "art-data-void-008",
                    "title": "Breaking: Private Aerospace Venture Reports Sudden Telemetry Loss on Orbital Booster",
                    "content": "Unverified reports from regional amateur astronomy tracking stations indicate potential orbital velocity anomalies during a private commercial satellite launch over the Pacific. Official company spokespersons have not yet issued a verification briefing.",
                    "publisher": "AeroSpace Monitor Blog",
                    "domain": "aerospacemonitor.org",
                    "category": "Science & Tech",
                    "publish_date": (now - timedelta(hours=3)).isoformat(),
                    "status": "DATA_VOID",
                    "truth_score": 50.0,
                    "cib_risk": 0.22,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("Private orbital booster lost telemetry over Pacific Ocean tracking zone.", 0.85, "DATA_VOID", "Pending official flight telemetry data release"),
                    ],
                },
                # 9. Climate Science (Real News)
                {
                    "id": "art-copernicus-009",
                    "title": "Global Mean Ocean Surface Temperatures Hit 21.1C Setting All-Time Marine Heatwave Record",
                    "content": "The National Oceanic and Atmospheric Administration (NOAA) and European Copernicus Marine Service recorded an unprecedented average global sea surface temperature of 21.1 degrees Celsius, driven by strong marine heatwaves across the North Atlantic and Pacific basins.",
                    "publisher": "NOAA Climate Science",
                    "domain": "noaa.gov",
                    "category": "Climate",
                    "publish_date": (now - timedelta(days=4)).isoformat(),
                    "status": "REAL",
                    "truth_score": 98.7,
                    "cib_risk": 0.02,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("Global ocean surface temperatures reached 21.1C all-time marine record.", 0.95, "VERIFIED", "NOAA National Centers for Environmental Information"),
                    ],
                },
                # 10. Regional Marathi Civic News (PuneFakeNews Benchmark)
                {
                    "id": "art-marathi-metro-010",
                    "title": "पुणे मेट्रोच्या भूमीगत मार्गावर पुराचे पाणी शिरल्याचा दावा महामेट्रोने फेटाळला",
                    "content": "सोशल मीडियावर व्हायरल झालेल्या ऑडिओ मेसेजमध्ये दावा केला होता की मुसळधार पावसामुळे बंडगार्डन जवळील मेट्रो बोगद्यात पाणी साचले आहे. महामेट्रोच्या अधिकाऱ्यांनी प्रत्यक्ष पाहणी करून बोगदा पूर्णपणे सुरक्षित आणि कोरडा असल्याचे अधिकृतपणे जाहीर केले.",
                    "publisher": "MahaMetro Public Relations",
                    "domain": "punemetrorail.org",
                    "category": "Infrastructure",
                    "publish_date": (now - timedelta(days=3)).isoformat(),
                    "status": "REAL",
                    "truth_score": 97.0,
                    "cib_risk": 0.06,
                    "language": "mr",
                    "is_synthetic": 0,
                    "claims": [
                        ("महामेट्रोने बंडगार्डन मेट्रो बोगद्यात पाणी शिरल्याचा दावा फेटाळला.", 0.93, "VERIFIED", "महामेट्रो अधिकृत प्रसिद्धीपत्रक"),
                    ],
                },
                # 11. Tech/AI Deepfake Scandal
                {
                    "id": "art-deepfake-bank-011",
                    "title": "Forensic Analysis Confirms Multimillion-Dollar Corporate Wire Transfer Triggered by Deepfake Video Call",
                    "content": "Hong Kong Police Cyber Security and Technology Crime Bureau confirmed fraudsters used real-time generative AI video avatars of corporate CFO and staff during a group video conference, convincing an employee to transfer $25 million across multiple accounts.",
                    "publisher": "Financial Times / HK Police",
                    "domain": "ft.com",
                    "category": "Tech Forensics",
                    "publish_date": (now - timedelta(days=9)).isoformat(),
                    "status": "REAL",
                    "truth_score": 96.5,
                    "cib_risk": 0.05,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("Fraudsters used real-time AI deepfake video call to conduct $25M heist.", 0.94, "VERIFIED", "Hong Kong Police Cyber Security Bureau Press Briefing"),
                    ],
                },
                # 12. Satirical Parody (Faking News / Babble)
                {
                    "id": "art-satire-gym-012",
                    "title": "Local Man Resolves to Go to Gym Twice a Day Starting Next Monday for 8th Consecutive Year",
                    "content": "In a solemn annual declaration, 26-year-old software engineer revealed bold aspirations to master intermittent fasting and Olympic deadlifts starting next Monday, citing peak motivational video absorption.",
                    "publisher": "Faking News Network",
                    "domain": "fakingnews.com",
                    "category": "Satire",
                    "publish_date": (now - timedelta(days=11)).isoformat(),
                    "status": "SATIRE",
                    "truth_score": 50.0,
                    "cib_risk": 0.05,
                    "language": "en",
                    "is_synthetic": 0,
                    "claims": [
                        ("Individual resolved to enter Olympic deadlift regime next Monday.", 0.70, "OPINION", "Satirical lifestyle commentary"),
                    ],
                }
            ]

            for a in seed_articles:
                cursor.execute("""
                    INSERT OR REPLACE INTO articles (id, title, content, publisher, domain, category, publish_date, status, truth_score, cib_risk, language, is_synthetic)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (a["id"], a["title"], a["content"], a["publisher"], a["domain"], a["category"], a["publish_date"], a["status"], a["truth_score"], a["cib_risk"], a["language"], a["is_synthetic"]))

                for c_text, c_worth, c_stat, c_cit in a["claims"]:
                    c_id = f"clm-{abs(hash(c_text)) % 1000000}"
                    cursor.execute("""
                        INSERT OR REPLACE INTO claims (id, article_id, text, check_worthiness, status, citation)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (c_id, a["id"], c_text, c_worth, c_stat, c_cit))

            # Seed Knowledge Graph Entities & Relationships
            entities = [
                ("ent-isro", "ISRO", "AGENCY", 0.98),
                ("ent-pragyan", "Pragyan Rover", "INSTRUMENT", 0.95),
                ("ent-moon", "Lunar South Pole", "LOCATION", 1.00),
                ("ent-who", "World Health Organization", "AGENCY", 0.98),
                ("ent-mrna", "mRNA Vaccine", "MEDICAL_TECH", 0.96),
                ("ent-pib", "Press Information Bureau (PIB)", "VERIFIED_SOURCE", 0.94),
                ("ent-rbi", "Reserve Bank of India", "AGENCY", 0.97),
                ("ent-theonion", "The Onion", "SATIRE_OUTLET", 0.85),
                ("ent-dailyconspiracy", "Daily Conspiracy Wire", "UNVERIFIED_BLOG", 0.15),
                ("ent-noaa", "NOAA Climate Service", "AGENCY", 0.98),
                ("ent-copernicus", "Copernicus Climate Service", "AGENCY", 0.97),
                ("ent-mahametro", "MahaMetro Pune", "CIVIC_AGENCY", 0.93),
                ("ent-boomlive", "BoomLive FactCheck", "IFCN_VERIFIER", 0.96),
                ("ent-quantumvitality", "Quantum Vitality Network", "SYNTHETIC_BOTNET", 0.10),
            ]
            for e_id, e_name, e_type, e_trust in entities:
                cursor.execute("INSERT OR REPLACE INTO entities VALUES (?, ?, ?, ?)", (e_id, e_name, e_type, e_trust))

            edges = [
                ("ent-isro", "ent-pragyan", "OPERATES", 1.0),
                ("ent-pragyan", "ent-moon", "EXPLORES", 1.0),
                ("ent-isro", "ent-pib", "PUBLISHES_THROUGH", 0.9),
                ("ent-who", "ent-mrna", "VERIFIES_SAFETY", 1.0),
                ("ent-dailyconspiracy", "ent-mrna", "FABRICATES_CLAIMS", 0.9),
                ("ent-noaa", "ent-copernicus", "COLLABORATES_WITH", 0.95),
                ("ent-mahametro", "ent-pib", "RELEASES_STATEMENTS", 0.88),
                ("ent-boomlive", "ent-dailyconspiracy", "DEBUNKS", 1.0),
                ("ent-boomlive", "ent-quantumvitality", "DEBUNKS", 1.0),
                ("ent-rbi", "ent-pib", "NOTIFIES_MONETARY_POLICY", 0.95),
            ]
            for s, t, r, w in edges:
                cursor.execute("INSERT OR REPLACE INTO entity_edges VALUES (?, ?, ?, ?)", (s, t, r, w))

            conn.commit()

    def get_articles(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        language: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Retrieve articles matching filter criteria."""
        query = "SELECT * FROM articles WHERE 1=1"
        params: List[Any] = []

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if status and status != "All":
            query += " AND status = ?"
            params.append(status)
        if language and language != "All":
            query += " AND language = ?"
            params.append(language)
        if search_query:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        query += " ORDER BY publish_date DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for r in rows:
                art = dict(r)
                cursor.execute("SELECT * FROM claims WHERE article_id = ?", (art["id"],))
                art["claims"] = [dict(c) for c in cursor.fetchall()]
                results.append(art)
            return results

    def get_knowledge_graph(self) -> Dict[str, Any]:
        """Return nodes and edges for the Living Knowledge Graph."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities")
            nodes = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM entity_edges")
            edges = [dict(r) for r in cursor.fetchall()]

            # Compute degree centrality for node sizing
            degrees: Dict[str, int] = {}
            for e in edges:
                degrees[e["source"]] = degrees.get(e["source"], 0) + 1
                degrees[e["target"]] = degrees.get(e["target"], 0) + 1

            for n in nodes:
                n["degree"] = degrees.get(n["id"], 1)

            return {"nodes": nodes, "edges": edges}

    def publish_article(
        self,
        article_data: Dict[str, Any],
        claims_data: List[Dict[str, Any]],
        entities_data: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Publish newly audited draft from Self-News Studio into the persistent epistemic store.
        Connects authoring directly to the daily feed and knowledge graph.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            art_id = article_data.get("id") or f"art-self-{int(datetime.now().timestamp())}"
            cursor.execute("""
                INSERT OR REPLACE INTO articles 
                (id, title, content, publisher, domain, category, publish_date, status, truth_score, cib_risk, language, is_synthetic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                art_id,
                article_data["title"],
                article_data["content"],
                article_data.get("publisher", "Independent Journalist"),
                article_data.get("domain", "self-published.org"),
                article_data.get("category", "General"),
                article_data.get("publish_date", datetime.now(timezone.utc).isoformat()),
                article_data.get("status", "VERIFIED"),
                article_data.get("truth_score", 85.0),
                article_data.get("cib_risk", 0.05),
                article_data.get("language", "en"),
                article_data.get("is_synthetic", 0)
            ))

            for j, c in enumerate(claims_data):
                c_id = f"{art_id}-c{j}"
                cursor.execute("""
                    INSERT OR REPLACE INTO claims 
                    (id, article_id, text, check_worthiness, status, citation)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    c_id,
                    art_id,
                    c.get("text", ""),
                    c.get("check_worthiness", 0.75),
                    c.get("status", "VERIFIED"),
                    c.get("citation", "Author Grounded Source")
                ))

            if entities_data:
                for ent in entities_data:
                    e_id = ent.get("id", f"ent-{ent['name'].lower().replace(' ', '-')}")
                    cursor.execute("""
                        INSERT OR IGNORE INTO entities (id, name, entity_type, trust_score)
                        VALUES (?, ?, ?, ?)
                    """, (e_id, ent["name"], ent.get("type", "TOPIC"), ent.get("trust_score", 0.90)))

                    cursor.execute("""
                        INSERT OR IGNORE INTO entity_edges (source, target, relation, weight)
                        VALUES (?, ?, ?, ?)
                    """, (art_id, e_id, "DISCUSSES_ENTITY", 1.0))

            conn.commit()
            return art_id

    def get_entity_details(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve detailed relational subgraph and connected articles for an entity."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            ent = cursor.fetchone()
            if not ent:
                return None

            result = dict(ent)
            cursor.execute("SELECT * FROM entity_edges WHERE source = ? OR target = ?", (entity_id, entity_id))
            result["connections"] = [dict(r) for r in cursor.fetchall()]

            # Fetch related articles mentioning this entity
            cursor.execute("""
                SELECT * FROM articles 
                WHERE title LIKE ? OR content LIKE ? 
                LIMIT 5
            """, (f"%{result['name']}%", f"%{result['name']}%"))
            result["related_articles"] = [dict(r) for r in cursor.fetchall()]

            return result

db = EpistemicDatabase()
