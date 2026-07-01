#!/usr/bin/env python3
"""
Build a short visual-direction prototype for the ADVNTR Road guide system.
This intentionally writes a separate PDF and does not modify the production guide.
"""

import base64
from pathlib import Path

from weasyprint import HTML


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "mount-rainier-np-visual-prototype.pdf"
HTML_OUTPUT = ROOT / "output" / "mount-rainier-np-visual-prototype.html"
ASSETS = ROOT / "guides" / "mount-rainier-np" / "assets"
FONTS = ROOT / "design_system" / "fonts"


def font_face(name, path, weight="400", style="normal"):
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"""
@font-face {{
  font-family: '{name}';
  src: url('data:font/truetype;base64,{data}') format('truetype');
  font-style: {style};
  font-weight: {weight};
}}
"""


def image_uri(path):
    suffix = path.suffix.lower().replace(".", "")
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{suffix};base64,{data}"


def build_html():
    fonts = "\n".join(
        [
            font_face("Inter Proto", FONTS / "Inter/static/Inter_18pt-Regular.ttf", "400"),
            font_face("Inter Proto", FONTS / "Inter/static/Inter_18pt-Bold.ttf", "700"),
            font_face("Inter Proto", FONTS / "Inter/static/Inter_18pt-Black.ttf", "900"),
            font_face("Playfair Proto", FONTS / "Playfair_Display/static/PlayfairDisplay-Bold.ttf", "700"),
            font_face("Playfair Proto", FONTS / "Playfair_Display/static/PlayfairDisplay-Italic.ttf", "400", "italic"),
            font_face("Space Proto", FONTS / "Space_Mono/SpaceMono-Regular.ttf", "400"),
            font_face("Space Proto", FONTS / "Space_Mono/SpaceMono-Bold.ttf", "700"),
        ]
    )

    cover = image_uri(ASSETS / "cover-map.png")
    paradise = image_uri(ASSETS / "paradise-wildflowers.jpg")
    narada = image_uri(ASSETS / "narada-falls.jpg")
    reflection = image_uri(ASSETS / "reflection-lake.jpg")
    emmons = image_uri(ASSETS / "emmons-vista.jpg")

    css = f"""
{fonts}
@page {{ size: letter; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #111; color: #123c30; font-family: 'Inter Proto', sans-serif; }}
.page {{ width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; background: #f6e4c5; }}
.grain::after {{
  content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .16;
  background-image:
    radial-gradient(circle at 18% 22%, rgba(255,255,255,.7) 0 1px, transparent 1.6px),
    radial-gradient(circle at 72% 64%, rgba(0,0,0,.38) 0 1px, transparent 1.8px);
  background-size: 12px 11px, 15px 14px; mix-blend-mode: multiply;
}}
.photo {{ position: absolute; object-fit: cover; }}
.kicker {{ font-family: 'Space Proto', monospace; font-size: 10px; letter-spacing: .22em; text-transform: uppercase; }}
.tiny {{ font-family: 'Space Proto', monospace; font-size: 8.5px; letter-spacing: .16em; text-transform: uppercase; line-height: 1.55; }}
.massive {{ font-family: 'Inter Proto', sans-serif; font-weight: 900; letter-spacing: -.07em; line-height: .78; text-transform: uppercase; }}
.display {{ font-family: 'Playfair Proto', serif; font-weight: 700; line-height: .95; }}
.italic {{ font-family: 'Playfair Proto', serif; font-style: italic; }}
.bar {{ position: absolute; background: #ff6a21; }}
.blue {{ color: #407faa; }}
.cream {{ color: #f6e4c5; }}
.dark {{ color: #123c30; }}
.paper {{ background: rgba(255, 248, 236, .92); border: 1px solid rgba(18,60,48,.18); }}
.rule {{ height: 1px; background: rgba(18,60,48,.28); }}
.barcode {{ display: flex; gap: 4px; height: 28px; align-items: stretch; }}
.barcode i {{ display: block; width: var(--w); background: currentColor; }}
.star {{ position: absolute; width: 42px; height: 42px; }}
.star::before, .star::after {{ content: ""; position: absolute; left: 19px; top: 0; width: 4px; height: 42px; background: currentColor; border-radius: 8px; }}
.star::after {{ transform: rotate(90deg); }}
.ring {{ position: absolute; border: 1.5px solid currentColor; border-radius: 999px; opacity: .55; }}
.meta-row {{ position: absolute; left: .55in; right: .55in; top: .48in; display: grid; grid-template-columns: repeat(5,1fr); gap: 22px; color: #1d332e; }}
.meta-row b {{ display: block; font-size: 14px; margin-bottom: 4px; }}
.meta-row span {{ font-size: 10px; }}
.label-block {{ border: 1px solid currentColor; padding: 10px 12px; font-family: 'Space Proto', monospace; font-size: 10px; letter-spacing: .12em; text-transform: uppercase; line-height: 1.45; }}
.note {{ padding: 18px 20px; border-left: 6px solid #ff6a21; background: rgba(255,248,236,.91); box-shadow: 0 8px 24px rgba(18,60,48,.08); }}
.note h3 {{ margin: 0 0 8px; font: 900 18px/1 'Inter Proto'; text-transform: uppercase; }}
.note p {{ margin: 0; font-size: 13px; line-height: 1.55; }}
.footer {{ position: absolute; left: .55in; right: .55in; bottom: .38in; display: flex; justify-content: space-between; color: rgba(18,60,48,.58); border-top: 1px solid rgba(18,60,48,.18); padding-top: 9px; }}

/* Page 1 */
.poster .hero {{ inset: 0; width: 100%; height: 100%; filter: saturate(.9) contrast(1.04); }}
.poster .wash {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,32,39,.18), rgba(8,32,39,.78)); }}
.poster .title {{ position: absolute; left: .42in; top: 1.48in; font-size: 136px; color: rgba(246,228,197,.43); }}
.poster .title span {{ display: block; }}
.poster .brand {{ position: absolute; left: .56in; top: .48in; color: #f6e4c5; }}
.poster .subtitle {{ position: absolute; left: .6in; right: .8in; bottom: 1.28in; color: #f6e4c5; font-size: 34px; }}
.poster .facts {{ position: absolute; right: .55in; top: .52in; color: rgba(246,228,197,.75); text-align: right; }}
.poster .coords {{ position: absolute; left: .6in; bottom: .55in; color: rgba(246,228,197,.72); }}
.poster .barcode {{ position: absolute; right: .62in; bottom: .58in; color: rgba(246,228,197,.74); }}

/* Page 2 */
.opener {{ background: #f7eee2; }}
.opener .top-photo {{ left: .48in; right: .48in; top: .45in; width: 7.54in; height: 4.45in; border-radius: 26px; }}
.opener .word {{ position: absolute; left: .4in; top: 2.72in; font-size: 122px; color: rgba(255,255,255,.84); mix-blend-mode: screen; }}
.opener .orange-sun {{ position:absolute; right: .55in; top: 4.66in; width: 230px; height: 230px; background: #ff7a1a; clip-path: polygon(50% 0%,58% 32%,82% 8%,68% 42%,100% 38%,70% 54%,96% 70%,64% 64%,72% 100%,50% 70%,28% 100%,36% 64%,4% 70%,30% 54%,0% 38%,32% 42%,18% 8%,42% 32%); }}
.opener .copy {{ position: absolute; left: .58in; top: 5.55in; width: 3.2in; font-size: 20px; line-height: 1.08; text-transform: uppercase; letter-spacing: .01em; }}
.opener .side {{ position: absolute; right: .52in; top: 5.36in; width: 1.48in; }}
.opener .data {{ position: absolute; left: .58in; right: .58in; bottom: 1.06in; display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }}

/* Page 3 */
.data-page {{ background: #17483b; color: #f6e4c5; }}
.data-page .big {{ position:absolute; left:-.18in; top:.72in; font-size:118px; color: rgba(246,228,197,.14); }}
.data-page .photo-a {{ right:0; top:0; width:4.45in; height:6.08in; clip-path: polygon(18% 0,100% 0,100% 100%,0 88%); filter: grayscale(.08) contrast(1.08); }}
.data-page .panel {{ position:absolute; left:.55in; top:1.1in; width:3.55in; }}
.data-page .steps {{ position:absolute; left:.55in; bottom:.8in; width:7.35in; display:grid; grid-template-columns: repeat(3,1fr); gap: 18px; }}
.step {{ border-top: 1px solid rgba(246,228,197,.52); padding-top: 14px; }}
.step b {{ font-size: 48px; color:#ff6a21; line-height:.8; }}
.step p {{ margin: 8px 0 0; font-size: 12.5px; line-height: 1.5; }}

/* Page 4 */
.closure {{ background:#f6e4c5; }}
.closure .left {{ position:absolute; left:0; top:0; bottom:0; width:2.35in; background:#101c22; color:#f6e4c5; padding:.55in .38in; }}
.closure .photo-b {{ right:0; top:0; width:6.4in; height:11in; filter: grayscale(.32) contrast(1.12) brightness(.82); }}
.closure .veil {{ position:absolute; right:0; top:0; width:6.4in; height:11in; background:linear-gradient(90deg, rgba(246,228,197,.98) 0 21%, rgba(246,228,197,.48) 47%, rgba(16,28,34,.72)); }}
.closure .word {{ position:absolute; left:2.02in; top:.95in; font-size:92px; color:rgba(255,106,33,.2); writing-mode:vertical-rl; transform: rotate(180deg); }}
.closure .warning {{ position:absolute; left:2.68in; top:.95in; right:.58in; padding:24px 28px 26px; background:rgba(255,248,236,.88); border-left:7px solid #ff6a21; box-shadow:0 18px 46px rgba(16,28,34,.18); }}
.closure .warning h2 {{ margin:0; font-size:58px; line-height:.9; }}
.closure .warning p {{ font-size:15px; line-height:1.55; max-width:4.2in; }}
.closure .tickets {{ position:absolute; left:2.72in; right:.58in; bottom:.95in; display:grid; grid-template-columns: 1fr 1fr; gap:16px; }}

/* Page 5 */
.checklist {{ background:#f7eee2; }}
.checklist .blue-band {{ position:absolute; left:0; top:0; width:3.4in; height:11in; background:#4d83aa; }}
.checklist .big {{ position:absolute; left:.28in; top:.75in; font-size:86px; color:rgba(247,238,226,.45); writing-mode:vertical-rl; transform:rotate(180deg); }}
.checklist .photo-c {{ right:.5in; top:.58in; width:4.65in; height:3.1in; border-radius: 4px; filter:saturate(.85); }}
.checklist .main {{ position:absolute; left:3.75in; right:.55in; top:4.05in; }}
.checklist h2 {{ margin:0 0 10px; font-size:42px; }}
.checklist ul {{ list-style:none; padding:0; margin:22px 0 0; }}
.checklist li {{ position:relative; padding: 0 0 16px 28px; font-size:14px; line-height:1.45; }}
.checklist li::before {{ content:""; position:absolute; left:0; top:3px; width:13px; height:13px; border:2px solid #ff6a21; }}
.checklist .mini {{ position:absolute; left:.55in; bottom:.65in; width:2.4in; color:#f6e4c5; }}
"""

    bars = "".join(f'<i style="--w:{w}px"></i>' for w in [2, 5, 2, 9, 3, 4, 2, 7, 2, 11, 3, 5, 2])

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>{css}</style></head><body>
<section class="page poster grain">
  <img class="photo hero" src="{cover}">
  <div class="wash"></div>
  <div class="brand kicker">ADVNTR ROAD / FIELD EDITION</div>
  <div class="facts tiny">PACIFIC NORTHWEST<br>14,411 FT<br>46.8523 N / 121.7603 W</div>
  <div class="massive title"><span>MOUNT</span><span>RAINIER</span></div>
  <div class="subtitle italic">The mountain that owns the sky above everything.</div>
  <div class="coords tiny">NO TIMED ENTRY / OFFLINE FIRST / BIG-RIG ROUTING MATTERS</div>
  <div class="barcode">{bars}</div>
