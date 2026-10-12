# COMPREHENSIVE PLAN: Multi-format Copywriting Expansion

## Mission
Expand the Telegram local bot from video-ad only to a complete copywriting agent covering all requested formats while preserving existing video ad functionality.

## 1) Architecture overview
- Keep: bot.py (Telegram UI), pipeline.py (2-agent: Strategist JSON -> Scriptwriter markdown), ollama_client.py, renderer.py, exporter.py, config.py, prompts.py
- Add: formats.py (registry + schemas), prompts_formats.py (per-format prompts), renderer_formats.py (optional), exporter_formats.py (layout per format)
- Generalize pipeline: add run_for_format(format, brief) while keeping run_pipeline() for VIDEO_AD (backward compat)
- UI: format selector (/start) -> submenu per category -> format-specific flow

## 2) Formats to support
A) Webmarketing: Landing page (conversion), E-commerce product sheet (specs->benefits), Online ads (FB/Google/LinkedIn/IG)
B) Loyalty/Engagement: Emails/newsletters (subject+body), Social posts (LinkedIn/IG), Paid/private newsletters
C) Audio/Visual: Video ads (upgrade existing), Podcast scripts (intro/transitions/segments)
D) Traditional: Flyers/brochures, Posters/slogans, Sales letters

## 3) Bot UX
- /start -> choose category -> choose format
- Reuse: brand/product/details/audience + format-specific fields
- After generation: show internal + client views, PDF export per format
- Keep /cancel /help /id

## 4) Prompts strategy
Per format use 2-agent (strategy JSON -> tailored output) with EN/FR, strict rules, avoid hallucinations, consistent tone/register.

## 5) PDF export
Extend exporter.py with format-aware layouts. Video keeps current; others use structured sections.

## 6) Implementation phases
Phase 1: Foundation (formats.py, prompts_formats.py, pipeline generalization)
Phase 2: UI (format selector + flows)
Phase 3: Webmarketing + Loyalty/Engagement
Phase 4: Audio/Visual + Traditional
Phase 5: Polish (samples, templates, README)

## 7) Next step
I need your approval to start Phase 1. Say 'go' to proceed.
