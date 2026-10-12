# AdScript Studio

An AI agent that turns a short brief into high-converting **copywriting
deliverables** - video ad scripts, landing pages, online ads, emails, sales
letters and more - each backed by a consumer-psychology strategy brief and
delivered through a private Telegram bot, powered by a **local** Qwen model.

Built as an internal, done-for-you tool: you generate copy for your clients,
review it, and deliver. 100% local inference, no per-request API cost.

**11 formats across 4 categories:**

| Category | Formats |
|---|---|
| Webmarketing | Landing Page, E-commerce Product Sheet, Online Ad (FB/Google/LinkedIn/IG) |
| Loyalty & Engagement | Email / Newsletter, Social Post (LinkedIn/IG), Paid / Private Newsletter |
| Audio & Visual | Video Ad (30s), Podcast Script |
| Traditional Media | Flyer / Brochure, Poster / Slogan, Sales Letter |

---

## How it works

```
Telegram user
   |  /start -> pick a category -> pick a format -> guided form
   |           (brand -> product -> details -> audience -> goal -> [format extras] -> tone)
   v
bot.py  (python-telegram-bot, async ConversationHandler)
   |  collects the brief, runs the pipeline in a worker thread
   v
pipeline.run_for_format(format_key, brief)
   |  two-agent chain (prompts_formats.py builds the messages)
   |-- Agent 1 STRATEGIST   -> Ollama /api/chat (JSON)  -> validate + retry/fallback
   |-- Agent 2 WRITER       -> Ollama /api/chat (text)  -> model fallback
   v
renderer.py -> Telegram markdown + 4096-char safe splitting
   v
User receives: STRATEGY BRIEF + the deliverable in the chosen format
   |
   |  "Client PDF" / "Full report PDF" buttons
   v
exporter.py -> branded, client-ready PDF (format-aware layout)
```

`formats.py` is the single source of truth for the 11 formats and the extra
questions each one asks; `prompts_formats.py` holds the per-format prompts
(the original video-ad prompts in `prompts.py` are reused unchanged).

## Files

| File | Purpose |
|---|---|
| `bot.py` | Telegram UI, category/format selector, guided form, threaded pipeline, startup health check + warmup, logging |
| `formats.py` | Registry: the 11 formats, their categories, and per-format extra form fields |
| `pipeline.py` | Orchestrates the two agents (`run_for_format`), validates strategy, retries, model fallback |
| `prompts.py` | The original Video Ad strategist/writer prompts + shared quality core |
| `prompts_formats.py` | Per-format prompt specs for all 11 formats (video_ad delegates to `prompts.py`) |
| `ollama_client.py` | Thin Ollama client: chat, JSON mode, retries, friendly errors |
| `renderer.py` | Formats results for Telegram (format-aware labels) and splits long messages |
| `exporter.py` | Builds branded client/operator PDFs (video-ad layout + generic markdown layout) |
| `config.py` | Loads `.env`; model, temps, timeouts, allowlist |
| `samples/` | 9 ready-to-send portfolio samples across video ad, landing page, online ad, email, sales letter (PDF + Markdown) |
| `marketing/` | Pricing menu (MD + PDF) and DM/e-mail templates |
| `register_autostart.ps1` | Registers the bot to run hidden at logon (Task Scheduler) |
| `unregister_autostart.ps1` | Removes the autostart task |
| `TEST_CHECKLIST.md` | Step-by-step live test script |
| `BRIEF_TEMPLATE.md` | How to write a good brief (biggest quality lever) |
| `bot.log` | Rotating runtime log (created on first run) |

## Requirements

