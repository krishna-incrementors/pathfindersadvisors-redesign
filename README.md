# Pathfinders Advisors | website redesign (review build)

Redesign of [pathfindersadvisors.com](https://www.pathfindersadvisors.com/) for client review.
Live preview: https://krishna-incrementors.github.io/pathfindersadvisors-redesign/

The preview is **noindex** (meta robots + robots.txt) so it never competes with the live site in Google.
Canonical tags already point at the live www.pathfindersadvisors.com URLs.

## Pages

Same URL paths as the current WordPress site, so nothing needs redirecting at launch:

| Path | Page |
| --- | --- |
| `/` | Families (home) |
| `/educators/` | School counselors & educators |
| `/financial-planners/` | Financial planners |
| `/workshops/` | Free virtual workshops (past dates hide themselves) |
| `/resources/` | Knowledge base: keyword search + topic filters (links to the existing blog posts) |
| `/about/` | About us & team |
| `/contact-us/` | Embedded booking calendar + contact form |

## Brand source

Copy follows Sue's brand documents: *Core Messaging* (category, umbrella statement, brand promise, taglines, core messages #1-3, objection answers) and *Ideal persona* (Future-Focused Fran, Legacy-Building Lisa, Legacy Larry). The home FAQ and the Financial Planners FAQ use the objection answers from those documents.

## Editing

- Page copy: `src/pages/*.html`
- Shared data (reviews, workshop dates, articles, FAQs, page titles and meta): top of `build.py`
- Styles: `assets/css/style.css` | Behaviour: `assets/js/main.js`

Build locally (Python 3, no packages needed):

```bash
python3 build.py              # review build into site/
python3 -m http.server 4178 --directory site
```

Knowledge base search matches titles, summaries and topic/grade terms indexed from each live article. After adding articles to `build.py`, refresh the index:

```bash
python3 tools/index_articles.py
```

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds and publishes `site/` to the `gh-pages` branch.

## Structured data (JSON-LD), generated per page

- All pages: Organization, WebSite, WebPage (+ BreadcrumbList on inner pages)
- Home: Service with offer catalog, FAQPage (same text as the visible FAQ)
- Financial planners: Service, FAQPage (advisor questions)
- About: AboutPage, Person x3, Course
- Workshops: EducationEvent for each upcoming workshop (past dates drop out on the next build)
- Knowledge base: CollectionPage + ItemList
- Contact: ContactPage

## Before going live

1. Connect the forms: add `data-endpoint="https://..."` to each `<form data-pf-form>` (CRM / form service). Until then they validate and show a "not connected yet" note.
2. Confirm the FAQ answers (taken from the brand documents' objection answers, plus timing and virtual-coverage answers from existing site copy).
3. Copy images and the video from `/wp-content/uploads/` into `assets/` (they are hotlinked from WordPress today).
4. Build with `python3 build.py --live` (indexable, adds sitemap.xml) and point the domain.
5. Re-test schema in Google's Rich Results Test.
