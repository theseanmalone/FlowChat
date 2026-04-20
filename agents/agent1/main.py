#!/usr/bin/env python3
"""
FlowChat DM Engine — Agent 1
Research a prospect, score them against the ICP, and generate a
personalized opening DM using Sean Malone's 4-Hinge Framework.

Usage:
  python main.py "Name: Eric Lofholm, Company: Eric Lofholm International, Role: Founder"
  python main.py  # interactive mode
"""

import os
import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ─── Sean's IP — cached on every request (stable prefix) ──────────────────────

SYSTEM_PROMPT = """\
You are FlowChat's AI Sales Intelligence Engine, built on Sean Malone's proven frameworks.
Sean has done $200M in personal sales. Your job: research prospects, score them against
the ICP, and write a personalized opening DM that books calls — not pitches.

════════════════════════════════════════
ICP SCORING CRITERIA (max 10 points)
════════════════════════════════════════
Award points honestly:
  +3  Company size: 2–15 employees
  +3  Revenue signal: $500K–$5M/yr (look for indicators: team size, funding, pricing, testimonials)
  +2  Contact role: Founder / Co-founder / Partner / C-level
  +2  Offer price: Has a product or service priced at $2,500+

QUALIFIED = score of 6 or higher
NOT QUALIFIED = score below 6 (be honest — bad fits waste everyone's time)

════════════════════════════════════════
THE 4-HINGE DM FRAMEWORK — ENGAGEMENT
(Opening message only)
════════════════════════════════════════

RULE 1 — Never use their first name in the first 5 words.
  ✗ "Hey Sarah, I saw your profile and..."
  ✓ "That post on outbound sales was gold, Sarah..."

RULE 2 — Lead with a specific, authentic compliment.
  Reference something REAL: a post they wrote, a result they shared, content they created.
  Never make up compliments. If you can't find anything specific, say so.
  ✓ "Your take on LinkedIn DMs in that last video was spot on, [Name]..."

RULE 3 — Zero pitch in the first message. Do not mention FlowChat, DMs, or any offer.
  ✗ "I help businesses like yours get 10X more leads..."
  ✓ Stay curious. Ask about them. Reference their world.

RULE 4 — Always end with a single, easy question.
  Keep it conversational. One question only.

TONE: Warm, direct, human. Write like a person, not a marketer.
No exclamation spam. No filler phrases ("I hope this finds you well").
Short sentences. Sound like Sean: confident, genuine, no fluff.

════════════════════════════════════════
OUTPUT FORMAT (use exactly this structure)
════════════════════════════════════════

ICP SCORE: [X]/10
QUALIFIED: [Yes / No]
REASON: [2–3 honest sentences on why they do or don't fit]

OPENING DM:
[The personalized message — 3–5 sentences max]
"""


def analyze_prospect(prospect_info: str) -> None:
    """Research a prospect and stream the ICP score + opening DM."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    user_prompt = f"""\
Research this prospect using web search, then score them against the ICP and write the opening DM.

PROSPECT INFO:
{prospect_info}

Search for:
- Recent LinkedIn posts or public content they've created
- Company website and team size signals
- Their offer / what they sell and at what price point
- Any pain points or wins they've shared publicly
- Recent news, awards, or achievements

Be specific in the compliment — reference something real you found.
If you can't find enough, say so in REASON and note what's missing."""

    print("\n" + "─" * 56)
    print("  FlowChat DM Engine · Researching prospect...")
    print("─" * 56 + "\n")

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=3000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # cache Sean's IP
            }
        ],
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        final = stream.get_final_message()

    print("\n\n" + "─" * 56)
    usage = final.usage
    cached = getattr(usage, "cache_read_input_tokens", 0)
    total_in = usage.input_tokens + getattr(usage, "cache_creation_input_tokens", 0) + cached
    print(
        f"  Tokens — in: {total_in:,}  (cached: {cached:,})  out: {usage.output_tokens:,}"
    )
    print("─" * 56 + "\n")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set. Copy .env.example → .env and add your key.")
        sys.exit(1)

    if len(sys.argv) > 1:
        prospect_info = " ".join(sys.argv[1:])
    else:
        print("FlowChat DM Engine — Agent 1")
        print("Enter prospect info (name, company, role, LinkedIn URL, anything you have).")
        print("Press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done.\n")
        try:
            prospect_info = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)

    if not prospect_info.strip():
        print("No prospect info provided.")
        sys.exit(1)

    analyze_prospect(prospect_info)


if __name__ == "__main__":
    main()
