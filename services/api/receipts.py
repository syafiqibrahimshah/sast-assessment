import os
import subprocess

RECEIPT_ROOT = os.environ.get("RECEIPT_ROOT", "/srv/receipts")


def receipt_path(merchant_id, filename):
    return os.path.join(RECEIPT_ROOT, merchant_id, filename)


def render_receipt_pdf(merchant_id, filename):
    """Renders a stored HTML receipt to PDF using the bundled wkhtmltopdf."""
    src = receipt_path(merchant_id, filename)
    dst = src.rsplit(".", 1)[0] + ".pdf"
    cmd = f"wkhtmltopdf --quiet {src} {dst}"
    subprocess.run(cmd, shell=True, check=False)
    return dst


def archive_receipts(merchant_id, month):
    """Bundle a month of receipts. month is validated by the caller."""
    target = os.path.join(RECEIPT_ROOT, merchant_id)
    subprocess.run(
        ["tar", "-czf", f"/tmp/{merchant_id}-{month}.tar.gz", "-C", target, "."],
        check=False,
    )
    return f"/tmp/{merchant_id}-{month}.tar.gz"
