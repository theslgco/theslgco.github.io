# theslg.co

The SLG website. Static HTML/CSS, hosted free on GitHub Pages at https://www.theslg.co.

## Editing

All page content lives in `build.py`. Change the text there, then run:

```
python3 build.py
```

This regenerates every page, the sitemap, robots.txt and the redirects from the old Wix addresses. Commit and push; GitHub Pages publishes within a minute.

- Styles: `assets/css/site.css` (brand tokens at the top, matching the SLG brand sheet).
- Photographs: Unsplash licence, listed in `PHOTOS` in `build.py` and credited on `/credits/`.
- Forms: delivered to info@theslg.co by FormSubmit (free, no account). The first submission triggers a one-time activation email to info@theslg.co.
- The Private Register table: edit `REGISTER` in `build.py`. Never publish prices, serials or seller names there.
