"""BYU CAS authentication helpers."""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

CAS_BASE = "https://cas.byu.edu/cas"


def cas_login_url(service_url: str) -> str:
    """Return the CAS login URL that redirects back to service_url after login."""
    return f"{CAS_BASE}/login?{urlencode({'service': service_url})}"


def cas_validate_ticket(ticket: str, service_url: str) -> dict | None:
    """
    Validate a CAS service ticket via the CAS 3.0 serviceValidate endpoint.

    Returns {'user': netid, 'attributes': {...}} on success, None on failure.
    """
    resp = requests.get(
        f"{CAS_BASE}/serviceValidate",
        params={"ticket": ticket, "service": service_url},
        timeout=10,
    )
    resp.raise_for_status()

    ns = "http://www.yale.edu/tp/cas"
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        return None

    success = root.find(f".//{{{ns}}}authenticationSuccess")
    if success is None:
        return None

    user = success.findtext(f"{{{ns}}}user")
    attrs: dict = {}
    attr_el = success.find(f"{{{ns}}}attributes")
    if attr_el is not None:
        for child in attr_el:
            tag = child.tag.replace(f"{{{ns}}}", "")
            attrs[tag] = child.text

    return {"user": user, "attributes": attrs}