- Windows, Python 3.12
- [Ollama](https://ollama.com) installed
- Python packages: `pip install -r requirements.txt`

## Setup

1. **Pull the model**
   ```
   ollama pull qwen2.5:3b
   ```
2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
3. **Create the bot and get a token** (Telegram -> @BotFather -> `/newbot`).
4. **Configure `.env`** in the project folder:
   ```
   BOT_TOKEN=<your token>
   OLLAMA_HOST=http://localhost:11434
   MODEL=qwen2.5:3b
   FALLBACK_MODEL=qwen2.5-coder:3b
   ALLOWED_USER_IDS=
   ```

## Run

```
cd C:\Users\bilel\Bureau\adscript-bot
python bot.py
```

In Telegram, open your bot and send `/start`. Pick a category, then a format,
then answer the form questions (the last questions change per format).

Commands: `/start` (or `/script`) begin, `/cancel` stop, `/help` help, `/id` show your Telegram ID.

## Deliver & export (PDF)

After a deliverable is generated, the bot shows two buttons:

- **Client PDF** - a clean, branded deliverable in the chosen format, no internal strategy.
- **Full report PDF** - the client view plus the strategy brief (for your own use).

The Video Ad format keeps its original layout (beats + shot-list table); every
other format is rendered from its markdown headings, bullets and bold labels.

PDFs use Windows Arial for full French accents, and fall back to a built-in font
otherwise. Generation never fails because of a PDF error - you just get a message.

## Selling with this tool

You sell the **copy** (done-for-you), not the bot. Ready-made assets:

- `samples/` - 9 polished samples: 5 video ads plus a landing page, online ad,
  email and sales letter, covering **French and English**. Send one as a free
  sample to prospects. Rebuild anytime with `python samples/build_samples.py`.
- `marketing/pricing-menu.md` / `pricing-menu.pdf` - your offers. Edit the price and
  contact placeholders, then rebuild with `python marketing/build_pricing_pdf.py`.
- `marketing/dm-templates.md` - French + English first-touch and follow-up messages.

## Autostart (optional)

Runs the bot hidden at logon and restarts it if it crashes.

```
powershell -ExecutionPolicy Bypass -File register_autostart.ps1
```

Start it immediately without rebooting:

```
Start-ScheduledTask -TaskName AdScriptBot
```

Remove it:

```
powershell -ExecutionPolicy Bypass -File unregister_autostart.ps1
```

Ollama should also start at logon (the Ollama desktop app does this by default);
the bot will try to launch `ollama serve` itself if it is not running.

## Security

- The bot is **open to everyone** until you set `ALLOWED_USER_IDS`.
- Send `/id` to the bot, then put that number in `.env`: `ALLOWED_USER_IDS=123456789`
  (comma-separate multiple IDs). Restart the bot.
- `BOT_TOKEN` lives only in `.env`, which is git-ignored. Never commit it.
- Briefs and generated scripts never leave your machine except as Telegram messages.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Logs "Ollama is still unreachable" | Run `ollama serve`, confirm `OLLAMA_HOST`. |
| Logs "Model ... is not installed" | `ollama pull qwen2.5:3b`. |
| Bot silent in Telegram | Check `bot.log`; verify token with a `getMe` call. |
| Telegram markdown error | Auto-fallback to plain text; check `bot.log`. |
| First script is slow | Wait for "Model warmup complete" in `bot.log`. |
| Bot won't autostart | Re-run `register_autostart.ps1`; check Task Scheduler for `AdScriptBot`. |

## Customization

- **Swap model:** change `MODEL` / `FALLBACK_MODEL` in `.env` (e.g. `qwen2.5:7b`).
- **Tune creativity:** `STRATEGIST_TEMPERATURE` (lower = more precise) and
  `WRITER_TEMPERATURE` (higher = more creative) in `config.py`.
- **Change the output style:** edit the per-format prompts in `prompts_formats.py`
  (video ad in `prompts.py`).
- **Add or edit a format:** edit `FORMATS` and `FORMAT_EXTRA_FIELDS` in `formats.py`,
  then add its spec in `prompts_formats.py`. The bot menus, form and PDF follow along.

## Roadmap

- [x] Phase 0 - Scaffold
- [x] Phase 1 - Ollama client
- [x] Phase 2 - Prompts
- [x] Phase 3 - Two-agent pipeline
- [x] Phase 4 - Telegram bot
- [x] Phase 5 - Autostart, health check, warmup, logging, docs
- [x] Expansion 1 - Format registry + per-format prompts
- [x] Expansion 2 - Telegram category/format UI + form extras
- [x] Expansion 3 - Per-format examples for all 11 formats
- [x] Expansion 4 - Format-aware PDF export
- [x] Expansion 5 - Samples, templates and docs
- [ ] V2 - Monthly subscription / SaaS (multi-user, billing)
