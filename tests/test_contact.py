import time

import pytest

import contact
from contact import RateLimiter, is_honeypot, validate


class TestValidate:
    def test_accepts_a_good_payload_and_trims_whitespace(self):
        cleaned, errors = validate(
            {"name": "  Iris  ", "email": " iris@example.com ", "message": "  Your triage demo works.  "}
        )
        assert errors == []
        assert cleaned == {
            "name": "Iris",
            "email": "iris@example.com",
            "message": "Your triage demo works.",
        }

    def test_rejects_a_payload_with_nothing_in_it(self):
        _, errors = validate({})
        assert "name is required" in errors
        assert "email is required" in errors
        assert "message is required" in errors

    def test_rejects_whitespace_only_fields(self):
        _, errors = validate({"name": "   ", "email": "   ", "message": "   "})
        assert "name is required" in errors
        assert "email is required" in errors
        assert "message is required" in errors

    @pytest.mark.parametrize("bad", ["not-an-email", "missing@tld", "@example.com", "a b@example.com"])
    def test_rejects_malformed_emails(self, bad):
        _, errors = validate({"name": "Iris", "email": bad, "message": "hello there friend"})
        assert errors == ["that email address does not look right"]

    def test_rejects_an_over_long_email(self):
        _, errors = validate({"name": "Iris", "email": f"{'a' * 250}@example.com", "message": "hello there friend"})
        assert errors == ["that email address does not look right"]

    def test_rejects_a_too_short_message(self):
        _, errors = validate({"name": "Iris", "email": "iris@example.com", "message": "hi"})
        assert errors == ["please write at least 10 characters"]

    def test_rejects_a_too_long_message(self):
        _, errors = validate({"name": "Iris", "email": "iris@example.com", "message": "x" * 5001})
        assert errors == ["please keep it under 5000 characters"]

    def test_rejects_an_over_long_name(self):
        _, errors = validate({"name": "n" * 101, "email": "iris@example.com", "message": "hello there friend"})
        assert errors == ["please keep your name under 100 characters"]

    def test_rejects_a_non_object_body(self):
        _, errors = validate(["not", "an", "object"])
        assert errors == ["could not read that submission"]

    def test_never_echoes_the_submitted_content_back_in_errors(self):
        _, errors = validate({"name": "Iris", "email": "bad", "message": "a secret plan"})
        assert not any("secret plan" in e for e in errors)


class TestHoneypot:
    def test_empty_honeypot_field_is_a_real_person(self):
        assert is_honeypot({"name": "Iris", "email": "i@e.com", "message": "hello there friend"}) is False

    def test_filled_honeypot_field_is_a_bot(self):
        assert is_honeypot({"name": "Iris", "email": "i@e.com", "message": "x", "website": "http://spam"}) is True


class TestRateLimiter:
    def test_allows_up_to_the_limit_then_blocks(self):
        limiter = RateLimiter(limit=3, window_seconds=60)
        assert [limiter.allow("1.2.3.4") for _ in range(3)] == [True, True, True]
        assert limiter.allow("1.2.3.4") is False

    def test_counts_per_key_not_globally(self):
        limiter = RateLimiter(limit=1, window_seconds=60)
        assert limiter.allow("1.1.1.1") is True
        assert limiter.allow("2.2.2.2") is True
        assert limiter.allow("1.1.1.1") is False

    def test_forgets_hits_once_the_window_passes(self):
        limiter = RateLimiter(limit=1, window_seconds=0.05)
        assert limiter.allow("1.2.3.4") is True
        assert limiter.allow("1.2.3.4") is False
        time.sleep(0.08)
        assert limiter.allow("1.2.3.4") is True


@pytest.fixture
def client(monkeypatch):
    import app as app_module

    app_module.app.config.update(TESTING=True, CONTACT_WEBHOOK="https://example.invalid/hook")
    contact.RATE_LIMITER.reset()
    return app_module.app.test_client()


@pytest.fixture
def sent(monkeypatch):
    calls = []

    def fake_deliver(url, payload, timeout):
        calls.append((url, payload))
        return 200

    monkeypatch.setattr(contact, "deliver", fake_deliver)
    return calls


class TestContactEndpoint:
    def test_a_valid_submission_is_delivered_and_acknowledged(self, client, sent):
        response = client.post(
            "/api/contact",
            json={"name": "Iris", "email": "iris@example.com", "message": "Your triage demo works."},
        )
        assert response.status_code == 200
        assert response.get_json() == {"ok": True}
        assert len(sent) == 1
        assert sent[0][1]["email"] == "iris@example.com"

    def test_a_bot_filling_the_honeypot_is_answered_without_being_sent(self, client, sent):
        response = client.post(
            "/api/contact",
            json={
                "name": "Bot",
                "email": "bot@spam.example",
                "message": "buy cheap backlinks now",
                "website": "http://spam.example",
            },
        )
        assert response.status_code == 200
        assert response.get_json() == {"ok": True}
        assert sent == []

    def test_an_invalid_submission_is_rejected_with_readable_reasons(self, client, sent):
        response = client.post("/api/contact", json={"name": "", "email": "nope", "message": "hi"})
        assert response.status_code == 400
        body = response.get_json()
        assert body["ok"] is False
        assert "that email address does not look right" in body["errors"]
        assert sent == []

    def test_it_never_claims_success_when_no_webhook_is_configured(self, client, monkeypatch):
        import app as app_module

        monkeypatch.setitem(app_module.app.config, "CONTACT_WEBHOOK", "")
        response = client.post(
            "/api/contact",
            json={"name": "Iris", "email": "iris@example.com", "message": "Your triage demo works."},
        )
        assert response.status_code == 503
        assert response.get_json() == {"ok": False, "errors": ["the contact form is not switched on yet"]}

    def test_it_reports_a_delivery_failure_instead_of_pretending(self, client, monkeypatch):
        monkeypatch.setattr(contact, "deliver", lambda url, payload, timeout: 500)
        response = client.post(
            "/api/contact",
            json={"name": "Iris", "email": "iris@example.com", "message": "Your triage demo works."},
        )
        assert response.status_code == 502
        assert response.get_json() == {
            "ok": False,
            "errors": ["that did not reach me, please email me directly"],
        }

    def test_it_reports_an_unreachable_webhook_instead_of_pretending(self, client, monkeypatch):
        def explode(url, payload, timeout):
            raise contact.WebhookUnreachable("dns went away")

        monkeypatch.setattr(contact, "deliver", explode)
        response = client.post(
            "/api/contact",
            json={"name": "Iris", "email": "iris@example.com", "message": "Your triage demo works."},
        )
        assert response.status_code == 502

    def test_it_throttles_a_human_who_double_submits_fast(self, client, sent, monkeypatch):
        monkeypatch.setitem(client.application.config, "CONTACT_RATE_LIMIT", 2)
        contact.RATE_LIMITER.reset()
        body = {"name": "Iris", "email": "iris@example.com", "message": "Your triage demo works."}
        assert client.post("/api/contact", json=body).status_code == 200
        assert client.post("/api/contact", json=body).status_code == 200
        third = client.post("/api/contact", json=body)
        assert third.status_code == 429
        assert third.get_json() == {"ok": False, "errors": ["too many messages from that address, try again later"]}
        assert len(sent) == 2

    def test_it_ignores_a_body_that_is_not_json(self, client):
        response = client.post("/api/contact", data="name=Iris", content_type="text/plain")
        assert response.status_code == 400