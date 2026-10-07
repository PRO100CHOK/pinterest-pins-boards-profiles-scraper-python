# Pinterest Pins, Boards & Profiles Scraper — Python Example

> Search Pinterest pins, export boards and sections, pull creator profiles and download image or video URLs from Python, with no Pinterest login or API key.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

This repository is a ready-to-run Python project built around the [Pinterest Full Scraper actor on Apify](https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python). One actor gives you **seven Pinterest data types**: keyword search, single pin details, profiles, a user's pins, boards with their pins, board sections and related pins. Every type comes back as flat JSON that you can load straight into pandas.

## What this does

Pinterest's official API v5 works well for managing your own pins and ads. It requires an approved developer app and OAuth, and it is not built for researching what other accounts publish or what ranks for a keyword. This actor reads the same public data a logged-out visitor sees on pinterest.com and returns it as structured records. You don't need an account, a cookie or a developer token.

You put keywords, pin URLs, profile URLs, board URLs, bare pin IDs or `@usernames` in `items` and choose a `scrapeType`. The actor paginates each input until it reaches `maxResults` or the feed runs out. Each record carries a `dataType` (`pin`, `profile`, `board`, `section`), the `scrapeType` that produced it and the `input` it came from, so multi-keyword runs are easy to split afterwards.

### Images, GIFs and videos labelled correctly

Pinterest keeps GIFs, video pins and Idea/Story pins in different parts of its data, and many scrapers label them wrongly. This actor checks every media subtree by file type and returns one reliable `media_type` (`image`, `gif` or `video`). Video pins include a direct MP4 `video_url`, an HLS `video_hls_url`, `video_duration_ms` and a thumbnail. Static pins include an `images` object with every resolution Pinterest offers, from thumbnail up to the original.

## Use cases

- **Keyword and trend research.** See which pins, formats and creators lead Pinterest search for your topics, and how many saves they get.
- **Traffic-source discovery.** Every pin has an outbound `link` and `domain`, so you can rank the blogs and shops that Pinterest traffic actually goes to.
- **Creator partnerships.** Search with `searchScope: "users"`, or collect the pinners behind top pins, then pull follower, pin and board counts plus the creator's website.
- **Competitor audits.** Export a brand's pins and boards to see which boards and outbound pages get the most saves.
- **Moodboards and asset collection.** Export an entire board, including its sections, with full-resolution image URLs.
- **Video content research.** Search video pins only and get MP4 links and durations.
- **Content ideation.** Start from one strong pin and expand it with Pinterest's related-pins feed.

## Requirements

