"""HTTP session. Uses curl_cffi (looks like real Chrome to bot checks) when installed."""

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

try:
    from curl_cffi import requests as _req

    def session():
        return _req.Session(impersonate="chrome")
except ImportError:  # plain requests works for eBay/Vinted; Depop may block it
    import requests as _req

    def session():
        s = _req.Session()
        s.headers["User-Agent"] = UA
        return s

HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
