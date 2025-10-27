import os
import re
import random
import streamlit as st
from datetime import datetime

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(
    page_title="BVA Finder Pro",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session ID
# -----------------------------
if "client_id" not in st.session_state:
    st.session_state.client_id = f"{random.randint(1000000000, 9999999999)}.{random.randint(1000000000, 9999999999)}"

# -----------------------------
# Google Sheet Logging
# -----------------------------
def log_to_sheet(session_id, search_term, document_viewed):
    try:
        if "gcp_service_account" not in st.secrets:
            return
        import gspread
        from google.oauth2.service_account import Credentials
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        SERVICE_ACCOUNT_INFO = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
        gs_client = gspread.authorize(creds)
        SHEET_KEY = "1siHLnL8t1OZMvbrALNrgMp9w54IhtlSTgeGqMXSt7JA"
        sheet = gs_client.open_by_key(SHEET_KEY).sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, search_term, session_id, document_viewed])
    except:
        pass

# -----------------------------
# Theme
# -----------------------------
st.markdown("""<style>
html, body, [class*="stAppViewContainer"], [class*="stApp"], 
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #f6f7f9 !important;
    color: #1c1e21 !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] {
    background-color: #ffffff !important;
    color: #1c1e21 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}
.centered-text {
    text-align: center;
    color: #1877f2 !important;
    font-weight: bold;
    margin-bottom: 8px;
}
.sub-title {
    text-align: center;
    color: #555555;
    font-size: 16px;
    margin-bottom: 25px;
}
.search-result {
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 30px;
    background-color: #ffffff;
    text-align: left;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.search-result:nth-child(even) {
    background-color: #f0f4f9;
}
.result-summary {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 12px 20px;
    margin-bottom: 20px;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    display: inline-block;
}
mark {
    background-color: #ffe58f;
    color: #000000;
    padding: 0 3px;
    border-radius: 3px;
}
div.stTextInput > label > div {
    color: #1877f2 !important;
    font-weight: bold;
    font-size: 16px;
}
div.stTextInput input {
    border: 2px solid #1877f2 !important;
    border-radius: 6px !important;
    padding: 10px !important;
    width: 100% !important;
    font-size: 16px !important;
    color: #000000 !important;
    background-color: #ffffff !important;
    caret-color: #1877f2 !important;
}
div.stTextInput input::placeholder {
    color: #888888 !important;
}
div.stButton > button {
    background-color: #1877f2 !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    padding: 8px 18px !important;
    font-size: 15px !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    background-color: #145dbf !important;
}
.footer-text {
    font-size: 11px;
    color: #555555;
    text-align: center;
    margin-top: 40px;
    line-height: 1.5;
}
</style>""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown('<h1 class="centered-text">BVA Finder Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Quickly search and explore BVA documents for conditions and claims information.</p>', unsafe_allow_html=True)

# -----------------------------
# Folders
# -----------------------------
folders = [f"document{i}" for i in range(1, 6)]
existing_folders = [f for f in folders if os.path.exists(f)]
if not existing_folders:
    st.error("No folders found! Make sure the folders document1..document5 exist.")
    st.stop()

# -----------------------------
# Cache Files
# -----------------------------
@st.cache_data(show_spinner=False)
def load_all_documents(folders):
    documents = []
    for folder in folders:
        for filename in os.listdir(folder):
            if filename.endswith(".txt"):
                path = os.path.join(folder, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append((filename, content))
                except Exception:
                    pass
    return documents

all_documents = load_all_documents(existing_folders)

# -----------------------------
# Synonyms
# -----------------------------
SYNONYMS = {
    "osa": ["obstructive sleep apnea", "sleep apnea", "sleep"],
    "stone": ["stones"],
    "migraines": ["headache", "headaches", "head aches", "migraine", "migrane", "migrain", "mirgaine", "migarine"],
    "ptsd": ["post-traumatic stress disorder"],
    "behcet": ["bechet", "behçet’s"],
    "suicide": ["suicidal ideation", "suicidal thoughts", "self-harm", "suicide attempt"],
    "suicidal ideation": ["suicidal thoughts", "self-harm", "suicide attempt"],
    "IBS": ["\(IBS\)"]
}

# Make synonyms bidirectional
bidirectional = {}
for key, syns in SYNONYMS.items():
    for syn in syns:
        bidirectional.setdefault(syn, []).append(key)
        for other in syns:
            if other != syn:
                bidirectional.setdefault(syn, []).append(other)
    bidirectional.setdefault(key, []).extend(syns)
for k, v in bidirectional.items():
    bidirectional[k] = sorted(set(v))
SYNONYMS = bidirectional

# -----------------------------
# Stopwords
# -----------------------------
STOPWORDS = {"to", "and", "was", "not", "the", "a", "an", "of", "but", "in", "on", "for", "with", "is", "are", "at", "by", "from"}

# -----------------------------
# Utility
# -----------------------------
def build_search_pattern(words, synonyms=None):
    all_terms = [w for w in words if w not in STOPWORDS]
    if synonyms:
        all_terms += [w for w in synonyms if w not in STOPWORDS]
    if not all_terms:
        return None
    escaped = [re.escape(t) + r"(s|es)?" for t in all_terms]
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)

def highlight_text(text, pattern):
    if not pattern:
        return text
    def repl(m):
        word = m.group(0).lower()
        return word if word in STOPWORDS else f"<mark>{m.group(0)}</mark>"
    return pattern.sub(repl, text)

def generate_snippets(content, pattern, window=200, max_snippets=3):
    if not pattern:
        return []
    matches = [m for m in pattern.finditer(content) if m.group(0).lower() not in STOPWORDS]
    if not matches:
        return []
    random.shuffle(matches)
    snippets = []
    for m in matches[:max_snippets]:
        start = max(m.start() - window, 0)
        end = min(m.end() + window, len(content))
        snippet = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
        snippets.append(snippet)
    return snippets

# -----------------------------
# Progressive Search (phrase fallback)
# -----------------------------
def progressive_search(search_input, documents):
    phrase_pattern = r'"([^"]+)"'
    phrases = re.findall(phrase_pattern, search_input.lower())
    temp_input = re.sub(phrase_pattern, "", search_input.lower()).strip()
    words = [w for w in temp_input.split() if w not in STOPWORDS]

    synonyms = [s for w in words if w in SYNONYMS for s in SYNONYMS[w]]
    all_terms = list(set(words + phrases + synonyms))
    if not all_terms:
        return []

    def try_phrases(phrases, content):
        found_phrases = set()
        for phrase in phrases:
            # If phrase not found, try progressively shorter versions
            tokens = phrase.split()
            while tokens:
                partial = " ".join(tokens)
                if re.search(re.escape(partial), content, re.IGNORECASE):
                    found_phrases.add(phrase)
                    break
                tokens = tokens[:-1]
        return found_phrases

    pattern = build_search_pattern(all_terms)
    results = []

    for file_name, content in documents:
        found_terms = set()

        # Single words and synonyms
        for word in words + synonyms:
            if re.search(rf"\b{re.escape(word)}[a-zA-Z]{{0,2}}(s|es)?\b", content, re.IGNORECASE):
                found_terms.add(word)

        # Progressive phrase fallback
        found_phrases = try_phrases(phrases, content)
        found_terms.update(found_phrases)

        required_terms = set(words + phrases)
        if not required_terms.issubset(found_terms):
            continue

        matches = [m for m in pattern.finditer(content) if m.group(0).lower() not in STOPWORDS]
        if not matches:
            continue

        snippets = generate_snippets(content, pattern)
        score = len(matches) * 10 + len(found_terms) * 5

        results.append({
            "file_name": file_name,
            "score": score,
            "total_matches": len(matches),
            "content": content,
            "pattern": pattern,
            "snippets": snippets,
            "found_words": found_terms
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:500]

# -----------------------------
# Search UI
# -----------------------------
search_input = st.text_input(
    "🔍 Enter condition or term. Use quotes for exact phrases.",
    value="",
    placeholder='PTSD, Sleep apnea, "Migraines is granted"...'
)

search_input = search_input.replace('“', '"').replace('”', '"')

if search_input:
    query = search_input.lower().strip()
    log_to_sheet(st.session_state.client_id, search_input, "")
    results = progressive_search(search_input, all_documents)

    if not results:
        st.warning("No documents matched your search.")
    else:
        st.markdown(f'<div class="result-summary">Showing {len(results)} most relevant document(s)</div>', unsafe_allow_html=True)

        for i, doc in enumerate(results, 1):
            clean_name = doc["file_name"].replace(".txt", "")
            found_str = ", ".join(sorted(doc["found_words"])) or "None"

            header = (
                f"<b>#{i} {clean_name} — <mark>{doc['total_matches']} match(es)</mark></b><br>"
                f"<b>Match Score:</b> <i>{doc['score']}</i><br>"
                f"<b>Found:</b> <i>{found_str}</i><br><br>"
            )
            snippet_html = "".join([highlight_text(s, doc["pattern"]) + "<br><br>" for s in doc["snippets"]])

            st.markdown(f'<div class="search-result">{header}{snippet_html}'
                        f'<div style="color:#555; font-style:italic; margin-bottom:8px;">Click “Show Full Document” to read the entire file.</div>'
                        f'</div>', unsafe_allow_html=True)

            if st.button(f"Show Full Document: #{i} {clean_name}", key=f"show_{i}_{clean_name}"):
                log_to_sheet(st.session_state.client_id, search_input, clean_name)
                st.markdown(f'<div class="search-result">{highlight_text(doc["content"], doc["pattern"])}</div>', unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer-text">
Disclaimer: This site indexes publicly available VA.gov BVA decisions.<br>
No personal data is uploaded or stored.<br>
For informational use only — not medical or legal advice.
</div>
""", unsafe_allow_html=True)