</section>

<section class="page opener grain">
  <img class="photo top-photo" src="{paradise}">
  <div class="massive word">PARADISE</div>
  <div class="orange-sun"></div>
  <div class="kicker" style="position:absolute;left:.58in;top:.52in;color:#f7eee2;">SECTION 01 / ORIENTATION</div>
  <div class="copy">Two open road corridors, one closed northwest sector, and a mountain that sets the terms.</div>
  <div class="side label-block">Arrive before 7 AM or after 4 PM. Clear summer weekends fill fast.</div>
  <div class="data">
    <div class="note"><h3>No timed entry</h3><p>Reservations are gone for 2026. Parking friction is back.</p></div>
    <div class="note"><h3>Offline first</h3><p>Download maps before the gate. Cell service is mostly absent.</p></div>
    <div class="note"><h3>Two corridors</h3><p>Paradise for classic first-timers. Sunrise for higher, quieter alpine access.</p></div>
  </div>
  <div class="footer tiny"><span>MOUNT RAINIER NATIONAL PARK</span><span>VISUAL PROTOTYPE / 02</span></div>
</section>

<section class="page data-page grain">
  <img class="photo photo-a" src="{emmons}">
  <div class="massive big">CAMP</div>
  <div class="panel">
    <div class="kicker" style="color:#ffad69;margin-bottom:18px;">RIG-SIZE REALITY</div>
    <div class="display" style="font-size:46px;">Camp by what you drive, not what looks close on a map.</div>
    <p style="font-size:15px;line-height:1.55;margin-top:18px;">Rainier rewards smaller rigs inside the park. Larger setups should base outside the gate, unhook, and commute in with less drama.</p>
  </div>
  <div class="steps">
    <div class="step"><b>01</b><p><strong>Under 24 ft:</strong> White River becomes realistic, but narrow loops still demand patience.</p></div>
    <div class="step"><b>02</b><p><strong>Under 30 ft:</strong> Cougar Rock is the interior play, with no dump or water fill in 2026.</p></div>
    <div class="step"><b>03</b><p><strong>Over 30 ft:</strong> Packwood is the honest answer. Full hookups beat forcing the park.</p></div>
  </div>
  <div class="footer tiny" style="color:rgba(246,228,197,.6);"><span>MOUNT RAINIER NATIONAL PARK</span><span>VISUAL PROTOTYPE / 03</span></div>
