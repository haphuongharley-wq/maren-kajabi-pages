# Maren – Kajabi pages

Snapshot of six landing pages from the Kajabi site "Det lille pusterommet" (https://www.detlillepusterommet.no), exported on 2026-10-25.

Each folder under `pages/` holds `index.html`, the published page as served. Two folders also hold `theme.json`, the page's Kajabi theme settings as returned by the Kajabi MCP.

| Folder | Kajabi title | Live URL | Kajabi ID |
|---|---|---|---|
| `linker-til-instagram` | Linker til Instagram | /klikkher | 2149080890 |
| `e-book-thx-page` | E-book Thx page | /Takk-side | 2152107608 |
| `bestilling-av-bok-1` | Bestilling av bok 1 | /ut-av-utbrenthet | 2152307393 |
| `e-book` | e-book | /book-ut-av-utbrenthet | 2152199251 |
| `takk-etter-kjop-av-ut-av-utbrenthet` | Takk etter kjøp av Ut av utbrenthet | /takk-etter-kjop-av-bok | 2151584027 |
| `pusterom-betaling-2` | Pusterom Betaling 2 | /bestillher | 2152237078 |

The other four pages have no `theme.json`. Three of them are built from one large Custom Code section (1–2.3 MB), which is over the Kajabi MCP's 200 KB read limit. Their full content is in `index.html`.

Images, fonts and scripts are still loaded from Kajabi's CDN; they are not copied into this repo.
