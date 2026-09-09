"""Safe mail-merge template renderer and suppression check for campaigns."""

import re


def render_template(template: str, variables: dict) -> str:
    """
    Safe template variable substitution.
    Supports {{variable}} and {{variable | fallback: "default"}}.
    Never executes arbitrary code.
    """

    def replacer(match: re.Match) -> str:
        expr = match.group(1).strip()
        if "|" in expr:
            var_name, fallback_part = expr.split("|", 1)
            var_name = var_name.strip()
            fallback_match = re.search(r'fallback:\s*["\'](.+?)["\']', fallback_part)
            fallback = fallback_match.group(1) if fallback_match else ""
            return str(variables.get(var_name, fallback))
        return str(variables.get(expr.strip(), ""))

    return re.sub(r"\{\{(.+?)\}\}", replacer, template)


def is_suppressed(email: str, bounced_emails: set, unsubscribed_emails: set) -> bool:
    """Check if email is in bounce or unsubscribe suppression lists."""
    email_lower = email.lower()
    return email_lower in bounced_emails or email_lower in unsubscribed_emails
