import email
from email import policy
from email.parser import BytesParser
from email.header import decode_header
from bs4 import BeautifulSoup

class EmailParseError(Exception):
    """Custom exception for email parsing failures."""
    pass

def decode_header_value(header_val) -> str:
    """Decode encoded headers like Subject or From safely."""
    if not header_val:
        return ""
    try:
        decoded_list = decode_header(str(header_val))
        parts = []
        for content, encoding in decoded_list:
            if isinstance(content, bytes):
                enc = encoding or 'utf-8'
                try:
                    parts.append(content.decode(enc, errors='replace'))
                except Exception:
                    parts.append(content.decode('latin1', errors='replace'))
            else:
                parts.append(str(content))
        return " ".join(parts).strip()
    except Exception:
        return str(header_val).strip()

def extract_body_from_msg(msg) -> str:
    """
    Extract readable body text from email message.
    Prefers text/plain. If only text/html exists, extract text using BeautifulSoup.
    Ignores non-text attachments.
    """
    plain_text_parts = []
    html_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            # Skip attachments
            content_disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in content_disposition:
                continue

            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        plain_text_parts.append(payload.decode(charset, errors='replace'))
                except Exception:
                    pass
            elif content_type == "text/html":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        html_parts.append(payload.decode(charset, errors='replace'))
                except Exception:
                    pass
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                decoded_str = payload.decode(charset, errors='replace')
                if content_type == "text/html":
                    html_parts.append(decoded_str)
                else:
                    plain_text_parts.append(decoded_str)
        except Exception:
            # Fallback if get_payload decode=True fails
            raw_payload = msg.get_payload()
            if isinstance(raw_payload, str):
                plain_text_parts.append(raw_payload)

    # Prefer plain text if available
    if plain_text_parts:
        return "\n".join(plain_text_parts).strip()
    elif html_parts:
        # Extract plain text from HTML
        full_html = "\n".join(html_parts)
        try:
            soup = BeautifulSoup(full_html, "html.parser")
            return soup.get_text(separator=' ').strip()
        except Exception:
            return full_html.strip()

    return ""

def parse_eml_bytes(raw_bytes: bytes, filename: str = "email.eml") -> dict:
    """
    Parse .eml binary contents.
    Returns dict:
    {
        "filename": filename,
        "subject": subject,
        "body": body_text,
        "combined_text": combined_text
    }
    """
    if not raw_bytes or len(raw_bytes.strip()) == 0:
        raise EmailParseError("Uploaded file is empty.")

    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    except Exception as e:
        raise EmailParseError(f"Failed to parse MIME structure: {str(e)}")

    subject_raw = msg.get('subject', '')
    subject = decode_header_value(subject_raw) if subject_raw else "(No Subject)"
    
    body = extract_body_from_msg(msg)

    combined_text = f"{subject} {body}".strip()

    return {
        "filename": filename,
        "subject": subject if subject else "(No Subject)",
        "body": body,
        "combined_text": combined_text
    }
