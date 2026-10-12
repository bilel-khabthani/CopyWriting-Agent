# AdScript Studio - Live Test Checklist

Run the bot first:

```
cd C:\Users\bilel\Bureau\adscript-bot
python bot.py
```

Leave that terminal open. In Telegram, open **@AdScriptAIBot** and work through
the tests below. Record PASS/FAIL and any odd output.

---

### 1. Startup health check + warmup
- **Do:** start `python bot.py` and watch the terminal / `bot.log`.
- **Expect:** lines "Ollama health check passed." and "Model warmup complete (qwen2.5:3b)."
- **If Ollama was off:** the bot tries to start it and waits up to ~15s.

### 2. Happy path (Video Ad)
- **Do:** send `/start`, then tap:
  - Category: **Audio & Visual**
  - Format: **Video Ad (30s)**
  - Brand: `SleepGuard`
  - Product: `A smartwatch that tracks sleep and warns you before you get sick.`
  - Details: `tracks sleep, warns 2 days before symptoms, 7-day battery`
  - Audience: `health-conscious adults aged 25-40`
  - Goal: tap **Sell the product**
  - Platform: tap **YouTube Shorts**
  - Product type: tap **Physical product**
  - Tone: tap **Professional**
  - Tap **Generate script**
- **Expect:** status shows "Agent 1/2 ..." then "Agent 2/2 ...", then the final
  message contains **STRATEGY BRIEF** and **VIDEO SCRIPT** with a shot-list table,
  and the CTA uses **Order/Buy now** (not "Download").

### 2b. Category / format navigation
- **Do:** `/start`; tap a category, then **Back**, then another category.
- **Do:** on the format screen, pick a format with extra questions (e.g.
  **E-commerce Product Sheet** or **Landing Page**).
- **Expect:** the Back button returns to the category list; the extra question
  (specs / offer) appears among the form steps. No crash.

### 2c. Non-video deliverable
- **Do:** `/start` -> **Webmarketing** -> **Online Ad (FB/Google/LinkedIn/IG)**;
  fill the brief, answer **Which channels?**, generate.
- **Expect:** the output uses the ad-copy shape (3 variants, each with Primary
  text / Headline / Description / CTA), in the same language as the brief.

### 2d. PDF export (format-aware)
- **Do:** after any result, tap **Client PDF**, then **Full report PDF** (open the
  files from Telegram).
- **Expect:** Client PDF has no strategy page; Full PDF adds it. A non-video format
  renders its headings/bullets/bold labels correctly (not the shot-list layout).

### 3. Cancel mid-form
- **Do:** `/start`, send a product, then `/cancel`.
- **Expect:** "Cancelled." No script generated.

### 4. Empty / garbage input
- **Do:** `/start`, then send a single space or `...`.
- **Expect:** the bot still advances (it stores the text). No crash.
  *(Note: it does not validate meaning, only presence.)*

### 5. Forced model fallback
- **Do:** stop the bot. In `.env` set `MODEL=qwen2.5:doesnotexist`, keep
  `FALLBACK_MODEL=qwen2.5-coder:3b`. Restart `python bot.py`. Run a script.
- **Expect:** several `404`/error logs, then a script produced by the fallback model.
  The meta line shows `qwen2.5-coder:3b`.
- **Then:** revert `MODEL=qwen2.5:3b` and restart.

### 6. Long output splitting
- **Do:** request an unusual brief that yields a long script (e.g. a detailed
  audience). 
- **Expect:** if the message exceeds 4096 chars it arrives as 2+ messages, none cut
  mid-table, in order.

### 7. `/id`
- **Do:** send `/id`.
- **Expect:** your numeric Telegram ID is shown.

### 8. Unauthorized user block
- **Do:** put your ID in `.env`: `ALLOWED_USER_IDS=<your_id>` (no spaces), restart.
- **Do:** from another Telegram account, send `/start`.
- **Expect:** "Sorry, this bot is private."
- **Then:** with your own account, confirm it still works.

### 9. Restart resilience
- **Do:** close the `python bot.py` terminal and, if registered, check Task Scheduler
  (`Start-ScheduledTask -TaskName AdScriptBot`). Reboot/log off+on.
- **Expect:** the bot runs hidden and responds again. `bot.log` shows a fresh startup.

### 10. Language matching (French)
- **Do:** run a full form (any format) with a **French** product/audience
  description (brand optional), then generate.
- **Expect:** the strategy brief and the deliverable are written in **French**, and
  the CTA is a French action phrase (e.g. "Commandez maintenant") - not "Download".

### 11. Samples still build
- **Do:** `python samples/build_samples.py`
- **Expect:** 9 lines "built <slug> (<format>)"; matching `.pdf` and `.md` updated
  in `samples/`. Open one non-video PDF (e.g. `atelier-lumen.pdf`) to confirm layout.

---

## Reporting

For any FAIL, copy the relevant `bot.log` lines. Most issues map to:
- Ollama down -> `ollama serve`
- Model missing -> `ollama pull qwen2.5:3b`
- Bad token -> `Telegram auth OK: False`
- Telegram markdown rejected -> the bot auto-falls back to plain text (check log).
