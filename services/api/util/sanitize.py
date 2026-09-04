import re
from html import escape as _html_escape

SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def escape_html(value):
    return _html_escape(str(value), quote=True)


def is_safe_filename(name):
    return bool(SAFE_FILENAME.match(name or ""))


def normalise_currency(code):
    code = (code or "").strip().upper()
    return code if re.match(r"^[A-Z]{3}$", code) else "SGD"

def normalise_reference(ref):
    """Trim and cap merchant-supplied reference strings for display use."""
    return (ref or "").strip()[:64]