#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmaciasESP — Generador HTML
Fuente: export.geojson (OpenStreetMap, amenity=pharmacy)
Genera un index.html con mapa Leaflet + sidebar + clusters.
Misma estética que GlutenFreeESP.
"""

import json, os, sys
from collections import Counter

DIR       = os.path.dirname(os.path.abspath(__file__))
GEOJSON   = os.path.join(DIR, 'export.geojson')
OUTPUT    = os.path.join(DIR, 'index.html')

print("=" * 56)
print("  FARMACIAS ESP — Generador HTML")
print("=" * 56)

if not os.path.exists(GEOJSON):
    print(f"\nERROR: No se encuentra {GEOJSON}")
    sys.exit(1)

with open(GEOJSON, encoding='utf-8') as f:
    geo = json.load(f)

features = geo.get('features', [])
print(f"Registros brutos: {len(features)}")

# ── Construir lista de farmacias ───────────────────────
farmacias = []
seen = set()

CP_PROV = {
    '01':'Álava','02':'Albacete','03':'Alicante','04':'Almería','05':'Ávila',
    '06':'Badajoz','07':'Baleares','08':'Barcelona','09':'Burgos','10':'Cáceres',
    '11':'Cádiz','12':'Castellón','13':'Ciudad Real','14':'Córdoba','15':'A Coruña',
    '16':'Cuenca','17':'Girona','18':'Granada','19':'Guadalajara','20':'Guipúzcoa',
    '21':'Huelva','22':'Huesca','23':'Jaén','24':'León','25':'Lleida',
    '26':'La Rioja','27':'Lugo','28':'Madrid','29':'Málaga','30':'Murcia',
    '31':'Navarra','32':'Ourense','33':'Asturias','34':'Palencia','35':'Las Palmas',
    '36':'Pontevedra','37':'Salamanca','38':'Santa Cruz de Tenerife','39':'Cantabria',
    '40':'Segovia','41':'Sevilla','42':'Soria','43':'Tarragona','44':'Teruel',
    '45':'Toledo','46':'Valencia','47':'Valladolid','48':'Vizcaya','49':'Zamora',
    '50':'Zaragoza','51':'Ceuta','52':'Melilla',
}

for feat in features:
    p    = feat.get('properties', {})
    geom = feat.get('geometry', {})
    if geom.get('type') != 'Point':
        continue
    lon, lat = geom['coordinates']

    nombre = p.get('name') or p.get('operator') or 'Farmacia'

    # Dirección: intentar construirla
    street = p.get('addr:street', '')
    num    = p.get('addr:housenumber', '')
    cp     = p.get('addr:postcode', '')
    city   = p.get('addr:city', '') or p.get('addr:town', '') or p.get('addr:village', '')
    full   = p.get('addr:full', '')

    if full:
        direccion = full
    elif street:
        direccion = street
        if num:   direccion += ', ' + num
        if cp:    direccion += ', ' + cp
        if city:  direccion += ' ' + city
    elif city:
        direccion = city
    else:
        direccion = ''

    # Provincia desde CP
    provincia = ''
    if cp and len(cp) >= 2:
        provincia = CP_PROV.get(cp[:2], '')
    if not provincia and city:
        provincia = city

    # Teléfono
    tel = p.get('contact:phone') or p.get('phone') or ''

    # Web
    web = p.get('contact:website') or p.get('website') or ''

    # Horario
    horario = p.get('opening_hours', '')

    # Wheelchair
    wc = p.get('wheelchair', '')

    # Deduplicar por coordenada redondeada
    key = (round(lat, 4), round(lon, 4))
    if key in seen:
        continue
    seen.add(key)

    farmacias.append({
        'n':   nombre,
        'd':   direccion,
        'prov': provincia,
        'tel': tel,
        'web': web,
        'h':   horario,
        'wc':  wc,
        'lat': round(lat, 6),
        'lon': round(lon, 6),
    })

print(f"Farmacias únicas: {len(farmacias)}")

# Estadísticas
con_nombre  = sum(1 for f in farmacias if f['n'] != 'Farmacia')
con_tel     = sum(1 for f in farmacias if f['tel'])
con_horario = sum(1 for f in farmacias if f['h'])
con_prov    = sum(1 for f in farmacias if f['prov'])

print(f"Con nombre:   {con_nombre}")
print(f"Con teléfono: {con_tel}")
print(f"Con horario:  {con_horario}")
print(f"Con provincia:{con_prov}")

TOTAL = len(farmacias)

# JSON compacto para el HTML
datos_json = json.dumps(farmacias, ensure_ascii=False, separators=(',', ':'))

# ── Generar HTML ───────────────────────────────────────
html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- ═══ SEO PRIMARIO ═══ -->
<title>Mapa Farmacias España · {TOTAL:,} farmacias en toda España</title>
<meta name="description" content="Mapa interactivo con {TOTAL:,} farmacias en España. Encuentra la farmacia más cercana, con teléfono, dirección y horario. Gratis y sin registro.">
<meta name="keywords" content="farmacias españa, mapa farmacias, farmacia cerca de mi, farmacias abiertas, buscador farmacias españa, farmacia mapa interactivo">
<meta name="author" content="FarmaciasESP">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="language" content="es">
<meta name="geo.region" content="ES">
<link rel="canonical" href="https://lasendadeltiempo.github.io/farmacias/">

<!-- ═══ OPEN GRAPH ═══ -->
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="FarmaciasESP">
<meta property="og:title" content="Mapa Farmacias España · {TOTAL:,} farmacias">
<meta property="og:description" content="Encuentra la farmacia más cercana en toda España. {TOTAL:,} farmacias geolocalizadas. Gratis y sin registro.">
<meta property="og:url" content="https://lasendadeltiempo.github.io/farmacias/">
<meta property="og:image" content="https://lasendadeltiempo.github.io/farmacias/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">

<!-- ═══ TWITTER / X CARD ═══ -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Mapa Farmacias España · {TOTAL:,} farmacias">
<meta name="twitter:description" content="{TOTAL:,} farmacias geolocalizadas en España. Encuentra la más cercana con un clic.">
<meta name="twitter:image" content="https://lasendadeltiempo.github.io/farmacias/og-image.jpg">

<!-- ═══ STRUCTURED DATA ═══ -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "FarmaciasESP — Mapa de farmacias en España",
  "url": "https://lasendadeltiempo.github.io/farmacias/",
  "description": "Mapa interactivo con {TOTAL:,} farmacias en España. Gratis y sin registro.",
  "applicationCategory": "HealthApplication",
  "operatingSystem": "Any",
  "inLanguage": "es",
  "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "EUR" }}
}}
</script>

<link rel="icon" type="image/png" href="../favicon.png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<meta name="theme-color" content="#0f4c81">
<link rel="manifest" href="../manifest.json">

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
:root{{
  --blue:      #1565c0;
  --blue-d:    #0d47a1;
  --blue-l:    #e3f2fd;
  --blue-m:    #90caf9;
  --accent:    #f9a825;
  --header-h:  58px;
  --sidebar-w: 340px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;font-family:'Nunito',sans-serif;background:#f0f4f8;color:#222;overflow:hidden}}

/* ── ANIMATIONS ── */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes shimmer{{0%{{background-position:200% center}}100%{{background-position:-200% center}}}}
@keyframes floatDot{{0%,100%{{transform:translateY(0) scale(1)}}50%{{transform:translateY(-6px) scale(1.08)}}}}
@keyframes pulse-ring{{0%{{box-shadow:0 0 0 0 rgba(21,101,192,.4)}}70%{{box-shadow:0 0 0 10px rgba(21,101,192,0)}}100%{{box-shadow:0 0 0 0 rgba(21,101,192,0)}}}}

/* ── LANDING ── */
#landing{{
  position:fixed;inset:0;z-index:1000;
  background: radial-gradient(ellipse at 20% 0%, #bbdefb 0%, transparent 55%),
              radial-gradient(ellipse at 80% 100%, #c5cae9 0%, transparent 50%),
              #eef2f7;
  display:flex;flex-direction:column;align-items:center;justify-content:flex-start;
  padding:0 2rem 2rem;text-align:center;transition:opacity .6s ease;
  overflow-y:auto;scroll-behavior:smooth;
}}
#landing::before{{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image: radial-gradient(circle, rgba(21,101,192,.06) 1px, transparent 1px);
  background-size: 28px 28px;
}}
#landing > *{{position:relative;z-index:1;}}
#landing.hide{{opacity:0;pointer-events:none}}

/* ── NAV LANDING ── */
.l-nav{{
  position:sticky;top:0;z-index:10;width:100%;
  background:rgba(238,242,247,0.92);backdrop-filter:blur(10px);
  border-bottom:1px solid rgba(21,101,192,.1);
  animation: fadeIn .4s ease both;
}}
.l-nav-inner{{
  max-width:960px;margin:0 auto;padding:10px 20px;
  display:flex;align-items:center;gap:16px;
}}
.l-nav-brand{{
  font-family:'Playfair Display',serif;font-size:20px;
  color:var(--blue-d);text-decoration:none;
  display:flex;align-items:center;gap:8px;
}}
.l-nav-fx{{color:var(--accent);}}
.l-nav-links{{display:flex;gap:4px;margin-left:auto;align-items:center;flex-wrap:wrap;}}
.l-nav-link{{
  font-size:13px;color:#444;text-decoration:none;padding:5px 10px;
  border-radius:8px;transition:background .15s,color .15s;
}}
.l-nav-link:hover{{background:rgba(21,101,192,.08);color:var(--blue-d);}}
.l-nav-cta{{
  background:var(--blue);color:white;border:none;
  padding:7px 16px;border-radius:20px;font-size:13px;font-weight:700;
  cursor:pointer;transition:background .15s,transform .15s;
}}
.l-nav-cta:hover{{background:var(--blue-d);transform:translateY(-1px);}}
.l-nav-burger{{display:none;background:none;border:none;font-size:22px;cursor:pointer;color:var(--blue-d);margin-left:auto;}}
.l-nav-mobile{{display:none;flex-direction:column;padding:0 16px 12px;gap:4px;}}
.l-nav-mobile.open{{display:flex;}}
.l-nav-mlink{{padding:10px 4px;font-size:14px;text-decoration:none;color:#333;border-radius:8px;}}

/* ── HERO ── */
.l-hero{{
  max-width:640px;width:100%;padding:3rem 0 2rem;
  animation: fadeUp .6s .1s ease both;
}}
.landing-logo{{
  display:flex;align-items:center;gap:12px;margin-bottom:1.8rem;justify-content:center;
}}
.logo-badge{{
  width:54px;height:54px;border-radius:16px;
  background:white;border:2px solid var(--blue-m);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
  box-shadow: 0 4px 20px rgba(21,101,192,.18);
  font-size:26px;
  animation: pulse-ring 2.5s ease infinite;
}}
.logo-name{{font-family:'Playfair Display',serif;font-size:30px;color:var(--blue-d);line-height:1;letter-spacing:-.5px}}
.logo-name span{{color:var(--accent)}}

.landing-title{{
  font-size:clamp(22px,4.5vw,38px);font-weight:700;color:var(--blue-d);
  line-height:1.2;margin-bottom:.7rem;
  animation: fadeUp .65s .15s ease both;
}}
.landing-title em{{
  font-style:normal;
  background: linear-gradient(135deg, var(--blue-d) 0%, #42a5f5 50%, var(--blue-d) 100%);
  background-size: 200% auto;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  animation: shimmer 3s linear infinite;
}}
.landing-sub{{
  font-size:15px;color:#3a5a7a;margin-bottom:1.6rem;line-height:1.65;
  animation: fadeUp .65s .2s ease both;
}}
.stats-row{{
  display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:1.8rem;
  animation: fadeUp .65s .3s ease both;
}}
.stat-pill{{
  background:white;border:1px solid rgba(21,101,192,.15);
  border-radius:14px;padding:10px 16px;text-align:center;
  box-shadow:0 2px 8px rgba(21,101,192,.08);
  transition:transform .18s,box-shadow .18s;
}}
.stat-pill:hover{{transform:translateY(-2px);box-shadow:0 5px 16px rgba(21,101,192,.15);}}
.stat-pill strong{{display:block;font-size:20px;font-weight:800;color:var(--blue-d);}}
.stat-pill small{{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.5px;}}
.btn-cta{{
  display:inline-block;
  background: linear-gradient(135deg, var(--blue) 0%, var(--blue-d) 100%);
  color:white;border:none;padding:14px 36px;border-radius:30px;
  font-size:16px;font-weight:700;cursor:pointer;
  box-shadow:0 4px 20px rgba(21,101,192,.35);
  transition:transform .2s,box-shadow .2s;
  margin-bottom:1.5rem;
  animation: fadeUp .65s .35s ease both;
}}
.btn-cta:hover{{transform:translateY(-3px);box-shadow:0 8px 30px rgba(21,101,192,.45);}}
.landing-features{{
  display:flex;gap:20px;flex-wrap:wrap;justify-content:center;
  animation: fadeUp .65s .4s ease both;
}}
.feat{{
  display:flex;align-items:center;gap:6px;font-size:13px;color:#555;
}}
.feat svg{{width:16px;height:16px;fill:var(--blue);flex-shrink:0;}}

/* ── INFO SECTIONS ── */
.l-section{{
  max-width:800px;width:100%;padding:2rem 0;text-align:left;
  animation: fadeUp .6s ease both;
}}
.l-section-title{{
  font-family:'Playfair Display',serif;
  font-size:22px;color:var(--blue-d);margin-bottom:1rem;
  padding-bottom:.5rem;border-bottom:2px solid var(--blue-m);
}}
.l-section p{{font-size:14px;line-height:1.7;color:#444;margin-bottom:.8rem;}}
.l-tips{{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:12px;margin-top:1rem;
}}
.l-tip{{
  background:white;border:1px solid rgba(21,101,192,.12);
  border-radius:14px;padding:1rem 1.2rem;
  box-shadow:0 2px 8px rgba(21,101,192,.06);
}}
.l-tip-ico{{font-size:22px;margin-bottom:.4rem;}}
.l-tip-title{{font-weight:700;font-size:13px;color:var(--blue-d);margin-bottom:.3rem;}}
.l-tip-text{{font-size:12px;color:#555;line-height:1.5;}}

/* ── APP ── */
#app{{position:fixed;inset:0;display:flex;flex-direction:column;visibility:hidden;opacity:0;transition:opacity .4s;}}
#app.visible{{visibility:visible;opacity:1;}}
#header{{
  height:var(--header-h);background:white;
  border-bottom:1px solid #e0e8f0;
  display:flex;align-items:center;gap:10px;padding:0 14px;
  box-shadow:0 2px 8px rgba(21,101,192,.07);z-index:100;flex-shrink:0;
}}
.h-logo{{display:flex;align-items:center;gap:8px;cursor:pointer;flex-shrink:0;}}
.h-badge{{
  width:34px;height:34px;border-radius:10px;
  background:var(--blue-l);border:1px solid var(--blue-m);
  display:flex;align-items:center;justify-content:center;font-size:18px;
}}
.h-name{{font-family:'Playfair Display',serif;font-size:15px;color:var(--blue-d);white-space:nowrap;}}
.h-name span{{color:var(--accent)}}
.h-sep{{width:1px;height:28px;background:#e0e8f0;margin:0 4px;flex-shrink:0;}}
.h-search{{
  flex:1;min-width:0;border:1px solid #dde5ee;border-radius:10px;
  padding:7px 12px;font-size:13px;font-family:'Nunito',sans-serif;
  background:#f5f8fc;outline:none;transition:border-color .2s,box-shadow .2s;
}}
.h-search:focus{{border-color:var(--blue-m);box-shadow:0 0 0 3px rgba(21,101,192,.12);background:white;}}
.h-stat{{font-size:12px;color:#666;white-space:nowrap;flex-shrink:0;}}
#btn-toggle{{background:none;border:none;font-size:20px;cursor:pointer;color:#555;padding:6px;flex-shrink:0;}}
#main{{display:flex;flex:1;overflow:hidden;}}
#sidebar{{
  width:var(--sidebar-w);background:white;
  border-right:1px solid #e0e8f0;
  display:flex;flex-direction:column;overflow:hidden;
  transition:transform .3s;
}}
#sidebar.hidden{{transform:translateX(-100%);}}
.sb-filters{{
  display:flex;flex-wrap:wrap;gap:5px;padding:10px 12px;
  border-bottom:1px solid #eef2f7;
}}
.chip{{
  font-size:11px;font-weight:600;padding:4px 10px;
  border-radius:20px;border:1px solid #dde5ee;
  background:#f5f8fc;cursor:pointer;transition:all .15s;color:#555;
}}
.chip.on{{background:var(--blue);color:white;border-color:var(--blue);}}
.sb-count{{
  padding:8px 12px;font-size:12px;color:#888;
  border-bottom:1px solid #eef2f7;flex-shrink:0;
}}
#list{{flex:1;overflow-y:auto;}}
.prov-sep{{
  font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--blue);background:#f0f4f8;padding:6px 12px;
  border-top:1px solid #e0e8f0;border-bottom:1px solid #e0e8f0;
  position:sticky;top:0;z-index:2;
}}
.list-item{{
  padding:10px 12px;border-bottom:1px solid #eef2f7;cursor:pointer;
  transition:background .15s;
}}
.list-item:hover,.list-item.active{{background:var(--blue-l);}}
.li-name{{font-weight:700;font-size:13px;color:#1a1a2e;margin-bottom:2px;}}
.li-addr{{font-size:11px;color:#666;line-height:1.4;}}
.li-tel{{font-size:11px;color:var(--blue);margin-top:2px;}}
.li-h{{font-size:10px;color:#888;margin-top:1px;}}
#map{{flex:1;}}

/* ── POPUP ── */
.popup-inner{{font-family:'Nunito',sans-serif;min-width:200px;}}
.popup-inner h3{{font-size:14px;font-weight:700;color:var(--blue-d);margin-bottom:6px;line-height:1.3;}}
.p-badge{{
  display:inline-block;font-size:10px;font-weight:700;
  background:var(--blue-l);color:var(--blue-d);
  border-radius:20px;padding:2px 8px;margin-bottom:6px;
}}
.p-row{{font-size:12px;color:#444;margin-top:4px;line-height:1.4;}}
.p-row a{{color:var(--blue);text-decoration:none;}}
.p-row a:hover{{text-decoration:underline;}}
.p-horario{{font-size:11px;color:#666;margin-top:3px;font-style:italic;}}
.p-wc{{font-size:11px;color:#888;margin-top:2px;}}

/* ── RESPONSIVE ── */
@media(max-width:700px){{
  :root{{--sidebar-w:100%;}}
  #sidebar{{position:absolute;top:var(--header-h);left:0;bottom:0;z-index:50;border-right:none;box-shadow:4px 0 20px rgba(0,0,0,.12);}}
  #sidebar.hidden{{transform:translateX(-100%);}}
  .h-stat{{display:none;}}
  .l-nav-links{{display:none;}}
  .l-nav-burger{{display:block;}}
  .l-hero{{padding:2rem 0 1.5rem;}}
}}
</style>
</head>
<body>

<!-- ══ LANDING ══════════════════════════════════════════ -->
<div id="landing">

  <nav class="l-nav" id="l-nav">
    <div class="l-nav-inner">
      <a class="l-nav-brand" href="#">
        💊 Farmacias<span class="l-nav-fx">ESP</span>
      </a>
      <div class="l-nav-links">
        <a href="https://lasendadeltiempo.github.io/" class="l-nav-link">🏠 Inicio</a>
        <a href="#sec-info" class="l-nav-link">¿Cómo funciona?</a>
        <a href="#sec-tips" class="l-nav-link">Consejos</a>
        <button class="l-nav-cta" onclick="entrarMapa()">Ver el mapa →</button>
      </div>
      <button class="l-nav-burger" id="l-nav-burger" onclick="document.getElementById('l-nav-menu').classList.toggle('open')">☰</button>
    </div>
    <div class="l-nav-mobile" id="l-nav-menu">
      <a href="https://lasendadeltiempo.github.io/" class="l-nav-mlink" style="color:var(--blue-d);font-weight:800;border-bottom:1px solid rgba(21,101,192,.15);">🏠 Inicio</a>
      <a href="#sec-info" class="l-nav-mlink" onclick="document.getElementById('l-nav-menu').classList.remove('open')">📖 ¿Cómo funciona?</a>
      <a href="#sec-tips" class="l-nav-mlink" onclick="document.getElementById('l-nav-menu').classList.remove('open')">💡 Consejos</a>
      <button class="l-nav-cta" style="margin:8px 16px 12px" onclick="entrarMapa()">Ver el mapa →</button>
    </div>
  </nav>

  <div class="l-hero">
    <div class="landing-logo">
      <div class="logo-badge">💊</div>
      <div class="logo-name">Farmacias<span>ESP</span></div>
    </div>
    <h1 class="landing-title">Encuentra tu <em>farmacia</em> más cercana</h1>
    <p class="landing-sub"><strong>{TOTAL:,}</strong> farmacias geolocalizadas en toda España.<br>Con dirección, teléfono y horario cuando disponible. Gratis y sin registro.</p>
    <div class="stats-row">
      <div class="stat-pill"><strong>{TOTAL:,}</strong><small>Farmacias</small></div>
      <div class="stat-pill"><strong>{con_tel:,}</strong><small>Con teléfono</small></div>
      <div class="stat-pill"><strong>{con_horario:,}</strong><small>Con horario</small></div>
      <div class="stat-pill"><strong>50</strong><small>Provincias</small></div>
    </div>
    <button class="btn-cta" onclick="entrarMapa()">Abrir el mapa →</button>
    <div class="landing-features">
      <div class="feat"><svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>Mapa interactivo</div>
      <div class="feat"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Sin registro</div>
      <div class="feat"><svg viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>Teléfono directo</div>
      <div class="feat"><svg viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zm4.24 16L12 15.45 7.77 18l1.12-4.81-3.73-3.23 4.92-.42L12 5l1.92 4.53 4.92.42-3.73 3.23L16.23 18z"/></svg>Datos abiertos OSM</div>
    </div>
  </div>

  <div class="l-section" id="sec-info">
    <div class="l-section-title">¿Cómo usar el mapa?</div>
    <div class="l-tips">
      <div class="l-tip">
        <div class="l-tip-ico">🔍</div>
        <div class="l-tip-title">Busca por nombre o ciudad</div>
        <div class="l-tip-text">Escribe el nombre de una farmacia o una ciudad en la barra de búsqueda y el mapa se actualizará al instante.</div>
      </div>
      <div class="l-tip">
        <div class="l-tip-ico">📍</div>
        <div class="l-tip-title">Haz zoom en tu zona</div>
        <div class="l-tip-text">Los puntos se agrupan en clusters. A más zoom, más detalle. A nivel de calle verás cada farmacia individualmente.</div>
      </div>
      <div class="l-tip">
        <div class="l-tip-ico">📞</div>
        <div class="l-tip-title">Llama directamente</div>
        <div class="l-tip-text">Pulsa sobre cualquier farmacia para ver su ficha. Si tiene teléfono, puedes llamar con un toque desde el móvil.</div>
      </div>
      <div class="l-tip">
        <div class="l-tip-ico">🗺️</div>
        <div class="l-tip-title">Ir en Google Maps</div>
        <div class="l-tip-text">Cada ficha incluye un enlace directo a Google Maps para obtener la ruta desde tu ubicación actual.</div>
      </div>
    </div>
  </div>

  <div class="l-section" id="sec-tips">
    <div class="l-section-title">Información útil sobre farmacias</div>
    <p>En España las farmacias están reguladas y distribuidas por todo el territorio nacional. Cada municipio tiene al menos una farmacia de guardia para emergencias fuera del horario habitual.</p>
    <p>Para localizar la farmacia de guardia más cercana puedes consultar el tablón de cada farmacia o llamar al <strong>112</strong> en caso de urgencia. También puedes buscar directamente en el mapa y llamar a las cercanas a tu ubicación.</p>
    <div class="l-tips" style="margin-top:1rem;">
      <div class="l-tip">
        <div class="l-tip-ico">🌙</div>
        <div class="l-tip-title">Guardia nocturna</div>
        <div class="l-tip-text">Las farmacias de guardia atienden 24h. Hay al menos una por zona en cada municipio importante.</div>
      </div>
      <div class="l-tip">
        <div class="l-tip-ico">💬</div>
        <div class="l-tip-title">Consejo farmacéutico</div>
        <div class="l-tip-text">El farmacéutico puede orientarte sobre medicamentos sin receta, interacciones y primeros auxilios.</div>
      </div>
      <div class="l-tip">
        <div class="l-tip-ico">♿</div>
        <div class="l-tip-title">Accesibilidad</div>
        <div class="l-tip-text">Algunas farmacias incluyen información sobre accesibilidad para personas con movilidad reducida.</div>
      </div>
    </div>
  </div>

  <div style="padding:2rem 0;font-size:12px;color:#aaa;text-align:center;">
    Datos: <a href="https://www.openstreetmap.org" target="_blank" rel="noopener" style="color:var(--blue);">OpenStreetMap</a> contributors · 
    <a href="https://lasendadeltiempo.github.io/" style="color:var(--blue);">Quien Busca Encuentra</a>
  </div>

</div>

<!-- ══ APP ═══════════════════════════════════════════════ -->
<div id="app">
  <div id="header">
    <div class="h-logo" onclick="volverLanding()">
      <div class="h-badge">💊</div>
      <div class="h-name">Farmacias<span>ESP</span></div>
    </div>
    <div class="h-sep"></div>
    <input class="h-search" type="text" id="search-input" placeholder="Buscar por nombre, ciudad, calle...">
    <div class="h-stat">Mostrando <strong id="stat-visible">{TOTAL}</strong> de {TOTAL}</div>
    <button id="btn-toggle" onclick="toggleSidebar()" aria-label="Menu">&#9776;</button>
  </div>
  <div id="main">
    <div id="sidebar">
      <div class="sb-filters" id="chips-container">
        <span class="chip on" data-prov="" onclick="setFiltroProv(this,'')">Todas</span>
      </div>
      <div class="sb-count">
        Mostrando <strong id="sb-count">{TOTAL}</strong> farmacias
      </div>
      <div id="list"></div>
    </div>
    <div id="map"></div>
  </div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<style>
.marker-cluster-small div,.marker-cluster-medium div,.marker-cluster-large div{{
  background-color:rgba(21,101,192,0.88)!important;color:white!important;
  font-family:'Nunito',sans-serif!important;font-weight:700!important;font-size:13px!important;
}}
.marker-cluster-small,.marker-cluster-medium,.marker-cluster-large{{
  background-color:rgba(21,101,192,0.25)!important;
}}
</style>
<script>
const DATOS = {datos_json};

// ── Estado ─────────────────────────────────────────────
let map, markersLayer, activeIdx = -1;
let currentFiltered = [...DATOS];
let filtroTexto = '', filtroProv = '';
let sidebarOpen = true;
let listaOffset = 0;
const LISTA_CHUNK = 80;

// ── Icon ───────────────────────────────────────────────
const farmIcon = L.divIcon({{
  html: '<div style="background:#1565c0;width:12px;height:12px;border-radius:50%;border:2.5px solid white;box-shadow:0 0 4px rgba(21,101,192,.6);"></div>',
  className: '',
  iconSize: [12,12],
  iconAnchor: [6,6],
  popupAnchor: [0,-8]
}});

// ── Landing ────────────────────────────────────────────
function entrarMapa() {{
  const l = document.getElementById('landing');
  const a = document.getElementById('app');
  l.classList.add('hide');
  a.classList.add('visible');
  setTimeout(() => {{ l.style.display='none'; }}, 650);
  if (!map) initMap();
}}
function volverLanding() {{
  const l = document.getElementById('landing');
  const a = document.getElementById('app');
  l.style.display='';
  requestAnimationFrame(() => l.classList.remove('hide'));
  a.classList.remove('visible');
}}

// ── Sidebar toggle ─────────────────────────────────────
function toggleSidebar() {{
  const sb = document.getElementById('sidebar');
  sidebarOpen = !sidebarOpen;
  sb.classList.toggle('hidden', !sidebarOpen);
}}

// ── Filtros ────────────────────────────────────────────
function setFiltroProv(el, prov) {{
  filtroProv = prov;
  document.querySelectorAll('.chip').forEach(c => c.classList.toggle('on', c === el));
  filtrar();
}}

document.addEventListener('DOMContentLoaded', () => {{
  // Barra de búsqueda
  document.getElementById('search-input').addEventListener('input', e => {{
    filtroTexto = e.target.value;
    filtrar();
  }});

  // Construir chips de provincia
  const provCnt = {{}};
  DATOS.forEach(d => {{
    if (d.prov) provCnt[d.prov] = (provCnt[d.prov] || 0) + 1;
  }});
  const provs = Object.keys(provCnt).sort((a,b) => provCnt[b]-provCnt[a]);
  const cc = document.getElementById('chips-container');
  provs.slice(0,20).forEach(p => {{
    const sp = document.createElement('span');
    sp.className = 'chip';
    sp.dataset.prov = p;
    sp.textContent = `${{p}} (${{provCnt[p]}})`;
    sp.onclick = () => setFiltroProv(sp, p);
    cc.appendChild(sp);
  }});

  filtrar();
}});

function filtrar() {{
  const txt = filtroTexto.toLowerCase();
  currentFiltered = DATOS.filter(d => {{
    if (filtroProv && d.prov !== filtroProv) return false;
    if (txt && !d.n.toLowerCase().includes(txt)
            && !(d.d||'').toLowerCase().includes(txt)
            && !(d.prov||'').toLowerCase().includes(txt)) return false;
    return true;
  }}).sort((a,b) => {{
    const pa = (a.prov||'zzz').toLowerCase();
    const pb = (b.prov||'zzz').toLowerCase();
    if (pa !== pb) return pa.localeCompare(pb, 'es');
    return (a.n||'').localeCompare(b.n||'', 'es');
  }});
  renderLista();
  if (map) renderMapa();
  const n = currentFiltered.length;
  document.getElementById('stat-visible').textContent = n;
  document.getElementById('sb-count').textContent = n;
}}

// ── Mapa ───────────────────────────────────────────────
function initMap() {{
  map = L.map('map', {{zoomControl:true}}).setView([40.4,-3.7], 6);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
  }}).addTo(map);
  renderMapa();
}}

function renderMapa() {{
  if (markersLayer) map.removeLayer(markersLayer);
  markersLayer = L.markerClusterGroup({{
    chunkedLoading: true,
    chunkInterval: 100,
    chunkDelay: 50,
    maxClusterRadius: 60,
    disableClusteringAtZoom: 16,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    animate: true,
  }});
  currentFiltered.forEach((d, idx) => {{
    const m = L.marker([d.lat, d.lon], {{icon: farmIcon}})
      .bindPopup(popupHtml(d), {{maxWidth: 280}});
    m.on('click', () => selectItem(idx));
    markersLayer.addLayer(m);
  }});
  markersLayer.addTo(map);
  if (currentFiltered.length > 0 && currentFiltered.length < DATOS.length) {{
    const lats = currentFiltered.map(d => d.lat);
    const lons = currentFiltered.map(d => d.lon);
    map.fitBounds([
      [Math.min(...lats), Math.min(...lons)],
      [Math.max(...lats), Math.max(...lons)]
    ], {{padding:[30,30], maxZoom:14}});
  }} else {{
    map.setView([40.4,-3.7], 6);
  }}
}}

function popupHtml(d) {{
  let h = `<div class="popup-inner">
    <h3>${{d.n}}</h3>
    <span class="p-badge">💊 Farmacia</span>`;
  if (d.d)   h += `<div class="p-row">📍 ${{d.d}}</div>`;
  if (d.tel) h += `<div class="p-row">📞 <a href="tel:${{d.tel}}">${{d.tel}}</a></div>`;
  if (d.web) h += `<div class="p-row">🌐 <a href="${{d.web}}" target="_blank" rel="noopener">Ver web</a></div>`;
  if (d.h)   h += `<div class="p-horario">🕐 ${{d.h}}</div>`;
  if (d.wc && d.wc !== 'no') h += `<div class="p-wc">♿ Accesible: ${{d.wc}}</div>`;
  h += `<div class="p-row" style="margin-top:8px">
    <a href="https://www.google.com/maps/search/?api=1&query=${{d.lat}},${{d.lon}}" target="_blank" rel="noopener">
      🗺️ Ver en Google Maps
    </a></div>`;
  return h + '</div>';
}}

// ── Lista ──────────────────────────────────────────────
function renderLista() {{
  listaOffset = 0;
  const list = document.getElementById('list');
  list.innerHTML = '';
  appendLista();
  list.addEventListener('scroll', onListScroll, {{once:false}});
}}

function onListScroll(e) {{
  const el = e.target;
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 100) appendLista();
}}

function appendLista() {{
  const list = document.getElementById('list');
  const old = document.getElementById('list-sentinel');
  if (old) old.remove();
  const chunk = currentFiltered.slice(listaOffset, listaOffset + LISTA_CHUNK);
  let lastProv = listaOffset > 0 ? (currentFiltered[listaOffset-1].prov||'') : null;
  chunk.forEach((d, j) => {{
    const i = listaOffset + j;
    const prov = d.prov || '— Sin provincia —';
    if (prov !== lastProv) {{
      const sep = document.createElement('div');
      sep.className = 'prov-sep';
      sep.textContent = prov;
      list.appendChild(sep);
      lastProv = prov;
    }}
    const div = document.createElement('div');
    div.className = 'list-item' + (i === activeIdx ? ' active' : '');
    div.innerHTML = `
      <div class="li-name">${{d.n}}</div>
      ${{d.d ? `<div class="li-addr">${{d.d}}</div>` : ''}}
      ${{d.tel ? `<div class="li-tel">📞 ${{d.tel}}</div>` : ''}}
      ${{d.h ? `<div class="li-h">🕐 ${{d.h}}</div>` : ''}}`;
    div.onclick = () => selectItem(i);
    list.appendChild(div);
  }});
  listaOffset += chunk.length;
  if (listaOffset < currentFiltered.length) {{
    const sentinel = document.createElement('div');
    sentinel.id = 'list-sentinel';
    list.appendChild(sentinel);
  }}
}}

function selectItem(idx) {{
  activeIdx = idx;
  document.querySelectorAll('.list-item').forEach((el,i) => el.classList.toggle('active', i===idx));
  const d = currentFiltered[idx];
  if (map) map.setView([d.lat, d.lon], 16);
}}
</script>
</body>
</html>'''

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Generado: {OUTPUT}")
print(f"   Tamaño: {os.path.getsize(OUTPUT)/1024/1024:.1f} MB")
