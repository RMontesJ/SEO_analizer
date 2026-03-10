import sys
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlparse, urljoin
import re
import time
import json
import os
import socket
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

url = sys.argv[1]

result = {}

try:

    headers = {
        "User-Agent": "Mozilla/5.0 SEO Analyzer Bot"
    }

    start = time.time()
    r = requests.get(url, headers=headers, timeout=10)
    load_time = round(time.time() - start, 2)

    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(url).netloc

    # ----------------
    # DOMAIN IP
    # ----------------
    try:
        ip_address = socket.gethostbyname(domain)
    except:
        ip_address = "Unknown"

    # ----------------
    # TITLE
    # ----------------
    title = soup.title.string.strip() if soup.title else ""
    title_length = len(title)

    # ----------------
    # META DESCRIPTION
    # ----------------
    description = ""
    desc = soup.find("meta", attrs={"name":"description"})
    if desc:
        description = desc.get("content","")

    # ----------------
    # VIEWPORT
    # ----------------
    viewport = bool(soup.find("meta", attrs={"name":"viewport"}))

    # ----------------
    # CANONICAL
    # ----------------
    canonical = ""
    canonical_tag = soup.find("link", rel="canonical")
    if canonical_tag:
        canonical = canonical_tag.get("href","")

    # ----------------
    # ROBOTS META
    # ----------------
    robots_meta = ""
    robots = soup.find("meta", attrs={"name":"robots"})
    if robots:
        robots_meta = robots.get("content","")

    # ----------------
    # OPEN GRAPH
    # ----------------
    og_title = ""
    og_desc = ""
    og_image = ""

    ogt = soup.find("meta", property="og:title")
    ogd = soup.find("meta", property="og:description")
    ogi = soup.find("meta", property="og:image")

    if ogt: og_title = ogt.get("content","")
    if ogd: og_desc = ogd.get("content","")
    if ogi: og_image = ogi.get("content","")

    # ----------------
    # TWITTER CARD
    # ----------------
    twitter_card = ""
    tw = soup.find("meta", attrs={"name":"twitter:card"})
    if tw:
        twitter_card = tw.get("content","")

    # ----------------
    # HEADINGS
    # ----------------
    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")

    # ----------------
    # LINKS
    # ----------------
    internal_links = 0
    external_links = 0

    for link in soup.find_all("a", href=True):

        href = link["href"]
        full = urljoin(url, href)

        if domain in urlparse(full).netloc:
            internal_links += 1
        else:
            external_links += 1

    # ----------------
    # IMAGES
    # ----------------
    images = soup.find_all("img")

    images_without_alt = []

    for img in images:

        src = img.get("src")

        if not src:
            continue

        full_src = urljoin(url, src)

        if not img.get("alt"):

            images_without_alt.append({
                "url": full_src,
                "suggested_alt": os.path.splitext(os.path.basename(src))[0].replace("-", " ").replace("_"," ")
            })

    # ----------------
    # TEXT ANALYSIS
    # ----------------
    text = soup.get_text().lower()

    words = re.findall(r'\b[a-z]{4,}\b', text)

    stopwords = set([
        "this","that","with","have","from","your","about","there",
        "their","would","could","should","where","which","these"
    ])

    words = [w for w in words if w not in stopwords]

    common_words = Counter(words).most_common(10)

    word_count = len(words)

    # ----------------
    # SCHEMA / STRUCTURED DATA
    # ----------------
    schema = soup.find_all("script", type="application/ld+json")
    schema_count = len(schema)

    # ----------------
    # FAVICON
    # ----------------
    favicon = ""
    icon = soup.find("link", rel="icon")

    if icon:
        favicon = icon.get("href","")

    # ----------------
    # HTTPS
    # ----------------
    https = url.startswith("https")

    # ----------------
    # PAGE SIZE
    # ----------------
    page_size = round(len(html)/1024,2)

    # ----------------
    # ROBOTS.TXT
    # ----------------
    robots_exists = False

    try:
        robots_url = urljoin(url,"/robots.txt")
        rob = requests.get(robots_url, headers=headers, timeout=5)
        robots_exists = rob.status_code == 200
    except:
        pass

    # ----------------
    # SITEMAP
    # ----------------
    sitemap_exists = False

    try:
        sitemap_url = urljoin(url,"/sitemap.xml")
        sm = requests.get(sitemap_url, headers=headers, timeout=5)
        sitemap_exists = sm.status_code == 200
    except:
        pass

    # ----------------
    # SEO SCORE
    # ----------------
    score = 0
    issues = []

    if title:
        score += 10
    else:
        issues.append({
            "issue":"Missing title",
            "suggestion":"Add a <title> tag"
        })

    if 10 <= title_length <= 60:
        score += 10
    else:
        issues.append({
            "issue":"Title length not optimal",
            "suggestion":"Keep title between 10 and 60 characters"
        })

    if description:
        score += 10
    else:
        issues.append({
            "issue":"Missing meta description",
            "suggestion":"Add meta description"
        })

    if len(h1) == 1:
        score += 10
    else:
        issues.append({
            "issue":"Should have exactly 1 H1",
            "suggestion":"Use a single H1 heading"
        })

    if viewport:
        score += 10
    else:
        issues.append({
            "issue":"Missing viewport",
            "suggestion":"Add viewport meta tag"
        })

    if https:
        score += 10
    else:
        issues.append({
            "issue":"Site not using HTTPS",
            "suggestion":"Install SSL certificate"
        })

    if len(images_without_alt) == 0:
        score += 10
    else:
        issues.append({
            "issue":"Images missing ALT tags",
            "suggestion":"Add alt attributes",
            "images_missing_alt":images_without_alt
        })

    if load_time < 2:
        score += 10
    else:
        issues.append({
            "issue":"Slow load time",
            "suggestion":"Optimize images and scripts"
        })

    if internal_links > 0:
        score += 10
    else:
        issues.append({
            "issue":"No internal links",
            "suggestion":"Add links to other pages"
        })

    if external_links > 0:
        score += 10

    # ----------------
    # RESULT
    # ----------------
    result = {
        "domain": domain,

        "ip_address": ip_address,

        "url":url,

        "seo_score":score,

        "https":https,

        "load_time":load_time,

        "page_size_kb":page_size,

        "title":title,

        "title_length":title_length,

        "description":description,

        "canonical":canonical,

        "robots_meta":robots_meta,

        "viewport":viewport,

        "mobile_friendly":viewport,

        "h1_count":len(h1),

        "h2_count":len(h2),

        "internal_links":internal_links,

        "external_links":external_links,

        "images_total":len(images),

        "images_without_alt_count":len(images_without_alt),

        "images_missing_alt":images_without_alt,

        "word_count":word_count,

        "top_keywords":common_words,

        "schema_count":schema_count,

        "favicon":favicon,

        "robots_txt":robots_exists,

        "sitemap":sitemap_exists,

        "og_title":og_title,

        "og_description":og_desc,

        "og_image":og_image,

        "twitter_card":twitter_card,

        "issues":issues

    }
   

