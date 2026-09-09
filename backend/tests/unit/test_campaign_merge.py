"""Unit tests for campaign template renderer and suppression logic."""


from app.services.campaigns.engine import is_suppressed, render_template


def test_basic_substitution():
    result = render_template("Hello {{first_name}}", {"first_name": "Alice"})
    assert result == "Hello Alice"


def test_fallback_substitution():
    result = render_template('Hello {{first_name | fallback: "there"}}', {})
    assert result == "Hello there"


def test_fallback_not_used_when_value_present():
    result = render_template('Hello {{first_name | fallback: "there"}}', {"first_name": "Bob"})
    assert result == "Hello Bob"


def test_multiple_variables():
    result = render_template(
        "Hi {{first_name}}, from {{company}}",
        {"first_name": "Carol", "company": "Acme"},
    )
    assert result == "Hi Carol, from Acme"


def test_missing_variable_empty_string():
    result = render_template("Hi {{missing}}", {})
    assert result == "Hi "


def test_suppression_by_bounce():
    assert is_suppressed("bad@example.com", {"bad@example.com"}, set()) is True


def test_suppression_by_unsubscribe():
    assert is_suppressed("opted@example.com", set(), {"opted@example.com"}) is True


def test_not_suppressed():
    assert is_suppressed("ok@example.com", set(), set()) is False


def test_suppression_case_insensitive():
    assert is_suppressed("USER@Example.COM", {"user@example.com"}, set()) is True
