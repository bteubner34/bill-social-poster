# Bill Teubner — 16-Day Social Media Auto-Poster

Standalone Python cron job that publishes daily social content to Instagram and LinkedIn via the Zernio API. Runs automatically on Render at **3:45 AM MST every day**.

---

## How It Works

1. On each run, the script calculates which day of the 16-day calendar it is (Day 1 = May 26, 2026)
2. It retrieves the correct business and personal graphics (from CDN or local `graphics/` folder)
3. It publishes both posts to Instagram (@bill.teubner) and LinkedIn simultaneously via Zernio
4. Logs the result — success or error — to Render's log dashboard

---

## Deploy to Render (One-Time Setup)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
gh repo create bill-social-poster --private --push --source=.
```

### Step 2 — Create Render Cron Job

1. Go to [render.com](https://render.com) and sign in (free account)
2. Click **New** → **Cron Job**
3. Connect your GitHub repo (`bill-social-poster`)
4. Render will auto-detect `render.yaml` and configure everything
5. Click **Create Cron Job**

That is it. Render will run `python post.py` every day at 10:45 AM UTC (3:45 AM MST).

---

## Graphic Files

Pre-uploaded CDN URLs are embedded in `post.py` for Day 1. For Days 2–16, place the graphic files in a `graphics/` subfolder:

```
graphics/
  day2_business_aso.png
  day2_personal_rockclimbing.png
  day3_business_content.png
  ... (all 32 files)
```

The script will auto-crop each image to 4:5 ratio before uploading to Zernio.

---

## Environment Variables (already set in render.yaml)

| Variable | Value |
|---|---|
| `ZERNIO_KEY` | Zernio API key |
| `IG_ACCOUNT` | Instagram account ID in Zernio |
| `LI_ACCOUNT` | LinkedIn account ID in Zernio |

---

## Manual Test Run

```bash
pip install -r requirements.txt
npm install -g @zernio/cli
zernio auth:set --key YOUR_KEY
python post.py
```