</section>

<section class="page closure grain">
  <img class="photo photo-b" src="{narada}">
  <div class="veil"></div>
  <div class="left">
    <div class="kicker" style="color:#ff6a21;">FIELD WARNING</div>
    <div class="barcode" style="color:#f6e4c5;margin-top:34px;">{bars}</div>
    <div class="tiny" style="position:absolute;bottom:.6in;left:.38in;right:.38in;">SR-165 / FAIRFAX BRIDGE / NORTHWEST SECTOR</div>
  </div>
  <div class="massive word">NO ROUTE</div>
  <div class="warning">
    <div class="bar" style="width:2.9in;height:.22in;top:-.28in;left:0;"></div>
    <h2 class="display">Ignore the private bypass.</h2>
    <p>Some navigation apps may show a logging-road workaround near Fairfax Bridge. It is gated, private, and not open to public travel. Do not plan Carbon River, Mowich Lake, Tolmie Peak, or Spray Park by road in 2026.</p>
  </div>
  <div class="tickets">
    <div class="label-block">Closure confirmed<br>Northwest sector deferred</div>
    <div class="label-block" style="color:#8c3d2d;">Do not route<br>Do not trust auto-map detours</div>
  </div>
  <div class="footer tiny"><span>MOUNT RAINIER NATIONAL PARK</span><span>VISUAL PROTOTYPE / 04</span></div>
