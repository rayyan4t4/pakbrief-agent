import json, urllib.request, urllib.parse, os, re, html

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "poolside/laguna-s-2.1:free"

def ddg_search(query, n=5):
    url = "https://lite.duckduckgo.com/lite/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            page = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [], str(e)
    out = []
    for m in re.finditer(r"class='result-link'[^>]*>([^<]+)</a>", page):
        # find the href before this match
        pass
    for m in re.finditer(r'<a rel="nofollow" href="([^"]+)" class=\'result-link\'>([^<]+)</a>', page):
        href, title = m.groups()
        if "uddg=" in href:
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        title = html.unescape(title).strip()[:120]
        if href.startswith("http"):
            out.append({"title": title, "url": href})
            if len(out) >= n:
                break
    return out, None

def llm(prompt, system="You are a helpful research assistant."):
    if not OPENROUTER_KEY:
        return "[no API key configured]"
    data = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": prompt}],
        "temperature": 0.3, "max_tokens": 800}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=data,
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                 "Content-Type": "application/json",
                 "HTTP-Referer": "https://rayyankhan.online"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read().decode())
        return d["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM error: {e}]"

def answer(question):
    trace = []
    results, err = ddg_search(question)
    trace.append({"tool": "ddg_search", "query": question,
                  "hits": len(results), "error": err})
    if not results:
        base = llm(question)
        return {"answer": base, "citations": [], "trace": trace,
                "note": "no search results; plain LLM fallback"}
    ctx = "\n".join(f"[{i+1}] {r['title']} ({r['url']})" for i, r in enumerate(results))
    prompt = (f"Question: {question}\n\nSearch results:\n{ctx}\n\n"
        "Answer using the search results. Cite sources inline like [1], [2]. "
        "If the results don't contain the answer, say so honestly.")
    ans = llm(prompt)
    return {"answer": ans, "citations": [r["url"] for r in results], "trace": trace}

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "What is the petrol price in Pakistan today?"
    r = answer(q)
    print(json.dumps(r, indent=2))