- Python **3.10+**
- A free [Apify account](https://console.apify.com/sign-up). Each month includes $5 of usage credit.
- No Pinterest account, login or API key

## Quick start

```bash
git clone https://github.com/pro100chok/pinterest-pins-boards-profiles-scraper-python.git
cd pinterest-pins-boards-profiles-scraper-python
pip install -r requirements.txt
cp .env.example .env
# paste your APIFY_API_TOKEN into .env
python main.py
```

`main.py` runs a **niche audit** for a home-decor brand:

1. It searches three keywords and collects 150 pins for each.
2. It ranks outbound domains by total saves.
3. It compares the average saves per pin for images, GIFs and videos.
4. It runs `profile` mode on the 15 creators with the most saves to get their followers, pin and board counts, and website.

The creator list goes to `output.csv`. The domain ranking, format mix, creators and raw pins go to `output.json`. To audit a different niche, change `KEYWORDS`.

## How it works

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_API_TOKEN"])
run = client.actor("pro100chok/pinterest-scraper-all-in-one").call(run_input={
    "scrapeType": "board",
    "items": ["https://www.pinterest.com/ikeausa/kitchen-inspiration/"],
    "includeBoardPins": True,
    "maxResults": 200,
})
for rec in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(rec["dataType"], rec.get("title") or rec.get("name"), rec.get("repin_count"))
```

The `scrapeType` value decides what each entry in `items` should be:

| `scrapeType` | Put in `items` | You get |
|---|---|---|
| `search` | keywords | pins, video pins, boards or profiles, depending on `searchScope` |
| `pinDetail` | pin URLs or IDs | one full pin record per input |
| `profile` | profile URLs or `@username` | one profile record per input |
| `userPins` | profile URLs or `@username` | the user's pins |
| `board` | board URLs | the board record, followed by its pins |
| `boardSections` | board URLs | one record per section |
| `relatedPins` | pin URLs or IDs | Pinterest's "more like this" pins |

## Example output

A pin record, shortened:

```json
{
  "dataType": "pin",
  "id": "1234567890",
  "url": "https://www.pinterest.com/pin/1234567890/",
  "title": "Minimal home office",
  "media_type": "image",
  "image": "https://i.pinimg.com/originals/...jpg",
  "images": {"236x": "...", "474x": "...", "736x": "...", "orig": "..."},
  "dominant_color": "#d9c7b8",
  "repin_count": 4210,
  "comment_count": 18,
  "reaction_count": 312,
  "link": "https://example.com/article",
  "domain": "example.com",
  "pinner_username": "studio.nord",
  "pinner_followers": 58200,
  "board_name": "Workspaces",
  "board_url": "https://www.pinterest.com/studio.nord/workspaces/",
  "created_at": "Tue, 04 Mar 2025 10:11:00 +0000",
  "scrapeType": "search",
  "input": "home office ideas"
}
```

**Profile** records include `full_name`, `about`, `website`, `location`, `follower_count`, `following_count`, `pin_count`, `board_count`, `video_pin_count`, `is_verified_merchant` and profile image URLs. **Board** records include `name`, `description`, `pin_count`, `follower_count`, `section_count`, `owner_username`, `privacy`, collaborator info and `image_cover`. **Section** records include `title`, `slug`, `pin_count` and `board_id`. When Pinterest leaves a field empty, the field is left out of the record.

## Input parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `scrapeType` | string | `search` | `search`, `pinDetail`, `profile`, `userPins`, `board`, `boardSections`, `relatedPins` |
| `items` | string[] | — | Keywords for search. Pin, profile or board URLs, pin IDs or `@usernames` for the other modes. |
| `maxResults` | integer | `100` | Max records per input, 1–100,000. Profiles and single pins always return one record. |
| `searchScope` | string | `pins` | Search mode only: `pins`, `videos`, `boards`, `users`. |
| `searchFilters` | string | — | Optional raw Pinterest filter string for advanced search refinement. |
| `includeBoardPins` | boolean | `true` | Board mode: return the board's pins after the board record. |
| `maxRetries` | integer | `5` | Retries per input on transient network errors. |
| `proxyConfiguration` | object | Residential, US | Apify proxy settings. The default works; custom proxies are supported. |

## More examples

| File | What it shows |
|---|---|
| `examples/01_basic_usage.py` | Keyword search with saves, media type and outbound link. |
| `examples/02_board_with_sections.py` | A board's sections, metadata and top pins. |
| `examples/03_video_pins_and_related.py` | Video-only search with MP4 URLs, then related pins for the best video. |
| `examples/04_export_to_csv.py` | A brand account audit in pandas (saves by board, domain and format) exported to CSV. |
| `examples/05_export_to_google_sheets.py` | A weekly keyword-position tracker in a Google Sheet. |

## Ready-made tasks

These are preconfigured runs on Apify. Open one and click Start:

- [Search Pinterest pins for any keyword](https://apify.com/pro100chok/pinterest-search-pins-by-keyword?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python)
- [Find Pinterest creators and brands in a niche](https://apify.com/pro100chok/pinterest-find-creators-in-niche?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python)
- [Export every pin from a Pinterest account](https://apify.com/pro100chok/pinterest-scrape-all-pins-from-user?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python)
- [Export a Pinterest board and all its pins](https://apify.com/pro100chok/pinterest-export-board-with-pins?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python)
- [Discover related pins for content ideas](https://apify.com/pro100chok/pinterest-related-pins-discovery?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python)

## Pricing

The actor charges pay-per-result with no subscription. Prices per 1,000 records:

| Record | Free plan | Paid plans (from) |
|---|---|---|
| Pin (search, user pins, board pins, related) | $3.00 | $1.00 |
| Board section | $4.00 | $1.50 |
| Board | $6.00 | $2.00 |
| Pin detail | $5.00 | $3.00 |
| Profile | $5.00 | $3.00 |

There is also a $0.00005 fee each time the actor starts. Proxies are included in these prices. On the Free plan, the $5 monthly credit pays for about 1,600 pins.

## FAQ

**Do I need a Pinterest account or API access?**
No. The actor only reads public Pinterest data. You need an Apify API token and nothing else.

**How is this different from Pinterest API v5?**
API v5 is for managing your own content and needs an approved app and OAuth. This actor lets you research any public pin, board, profile or keyword.

**Can I download full-size images and videos?**
Yes. `image` is the largest rendition, `images` lists every size, and video pins include an MP4 `video_url` and an HLS `video_hls_url`.

**What engagement data do I get?**
You get `repin_count` (saves), `comment_count`, `share_count`, `reaction_count` and a `reactions` breakdown when Pinterest provides them. The actor collects comment counts but not comment text.

**How do I get pins from a whole board, including sections?**
Use `board` mode with `includeBoardPins: true` to get the board and its pins, and `boardSections` mode to list the board's sections. `examples/02_board_with_sections.py` does both.

**Why did I get fewer results than `maxResults`?**
Some keywords and boards have fewer public pins than the cap you set. Pinterest also mixes non-pin modules into its feeds, and the actor filters those out.

**Am I charged for inputs that return nothing?**
No. You pay only for records added to the dataset, plus the start fee.

## Related actors

- [Instagram Scraper API — Profiles, Posts, Reels](https://apify.com/pro100chok/instagram-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python) — the other big visual platform, with bio emails for creators.
- [TikTok Profile API Scraper + Contacts](https://apify.com/pro100chok/tiktok-profile-pro?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python) — creator stats and contacts on TikTok.
- [RedNote Xiaohongshu Scraper](https://apify.com/pro100chok/rednote-xiaohongshu-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python) — notes and transcripts from RedNote, a lifestyle discovery app often compared to Pinterest.
- [YouTube Scraper API](https://apify.com/pro100chok/youtube-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python) — videos, Shorts, comments and channel emails.
- [Website Contact Scraper](https://apify.com/pro100chok/extract-emails?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python) — finds emails and phone numbers on the websites that pins and creators link to.

## License

MIT. See [LICENSE](LICENSE). Use the data in line with Pinterest's terms and the privacy laws that apply to you.

---

Built by [pro100chok](https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python) on Apify.
