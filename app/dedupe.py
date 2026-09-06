import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()

def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    try:
        parts = urlsplit(url.strip())
        host = parts.netloc.lower()
        path = re.sub(r"/+$", "", parts.path) or "/"
        query = ""
        return urlunsplit((parts.scheme.lower(), host, path, query, ""))
    except ValueError:
        return clean(url)

def make_fingerprint(job: dict) -> str:
    raw = "|".join([
        clean(job.get("company", "")),
        clean(job.get("title", "")),
        clean(job.get("location", "")),
        canonicalize_url(job.get("job_url", "")),
        clean(job.get("description", ""))[:1500],
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
