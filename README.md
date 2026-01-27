# SEO Audit App 🚀

A custom-built SEO Audit application that crawls websites and generates actionable SEO insights in one place.

This tool is designed to replace manual audits and reduce dependency on multiple third-party SEO tools by combining:
- Technical SEO checks
- On-page SEO analysis
- Performance insights (future)
- Search Console data (future)

---

## 🔍 Features (Current & Planned)

### ✅ Current (MVP)
- Crawl websites via URLs / sitemap
- Extract:
  - Meta title & description
  - Headings (H1–H6)
  - Internal & external links
  - Images & alt attributes
- Detect SEO issues automatically:
  - Missing / duplicate titles
  - Missing H1
  - Long titles
  - Broken links
- Export SEO audit reports (CSV / Excel)

### 🛠 Planned
- Google Search Console API integration
- PageSpeed Insights & Core Web Vitals
- SEO scoring system (per page & site)
- Competitor comparison
- Client-ready dashboard
- SaaS deployment

---

## 🏗 Tech Stack

- **Language**: Python
- **Backend**: FastAPI
- **Crawling**: Requests, BeautifulSoup, Playwright (JS sites)
- **Database**: SQLite (MVP), PostgreSQL (later)
- **Reports**: CSV / Excel / PDF
- **Version Control**: Git + GitHub

---

## 📁 Project Structure

```text
crawler/     → Fetch & parse web pages
rules/       → SEO rules & issue detection
api/         → API endpoints (FastAPI)
reports/     → SEO audit report generation
db/          → Database models
config/      → App configuration
