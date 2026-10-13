import json, urllib.request, urllib.parse, os, re, html, time

AGENTROUTER_KEY = os.environ.get("AGENTROUTER_API_KEY", "")
BASE = "https://agentrouter.org/v1"
MODEL = "deepseek-v4-flash"

AR_HEADERS = {
    "Content-Type": "application/json",
    "Originator": "codex_cli_rs",
    "Version": "0.101.0",
    "User-Agent": "codex_cli_rs/0.101.0 (Mac OS 26.0.1; arm64) Apple_Terminal/464",
}


def ddg_search(query, n=5):
    url = "https://lite.duckduckgo.com/lite/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            page = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [], str(e)
    out = []
    for m in re.finditer(r'<a rel="nofollow" href="([^"]+)" class=\'result-link\'>([^<]+)</a>', page):
        href, title = m.groups()
        if "uddg=" in href:
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        title = html.unescape(title).strip()[:140]
        if href.startswith("http"):
            out.append({"title": title, "url": href})
            if len(out) >= n:
                break
    return out, None


def fetch_page_text(url, max_chars=2500):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception:
        return ""


def llm(prompt, system="You are a helpful research assistant. Answer concisely and cite sources."):
    if not AGENTROUTER_KEY:
        return "[AGENTROUTER_API_KEY not configured]"
    headers = dict(AR_HEADERS)
    headers["Authorization"] = f"Bearer {AGENTROUTER_KEY}"
    last_err = None
    for attempt in range(4):
        data = json.dumps({
            "model": MODEL,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
            "temperature": 0.3, "max_tokens": 1000}).encode()
        req = urllib.request.Request(f"{BASE}/chat/completions", data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read().decode().strip()
            if not body:
                raise ValueError("empty response body")
            d = json.loads(body)
            content = d["choices"][0]["message"]["content"]
            if content and content.strip():
                return content
            raise ValueError("empty message content")
        except Exception as e:
            last_err = e
            time.sleep(4 * (attempt + 1))
    return f"[LLM error: {last_err}]"


def answer(question):
    trace = []
    results, err = ddg_search(question)
    trace.append({"tool": "web_search", "query": question,
                  "results_found": len(results), "error": err})
    if not results:
        return {"answer": llm(question), "citations": [], "trace": trace,
                "note": "no search results; plain LLM fallback"}
    for r in results[:3]:
        r["snippet"] = fetch_page_text(r["url"])
        trace.append({"tool": "read_page", "url": r["url"][:60],
                      "chars": len(r["snippet"])})
    ctx = "\n\n".join(
        f"[{i+1}] {r['title']}\n    {r['url']}\n    "
        f"{r.get('snippet', '')[:1200]}" for i, r in enumerate(results))
    prompt = (f"Question: {question}\n\nWeb search results (with page content):\n{ctx}\n\n"
        "Answer the question using the search results above. "
        "Cite every factual claim inline like [1], [2] matching the numbered sources. "
        "Give specific numbers, dates, and names when the sources contain them. "
        "If the results don't contain the answer, say so honestly instead of guessing.")
    ans = llm(prompt)
    return {"answer": ans, "citations": [r["url"] for r in results],
            "sources": results, "trace": trace}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "What is the petrol price in Pakistan today?"
    print(json.dumps(answer(q), indent=2))
