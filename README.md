# Solar Hisaab: setup guide (all free)

## 1. Put it online with GitHub Pages
1. Log in to github.com and create a new **public** repository, e.g. `solar-hisaab`.
2. Click **Add file → Upload files** and drag in everything from this folder
   (including the hidden `.github` folder; if your computer hides it, create the file
   `.github/workflows/update-prices.yml` on GitHub and paste its contents).
3. Go to **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, Save.
4. After about a minute your site is live at `https://YOUR-USERNAME.github.io/solar-hisaab/`.

## 2. Turn on daily price updates
1. Go to **Settings → Actions → General → Workflow permissions**, choose **Read and write**, Save.
2. Open the **Actions** tab, pick "Update solar prices daily", click **Run workflow** once to test.
3. From then on it runs every morning at 9 AM Pakistan time and updates `prices.json`.
   Lines starting with `CHECK:` in the run log are prices that need a look (layout changed, or a big jump).
   To add or fix a source, edit `sources.json`.

## 3. Get on Google
1. Open search.google.com/search-console, add your github.io address as a **URL prefix** property.
2. Choose the **HTML tag** method, copy the `<meta name="google-site-verification" ...>` tag,
   paste it into `index.html` right after `<head>`, commit, then click Verify.
3. Submit your site address under **Sitemaps** / **URL inspection → Request indexing**.

## 4. Android app (free)
- People open the site in Chrome on Android, tap ⋮ and choose **Install app** / **Add to Home screen**.
- For the Play Store later: go to pwabuilder.com, enter your site address, download the Android package,
  and upload it with a Google Play developer account (one-time fee of about $25).

## Notes
- Every price shows its source link and date. If any site asks you to stop using its prices, remove it from `sources.json`.
- Prices are estimates; always tell visitors to confirm with the seller.
