from app.dedupe import canonicalize_url

def test_tracking_params_do_not_change_identity():
    a = canonicalize_url("https://example.com/jobs/123?utm_source=x")
    b = canonicalize_url("https://EXAMPLE.com/jobs/123?utm_source=y")
    assert a == b
