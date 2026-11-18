"""Build the sales sequence after the 15 November webinar as Kajabi-ready HTML emails and a review page.

Source of truth for the copy: copy/08-webinar-sales-sequence/sequence-no.md. Edit there, fill LINKS below, then run:
    python3 build-emails.py
Outputs (next to this script): email-01.html ... email-08.html, index.html
Rendering (layout, colours, review page) is shared with emails/webinar-invite-15-11/build-emails.py.
"""
import importlib.util
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / "copy/08-webinar-sales-sequence/sequence-no.md"

_spec = importlib.util.spec_from_file_location("invite", HERE.parent / "webinar-invite-15-11/build-emails.py")
inv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inv)

# Fill before uploading to Kajabi. Empty values show a visible placeholder link.
LINKS = {
    "CHECKOUT": "https://www.detlillepusterommet.no/fra-stress-til-ro",   # the Kajabi page holding maren-checkout-page.html (not a Kajabi offer link)
    "SALGSSIDE": "https://www.detlillepusterommet.no/fra-stress-til-ro-tilbud",  # the sales page
    "OPPTAKS": "https://www.detlillepusterommet.no/opptak-webinar",    # the replay page (maren-replay-page.html)
    "STOPP": "https://www.detlillepusterommet.no/stopp-salg",      # opt-out of the sales emails only: a Kajabi link (or form page) that adds the tag stopp-salg-fsr
}
IMAGES = {"Anne Schei": "anne-schei-square.jpg", "Audhild Helgaas": "audhild-helgaas-square.jpg", "Cecilie Liland": "cecilie-liland-square.jpg"}  # served from the invite email img folder on GitHub Pages

AUDIENCE = {
    "send": "Alle som meldte seg på webinaret 15. november.",
    "exclude": [
        "Tag: aktiv coachingkunde",
        "Tag: avsluttet coachingkunde",
        "Alle som deltok på Advanced Training søndag 8. november",
    ],
    "on_label": "Ved kjøp",
    "on_register": "Får taggen kjøpt-fra-stress-til-ro og går ut av sekvensen.",
}


def url(key, n):
    base = LINKS[key] or f"https://www.detlillepusterommet.no/[{key}-LENKE]"
    sep = "&amp;" if "?" in base else "?"
    return f"{base}{sep}utm_source=epost&amp;utm_medium=email&amp;utm_campaign=salg-webinar-15-11&amp;utm_content=e{n}"


def linkify(p, n):
    """«… her: [X-LENKE]» (or «HER: …») becomes a text link on that word."""
    return re.sub(r"\b(her|HER): \[([A-ZÆØÅ]+?)-?LENKE\]", lambda m: f"[{m[1]}]({url(m[2], n).replace('&amp;', '&')})", p)


def render_block(block, n):
    """Sales emails: a full-width navy button, so the call to action stands out more than the gold one in the invites.
    The colour is also inline CSS: the Kajabi editor drops the bgcolor attribute, which left white text on white."""
    if block[0] != "btn":
        return _render_block(block, n)
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:14px 0 28px;">'
            f'<tr><td align="center" bgcolor="{inv.NAVY}" style="background-color:{inv.NAVY};border-radius:999px;border-bottom:3px solid {inv.GOLD};">'
            f'<a href="{block[2]}" target="_blank" style="display:block;background-color:{inv.NAVY};padding:20px 24px;font-family:{inv.SANS};font-size:19px;'
            f'font-weight:bold;line-height:1.3;color:#ffffff;text-decoration:none;border-radius:999px;">{inv.inline(block[1])}</a>'
            f'</td></tr></table>')


_render_block, inv.render_block = inv.render_block, render_block

FOOTER = f'<p style="margin:18px 0 0;font-family:{inv.SANS};font-size:13px;line-height:1.5;color:{inv.SLATE};">Det lille pusterommet · Maren Kvalvaag-Toven</p>'


def finish(page, n):
    """Underline text links and add the opt-out line for the sales emails above the footer."""
    page = page.replace(f'style="color:{inv.NAVY};font-weight:bold;"', f'style="color:{inv.NAVY};font-weight:bold;text-decoration:underline;"')
    stop = (f'<p style="margin:18px auto 0;max-width:520px;font-family:{inv.SANS};font-size:14px;line-height:1.6;color:{inv.SLATE};">'
            f'Vil du ikke ha flere e-poster om Fra stress til ro? <a href="{url("STOPP", n)}" target="_blank" style="color:{inv.NAVY};text-decoration:underline;">Klikk her</a>, '
            f'så stopper de. Du får fortsatt de vanlige e-postene mine.</p>\n')
    assert page.count(FOOTER) == 1
    page = page.replace(FOOTER, stop + FOOTER)
    # Keep prices like «3 × 3 497 kr» on one line (text nodes only, never attributes).
    nb = lambda t: re.sub(r"(?<=\d) (?=\d{3}\b)|(?<=\d) (?=kr\b)|(?<=\d) (?=×)|(?<=×) (?=\d)", "&nbsp;", t)
    return re.sub(r">([^<]+)<", lambda m: ">" + nb(m[1]) + "<", page)