except Exception as e:

    result = {
        "error":str(e)
    }

print(json.dumps(result, indent=4))

def explain_issue(issue):
    explanations = {
        "Missing title":
            "El título es el texto que aparece en Google cuando alguien busca tu página. "
            "Si no existe, Google no sabrá cómo mostrar tu página correctamente.",
        "Title length not optimal":
            "Los títulos demasiado largos o demasiado cortos no funcionan bien en Google. "
            "Google suele mostrar entre 50 y 60 caracteres.",
        "Missing meta description":
            "La meta descripción es el pequeño texto que aparece debajo del título en Google. "
            "Ayuda a convencer al usuario de entrar en tu web.",
        "Should have exactly 1 H1":
            "El H1 es el título principal de la página. Tener más de uno puede confundir a Google "
            "sobre el tema principal.",
        "Missing viewport":
            "El viewport permite que la web se vea correctamente en móviles.",
        "Site not using HTTPS":
            "HTTPS protege la información de los usuarios y Google lo considera un factor de ranking.",
        "Images missing ALT tags":
            "El atributo ALT describe las imágenes para Google y para personas con discapacidad visual.",
        "Slow load time":
            "Las páginas lentas hacen que los usuarios abandonen la web y Google penaliza su posicionamiento.",
        "No internal links":
            "Los enlaces internos ayudan a Google a entender la estructura de la web."
    }

    return explanations.get(issue, "Este problema puede afectar al posicionamiento SEO.")


def generate_pdf(result):
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("SEO Audit Report", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"URL Analizada: {result['url']}", styles["Normal"]))
    story.append(Paragraph(f"Dominio: {result['domain']}", styles["Normal"]))
    story.append(Paragraph(f"IP: {result['ip_address']}", styles["Normal"]))
    story.append(Paragraph(f"SEO Score: {result['seo_score']} / 100", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Resumen de métricas", styles["Heading2"]))

    data = [
        ["Métrica", "Valor"],
        ["Título", result["title"]],
        ["Longitud título", result["title_length"]],
        ["Meta descripción", result["description"]],
        ["H1 encontrados", result["h1_count"]],
        ["H2 encontrados", result["h2_count"]],
        ["Links internos", result["internal_links"]],
        ["Links externos", result["external_links"]],
        ["Imágenes totales", result["images_total"]],
        ["Imágenes sin ALT", result["images_without_alt_count"]],
        ["Tiempo de carga", result["load_time"]],
        ["Tamaño página KB", result["page_size_kb"]],
        ["HTTPS", result["https"]],
    ]

    table = Table(data, colWidths=[7 * cm, 10 * cm])
    story.append(table)
    story.append(Spacer(1, 30))

    story.append(Paragraph("Problemas SEO detectados", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for issue in result["issues"]:
        story.append(Paragraph(f"<b>Problema:</b> {issue['issue']}", styles["Normal"]))
        story.append(Paragraph(f"<b>Cómo solucionarlo:</b> {issue['suggestion']}", styles["Normal"]))

        explanation = explain_issue(issue["issue"])
        story.append(Paragraph(f"<b>Explicación:</b> {explanation}", styles["Normal"]))
        story.append(Spacer(1, 15))

    pdf = SimpleDocTemplate("seo_report.pdf", pagesize=A4)
    pdf.build(story)
    
generate_pdf(result)    