</section>

<section class="page checklist grain">
  <div class="blue-band"></div>
  <div class="massive big">OFFLINE</div>
  <div class="mini">
    <div class="kicker">BEFORE THE GATE</div>
    <div class="barcode" style="margin:24px 0;">{bars}</div>
    <p style="font-size:13px;line-height:1.55;">The useful guide page should feel like a field card: fast to scan, visually distinct, and hard to miss.</p>
  </div>
  <img class="photo photo-c" src="{reflection}">
  <div class="main">
    <div class="kicker blue">CHECKLIST / 2026</div>
    <h2 class="display">Do these before the mountain takes your signal.</h2>
    <ul>
      <li>Book Cougar Rock as soon as the six-month window opens.</li>
      <li>Download offline maps for the entire park and gateway towns.</li>
      <li>Confirm waste tank capacity. No park dump stations are operating.</li>
      <li>Check tunnel clearance if routing through Stevens Canyon.</li>
      <li>Pack microspikes for June or early July alpine trails.</li>
    </ul>
  </div>
  <div class="footer tiny"><span>MOUNT RAINIER NATIONAL PARK</span><span>VISUAL PROTOTYPE / 05</span></div>
</section>
</body></html>"""
    return html


def main():
    html = build_html()
    HTML_OUTPUT.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(OUTPUT))
    print(f"HTML written to {HTML_OUTPUT}")
    print(f"PDF written to {OUTPUT}")


if __name__ == "__main__":
    main()