def blocks_for(paras, n):
    out, i, photo = [], 0, None
    while i < len(paras):
        p = paras[i]
        lines = p.split("\n")
        if m := re.fullmatch(r"\[KNAPP: (.+?)\] → \[([A-ZÆØÅ]+?)-?LENKE\]", p):
            out.append(("btn", m[1], url(m[2], n)))
        elif m := re.fullmatch(r"\[BILDE: (.+)\]", p):
            photo = IMAGES[m[1]]  # attached to the next quote, next to the author's name
        elif p.startswith("«"):
            # A quote may run over several paragraphs; it ends at the paragraph holding the closing », then the author line.
            parts = [p]
            while "»" not in parts[-1]:
                i += 1
                parts.append(paras[i])
            text = "<br><br>".join(parts)
            body, _, author = text.rpartition("»")
            out.append(("quote", body.lstrip("«"), author.strip() or None, photo))
            photo = None
        elif p == "Klem fra Maren":
            prev = out.pop() if out and out[-1] == ("p", "Sov godt.") else None
            out.append(("sign", ("Sov godt.<br>" if prev else "") + p))
        elif p.startswith("PS."):
            out.append(("ps", linkify(p, n)))
        elif any(l.startswith("• ") for l in lines):
            head = [l for l in lines if not l.startswith("• ")]
            if head:
                out.append(("p", "**" + " ".join(head) + "**" if not head[-1].endswith(":") else " ".join(head)))
            out.append(("ul", [l[2:] for l in lines if l.startswith("• ")]))
        elif len(lines) > 1:  # question or heading on the first line, answer below
            out.append(("p", f"**{lines[0]}**<br>" + "<br>".join(lines[1:])))
        else:
            out.append(("p", linkify(p, n)))
        i += 1
    return out


def parse():
    text = SOURCE.read_text(encoding="utf-8")
    chunks = re.split(r"\n=+\nE-POST (\d+) · (.+?)\n=+\n", text)
    emails = []
    for k in range(1, len(chunks), 3):
        n, when, body = int(chunks[k]), chunks[k + 1], chunks[k + 2]
        subject = re.search(r"^Emne: (.+)$", body, re.M)[1]
        pre = re.search(r"^Forhåndstekst: (.+)$", body, re.M)[1]
        rest = body.split(f"Forhåndstekst: {pre}", 1)[1]
        paras = [p.strip() for p in re.split(r"\n\s*\n", rest) if p.strip()]
        emails.append({"send": when.replace(" · ", ", "), "subject": subject, "preheader": pre, "blocks": blocks_for(paras, n)})
        assert len(emails) == n, f"email numbering breaks at {n}"
    return emails


