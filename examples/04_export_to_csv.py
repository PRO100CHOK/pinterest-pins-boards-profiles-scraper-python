"""Audit a brand's Pinterest account with pandas and export it to CSV.

Pulls a user's pins and writes output.csv, then prints which boards and which
outbound domains collect the most saves, and how the format mix performs.

Actor: https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python
"""
import os

import pandas as pd
from apify_client import ApifyClient
from dotenv import load_dotenv

ACCOUNT = "@ikeausa"

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/pinterest-scraper-all-in-one").call(run_input={
    "scrapeType": "userPins",
    "items": [ACCOUNT],
    "maxResults": 300,
})
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
if not items:
    raise SystemExit("No pins returned.")

df = pd.DataFrame(items)
for col in ("repin_count", "comment_count", "board_name", "domain", "media_type"):
    if col not in df.columns:
        df[col] = None
df["repin_count"] = df["repin_count"].fillna(0).astype(int)
cols = ["id", "title", "media_type", "repin_count", "comment_count", "board_name",
        "domain", "link", "image", "video_url", "created_at", "url"]
df[[c for c in cols if c in df.columns]].sort_values("repin_count", ascending=False) \
    .to_csv("output.csv", index=False)

print("Saves by board:")
print(df.groupby("board_name")["repin_count"].agg(["count", "sum"])
      .sort_values("sum", ascending=False).head(10))
print("\nSaves by outbound domain:")
print(df.groupby("domain")["repin_count"].sum().sort_values(ascending=False).head(10))
print("\nFormat mix:")
print(df.groupby("media_type")["repin_count"].agg(["count", "mean"]).round(1))
print(f"\nSaved {len(df)} pins to output.csv")
