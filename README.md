<p align="center">
  <img src="apps/frontend/public/logo.svg" alt="veyl.io" width="284" height="68">
</p>

<h4 align="center">
  <a href="https://www.veyl.io">Website</a> |
  <a href="https://www.veyl.io/docs">Documentation</a> |
  <a href="https://github.com/RomeoCavazza/veyl.io">GitHub</a> |
  <a href="https://discord.gg/TKbNuuV4sX">Discord</a>
</h4>

<p align="center">
  <a href="https://github.com/RomeoCavazza/veyl.io/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
  <a href="https://github.com/RomeoCavazza/veyl.io"><img src="https://img.shields.io/badge/status-In_Development-yellow" alt="Status"></a>
  <a href="https://developers.facebook.com/"><img src="https://img.shields.io/badge/partner-Meta_for_Developers-blue" alt="Meta Partner"></a>
  <a href="https://developers.tiktok.com/"><img src="https://img.shields.io/badge/partner-TikTok_for_Developers-black" alt="TikTok Partner"></a>
</p>

<p align="center">⚡ A social media intelligence platform that helps you monitor, analyze, and anticipate trends on Instagram and TikTok 🔍</p>

[veyl.io](https://www.veyl.io) helps you shape a comprehensive social media monitoring experience, offering powerful analytics and trend detection features powered by official Meta/TikTok APIs.

## 🖥 Platform Features

- **Trend Monitoring** — Create custom projects to track hashtags, creators, and emerging trends across Instagram and TikTok
- **Advanced Analytics** — Real-time engagement metrics, growth tracking, and performance insights
- **Fast Search** — Search across millions of posts with database-backed fallback
- **Creator Intelligence** — Analyze influencer performance, partnerships, and content strategies
- **Project Workspaces** — Organize your monitoring with dedicated project dashboards (Watchlist, Grid, Analytics)

See the [online documentation](https://www.veyl.io/docs) for more details.

## ✨ Features

- **Search-as-you-type:** Find posts and creators with real-time API integration and database fallback
- **Multi-platform monitoring:** Track trends simultaneously on Instagram and TikTok
- **Real-time analytics:** Monitor engagement rates, follower growth, and content performance
- **Creator insights:** Analyze influencer partnerships, content strategies, and audience demographics
- **Project-based organization:** Organize your monitoring with custom projects and watchlists
- **OAuth integration:** Secure authentication via Meta, TikTok, and Google OAuth
- **API-first architecture:** RESTful API for programmatic access and integrations
- **Open source:** Fully open-source codebase available on GitHub
- **Conformité RGPD:** Compliant with GDPR and CCPA data protection regulations
- **Meta & TikTok partnerships:** Official partner with Meta for Developers and TikTok for Developers

## 📖 Documentation

You can consult veyl.io's documentation at [veyl.io/docs](https://www.veyl.io/docs).

## 🚀 Getting Started

For basic instructions on how to set up veyl.io, configure OAuth, and create your first monitoring project, take a look at our [documentation](https://www.veyl.io/docs) guide.

### Quick Start

**Backend (FastAPI)**
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend (React)**
```bash
cd apps/frontend
npm install
npm run dev
```

**Access:**
- Frontend: `http://localhost:8081`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 🌍 Tech Stack

**Backend:**
- **FastAPI** — Python async API framework
- **PostgreSQL** — Relational database (Railway)
- **Rate Limiting** — In-memory rate limiting for API protection

**Frontend:**
- **React 18** — UI framework
- **TypeScript** — Static typing
- **Vite** — Build tool and dev server
- **Tailwind CSS** — Utility-first CSS framework
- **Radix UI + shadcn/ui** — Accessible UI components

**Infrastructure:**
- **Railway** — Backend hosting (auto-deploy)
- **Vercel** — Frontend hosting with proxy to Railway

## 🧰 Official Integrations

veyl.io integrates with official developer platforms:

**Meta for Developers**
- Instagram Graph API — Access to public Instagram Business content
- Facebook Pages API — Page management and insights
- [Documentation](https://developers.facebook.com/)

**TikTok for Developers**
- TikTok Login Kit — OAuth authentication
- TikTok API — Access to public videos and creator statistics
- [Documentation](https://developers.tiktok.com/)


## ⚙️ Advanced Usage

For technical details, see the [online documentation](https://www.veyl.io/docs).

## 🧾 Roadmap

### ✅ Phase 1: Foundations (Completed)
- Projects CRUD with database models
- OAuth integration (Meta, TikTok, Google)
- Search interface with API-first strategy and database fallback
- Analytics dashboards and insights
- Project management UI

### 🔄 Phase 2: Post-App Review (In Progress)
- **Advanced Search** — Enhanced search UX, filters, and ranking
- **Supabase + pgvector** — Semantic storage, RAG, similarity search
- **Make / n8n** — Automated data ingestion
- **Dust** — Agent internal reasoning (if needed)

## 📊 Privacy & Data Protection

veyl.io collects **anonymized** usage data to help us improve our product. We are fully compliant with GDPR and CCPA regulations.

To request deletion of collected data, please visit our [data deletion page](https://www.veyl.io/data-deletion) or write to us at [romeo.cavazza@gmail.com](mailto:romeo.cavazza@gmail.com).

If you want to know more about the kind of data we collect and what we use it for, check our [Privacy Policy](https://www.veyl.io/privacy).

## 📫 Get in Touch!

veyl.io is a social media intelligence platform created as an open-source project, developed in collaboration with **ISCOM Paris** and **EPITECH Paris**.

💌 Want to make a suggestion or give feedback? Here are some of the channels where you can reach us:

- For feature requests, please visit our [GitHub discussions](https://github.com/RomeoCavazza/veyl.io/discussions)
- Found a bug? Open an [issue](https://github.com/RomeoCavazza/veyl.io/issues)!
- Want to be part of our Discord community? [Join us!](https://discord.gg/TKbNuuV4sX)

Thank you for your support!

## 👩‍💻 Contributing

veyl.io is, and will always be, open-source! If you want to contribute to the project, here's how:

1. Fork the repository on GitHub
2. Create a branch from `main`
3. Develop and test locally
4. Push and create a Pull Request

Contributions are welcome! Check out the [GitHub issues](https://github.com/RomeoCavazza/veyl.io/issues) to see how you can help.

### Academic Partners

- **ISCOM Paris** — Strategic planning, marketing insights, and trend analysis
- **EPITECH Paris** — Technical development and backend architecture

## 📦 Versioning

veyl.io releases and their associated binaries are available on the project's [releases page](https://github.com/RomeoCavazza/veyl.io/releases).

The project follows [SemVer conventions](https://semver.org/) for versioning.

---

<p align="center">
  Made with ❤️ by the veyl.io team
</p>