def paste_page(emails, out):
    """Local helper for the team: one card per email with copy buttons for subject, preview text and HTML."""
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    cards = []
    for n, e in enumerate(emails, 1):
        h = re.search(r"(\d+) timer?(?: (\d+) min)? etter webinarstart", e["send"])
        # Kajabi takes whole numbers only, so a half hour goes in as minutes
        after = f"{int(h[1]) * 60 + int(h[2])} minutes" if h[2] else f"{h[1]} hours"
        html = (out / f"email-{n:02d}.html").read_text(encoding="utf-8")
        cards.append(f'''<section><h2>Email {n} <span>After the event: <b>{after}</b> · {esc(e["send"].split(",")[0])}</span></h2>
<label>Subject</label><div class="row"><input readonly value="{esc(e["subject"])}"><button data-c>Copy</button></div>
<label>HTML (paste into a Custom code / HTML block)</label><div class="row"><textarea readonly>{esc(html)}</textarea><button data-c>Copy</button></div>
<details><summary>Preview</summary><iframe srcdoc="{esc(html)}" loading="lazy"></iframe></details></section>''')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Paste into Kajabi · sales emails</title><style>
body{margin:0;background:#FAF9F6;color:#1f2a3d;font:15px/1.5 Inter,system-ui,sans-serif}main{max-width:860px;margin:0 auto;padding:32px 16px 80px}
h1{font-size:1.5rem;margin:0 0 8px}.note{background:#fff;border-left:3px solid #AB9461;padding:10px 14px;margin:0 0 24px}
section{background:#fff;border:1px solid #EDE7DB;border-radius:16px;padding:18px;margin:0 0 16px}h2{font-size:1.1rem;margin:0 0 10px}h2 span{font-weight:400;color:#5d6a82;font-size:.9rem}
label{display:block;font-size:.8rem;font-weight:600;color:#5d6a82;margin:10px 0 4px}.row{display:flex;gap:8px}
input,textarea{flex:1;min-width:0;font:13px/1.4 ui-monospace,Menlo,monospace;border:1px solid #EDE7DB;border-radius:8px;padding:8px}textarea{height:70px}
button{min-width:88px;min-height:40px;border:0;border-radius:999px;background:#274472;color:#fff;font-weight:600;cursor:pointer}button.ok{background:#2f6b45}
iframe{width:100%;height:640px;border:1px solid #EDE7DB;border-radius:8px;margin-top:8px}summary{cursor:pointer;margin-top:10px;color:#274472;font-weight:600}
</style></head><body><main><h1>Sales emails: paste into the Kajabi event</h1>
<p class="note">Event «New Live Wbn - 15.11.2026» → Emails → add email → timing «After the event». The offsets below count from the webinar <b>start</b> (Sunday 10:00).
If Kajabi counts «after the event» from the event's <b>end</b> time, subtract the event length (for a 1 h 30 min event, email 1 goes at 30 minutes). Kajabi takes whole numbers only, so email 3 is in minutes.
In each email, also give the «Klikk her» link the action «add tag stopp-salg-fsr».</p>
''' + "\n".join(cards) + '''
</main><script>document.querySelectorAll('[data-c]').forEach(function(b){b.onclick=function(){var f=b.previousElementSibling;navigator.clipboard.writeText(f.value).then(function(){b.textContent='Copied';b.classList.add('ok');setTimeout(function(){b.textContent='Copy';b.classList.remove('ok')},1500)})}})</script></body></html>
'''


def main():
    emails = parse()
    for n, e in enumerate(emails, 1):
        (HERE / f"email-{n:02d}.html").write_text(finish(inv.render_email(e, n), n), encoding="utf-8")
    (HERE / "index.html").write_text(inv.render_index(
        emails, AUDIENCE, title="Salgssekvens etter webinaret",
        heading="Salgssekvens etter webinaret hver søndag",
        lead="Åtte e-poster fra søndag til onsdag etter hvert webinar, alle til alle påmeldte. De ligger i det gjentakende eventet med tid etter webinarstart. Opptaket sendes søndag kl. 20.00 i e-post 2. E-post 1 og 3 går til checkout, e-post 4 til 8 til salgssiden."),
        encoding="utf-8")
    # Self-check: Maren's rules and one button per email.
    for n, e in enumerate(emails, 1):
        text = " ".join(x for b in e["blocks"] for v in b[1:2] for x in (v if isinstance(v, list) else [v])) + e["subject"] + e["preheader"]
        assert "—" not in text and "–" not in text, f"long dash in email {n}"
        assert sum(b[0] == "btn" for b in e["blocks"]) == 1, f"email {n} must have one button"
        assert e["blocks"][-1][0] in ("sign", "ps") and any(b[0] == "sign" and b[1].endswith("Klem fra Maren") for b in e["blocks"]), f"email {n} must end with Klem fra Maren"
        assert "[" not in re.sub(r"\[\w+-LENKE\]|\[(?:her|HER)\]|\[Fornavn\]", "", text), f"unfilled placeholder in email {n}"
    # Paste-ready Kajabi snippets: only the START..END block, with Kajabi's first-name merge tag.
    out = HERE / "kajabi"
    out.mkdir(exist_ok=True)
    for n in range(1, len(emails) + 1):
        page = (HERE / f"email-{n:02d}.html").read_text(encoding="utf-8")
        snippet = page.split("<!-- START -->", 1)[1].split("<!-- END -->", 1)[0].strip()
        # Kajabi's editor turns the hidden preheader into a visible paragraph, and event emails have no preview text field.
        if snippet.startswith('<div style="display:none;'):
            snippet = snippet.split("</div>", 1)[1].lstrip()
        (out / f"email-{n:02d}.html").write_text(snippet.replace("[Fornavn]", "{{ first_name }}") + "\n", encoding="utf-8")
    (out / "index.html").write_text(paste_page(emails, out), encoding="utf-8")
    missing = [k for k, v in LINKS.items() if not v]
    print(f"built {len(emails)} emails and index.html" + (f"; links still empty: {', '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
