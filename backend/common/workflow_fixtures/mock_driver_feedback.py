"""
50-entry driver feedback pool covering the full emotional spectrum.
Each message is normalized into a single quote block:
1) difficulty or trip condition context
2) solution, support, or operational need

Each tuple: (message: str, trip_rating: int, fatigue_self_report: str)
  trip_rating        1–5
  fatigue_self_report  "none" | "mild" | "moderate" | "severe"
"""

from __future__ import annotations

import re


def _sentence_count(text: str) -> int:
    return len(re.findall(r"[.!?](?:\s|$)", text.strip()))


def _ensure_first_paragraph_detail(message: str, trip_rating: int, fatigue: str) -> str:
    paragraph = message.strip()
    if _sentence_count(paragraph) >= 3:
        return paragraph

    if trip_rating <= 2:
        paragraph += (
            " The pressure is making routine decisions feel heavier than they should."
        )
    elif trip_rating == 3:
        paragraph += " I can still complete the route safely, but it takes more concentration than usual."
    else:
        paragraph += " Even on better days, I still notice moments that require extra discipline and focus."

    if _sentence_count(paragraph) < 3:
        if fatigue in {"moderate", "severe"}:
            paragraph += " Fatigue is part of the reason my attention feels stretched by the end of the shift."
        else:
            paragraph += " Better pacing through the shift would help me stay consistent from start to finish."

    return paragraph


def _support_paragraph(trip_rating: int, fatigue: str) -> str:
    fatigue_needs = {
        "none": "What helps most is keeping route plans predictable and dispatch communication clear so small delays do not escalate.",
        "mild": "I would benefit from slightly better pacing between assignments and a short reset window after congested segments.",
        "moderate": "I need tighter workload balancing, clearer contingency plans, and more reliable handover timing to reduce cumulative stress.",
        "severe": "I need immediate schedule relief, protected recovery time, and closer check-ins before and after demanding runs.",
    }

    if trip_rating <= 2:
        rating_needs = "For now, a temporary reduction in back-to-back high-pressure trips would make the work safer and more sustainable."
    elif trip_rating == 3:
        rating_needs = "A steadier sequence of stops and realistic buffers would help keep performance stable across the full shift."
    else:
        rating_needs = "Maintaining the current planning discipline and preventive checks will help preserve this level of performance."

    return (
        f"{fatigue_needs[fatigue]} "
        f"{rating_needs} "
        "Regular debriefs after difficult routes and practical support from operations would improve long-term consistency."
    )


def _normalize_feedback_message(message: str, trip_rating: int, fatigue: str) -> str:
    first_paragraph = _ensure_first_paragraph_detail(message, trip_rating, fatigue)
    second_paragraph = _support_paragraph(trip_rating, fatigue)
    return f"{first_paragraph} {second_paragraph}"


_BASE_FEEDBACK_POOL: list[tuple[str, int, str]] = [
    # ── Negative / distressed (1–20) ─────────────────────────────────────────
    (
        "I've been doing this job for years, but lately it feels like everything is stacked against me. "
        "The schedules are tighter, the roads are worse, and no one seems to care what it takes to get from point A to B safely. "
        "I find myself getting irritated over small things, and that's not who I used to be. "
        "By the time I finish a shift, I'm mentally drained and physically exhausted. "
        "It's not just the driving — it's the constant pressure. I don't feel like I get enough time to reset before the next run.",
        2,
        "moderate",
    ),
    (
        "Every time I get behind the wheel now, there's this constant sense of unease. "
        "I double-check everything more than I used to, and even then, I don't feel confident. "
        "It's like I'm waiting for something to go wrong. "
        "I don't sleep well anymore either. My mind keeps replaying worst-case scenarios, "
        "and I wake up already tired. It's affecting how I drive, and honestly, it scares me.",
        2,
        "severe",
    ),
    (
        "I feel like I'm running on empty most days. The long hours and back-to-back trips are catching up with me, "
        "and I don't think I've had a proper rest in weeks. Even coffee doesn't help anymore. "
        "Sometimes I wonder how long I can keep doing this. I used to enjoy the road, "
        "but now it just feels like something I have to survive rather than something I'm good at.",
        1,
        "severe",
    ),
    (
        "There's this frustration that's been building up inside me. It feels like no matter how hard I try, it's never enough. "
        "The expectations keep rising, but the support doesn't. "
        "I try not to let it show, but it's getting harder. I'm more on edge, more impatient, and I don't like what that's doing to me.",
        2,
        "moderate",
    ),
    (
        "Lately, I've been feeling low during my trips. It's hard to explain, but there's this heaviness that follows me, "
        "even on routes I used to enjoy. It's like something's missing. "
        "I keep pushing through because that's what I'm supposed to do, but inside, I feel disconnected. "
        "It's not just physical fatigue — it's something deeper.",
        2,
        "mild",
    ),
    (
        "Driving used to feel routine, something I could handle without thinking too much. "
        "Now, I'm constantly alert, almost to the point where it's exhausting. Every sound, every movement makes me tense. "
        "By the end of the day, I feel completely worn out — not just physically, but mentally. "
        "It's like my mind never gets a break.",
        3,
        "moderate",
    ),
    (
        "I've started getting irritated more easily on the road. Small things that didn't bother me before now feel like a big deal. "
        "It's frustrating because I know I shouldn't react this way. "
        "I think it's the stress building up over time. There's no real outlet for it, so it just sits there and grows.",
        2,
        "mild",
    ),
    (
        "There's always this feeling that something might go wrong. Even when everything is fine, I can't shake that thought. "
        "It keeps me alert, but it also drains me. It's like being on edge all the time. "
        "There's a constant pressure to keep moving, to stay on schedule no matter what. "
        "It doesn't leave much room to breathe or think.",
        3,
        "moderate",
    ),
    (
        "I don't feel as sharp as I used to. There are moments when I catch myself zoning out, and that worries me. "
        "This job doesn't allow for mistakes. I try to compensate by being extra careful, "
        "but that just adds to the exhaustion. It's a cycle I can't seem to break.",
        2,
        "severe",
    ),
    (
        "Some days, I just feel overwhelmed. The responsibility, the isolation, the long hours — it all piles up. "
        "It's not easy to carry that alone. "
        "I don't really talk about it much, but it's there. And it's getting harder to ignore.",
        2,
        "moderate",
    ),
    (
        "There's a lot of anger sitting under the surface lately. It's not directed at anyone in particular — it's just there. "
        "Maybe it's the pressure, maybe it's the lack of rest. "
        "I don't like feeling this way. It makes the job harder, and it's not who I want to be.",
        2,
        "mild",
    ),
    (
        "I've been feeling anxious before every trip. It's like a knot in my stomach that doesn't go away until I'm done. "
        "Even then, it lingers. It's affecting how I approach the job. "
        "I'm more cautious, but also more tense, and that's tiring in its own way.",
        2,
        "moderate",
    ),
    (
        "The fatigue is real. It's not just being tired — it's feeling like your body hasn't fully recovered no matter how much you rest. "
        "I push through because I have to, but I know it's not sustainable like this.",
        2,
        "severe",
    ),
    (
        "I feel disconnected from everything when I'm on the road. It's just me, the truck, and the distance ahead. It gets lonely. "
        "That loneliness turns into something heavier over time. It's not easy to shake off.",
        3,
        "mild",
    ),
    (
        "I've been snapping more than usual. Little delays or issues set me off, and I regret it afterward. "
        "It's not how I used to handle things. I think it's the stress catching up with me. "
        "There's only so much you can carry before it starts spilling over.",
        2,
        "moderate",
    ),
    (
        "There's always this feeling that something might go wrong. Even when everything is fine, I can't shake that thought. "
        "It keeps me alert, but it also drains me. It's like being on edge all the time.",
        3,
        "mild",
    ),
    (
        "I don't feel rested anymore, no matter how much I sleep. "
        "It's like my body is always catching up but never quite gets there. "
        "That kind of fatigue makes everything harder — focus, patience, even simple decisions.",
        2,
        "severe",
    ),
    (
        "I've been feeling down more often than not. It's not tied to one thing — it's just a general feeling that sticks around. "
        "Driving alone gives you too much time to think, and sometimes that's not a good thing.",
        2,
        "mild",
    ),
    (
        "The frustration is building. It feels like the system expects more and more without understanding what it takes on the ground. "
        "I do my job the best I can, but it doesn't feel appreciated or supported.",
        2,
        "mild",
    ),
    (
        "I've started to dread the start of each trip. That's new for me. I used to look forward to it. "
        "Now it feels like something I have to get through rather than something I enjoy.",
        1,
        "moderate",
    ),
    # ── Mixed / neutral (21–35) ───────────────────────────────────────────────
    (
        "Today was an average day. The traffic was a bit unpredictable on the expressway, "
        "but nothing I couldn't manage. Delivered on time, no major issues.",
        3,
        "none",
    ),
    (
        "Route was okay, had a slight delay at the loading bay but caught up later. "
        "Feeling a little tired but nothing unusual for a Friday shift.",
        3,
        "mild",
    ),
    (
        "Steady trip overall. Roads were clear in the morning but got congested near the industrial area. "
        "I stayed patient and made up the time. Body feels a bit stiff after the long haul.",
        3,
        "mild",
    ),
    (
        "Not my best drive, not my worst either. Bit of a slow start due to vehicle check, "
        "but everything was fine once I got moving. Mild fatigue toward the end.",
        3,
        "mild",
    ),
    (
        "Mixed feelings about today. The route itself was fine but had a near-miss at a junction — "
        "another driver cut in without signalling. Shook me up a bit, but I handled it.",
        3,
        "moderate",
    ),
    (
        "Nothing special to report. Routine trip, familiar roads, on-time delivery. "
        "Feeling a bit flat but that might just be the midweek slump.",
        3,
        "none",
    ),
    (
        "Decent drive. Weather was overcast which made visibility harder than usual, "
        "but I kept my speed down and stayed alert. A bit tired from yesterday's late finish.",
        3,
        "mild",
    ),
    (
        "Managed the route fine today. Had one road diversion that added about 15 minutes, "
        "but I found an alternate route quickly. Not great, not bad.",
        3,
        "none",
    ),
    (
        "Feeling okay today. The vehicle behaved well, no warning lights. "
        "Traffic was medium — not the worst I've seen. Arrived a few minutes early.",
        4,
        "none",
    ),
    (
        "Had a passenger with me for part of the route — a new driver in training. "
        "Made me more conscious of my habits, which is a good thing. Mild fatigue from the extra focus.",
        4,
        "mild",
    ),
    (
        "Productive trip. A bit of congestion at Jurong but moved through it steadily. "
        "Energy level was moderate — not my sharpest day, but I got the job done safely.",
        3,
        "mild",
    ),
    (
        "Route was smooth in the morning, picked up some delays after noon. "
        "Overall I stayed calm and managed my stops well. Feeling a little stiff but nothing concerning.",
        3,
        "none",
    ),
    (
        "Today felt balanced. No major incidents, good communication with dispatch, "
        "and the vehicle performed reliably. Mild tiredness at the end but nothing unusual.",
        4,
        "mild",
    ),
    (
        "It was an okay day. I had one moment of frustration when a cargo delay pushed my schedule back, "
        "but I adapted and made up the time. Feeling fine overall.",
        3,
        "none",
    ),
    (
        "The morning was rough — heavy rain and reduced visibility near Woodlands — "
        "but the afternoon cleared up and I completed the run without issues. "
        "Moderate fatigue from driving in poor weather.",
        3,
        "moderate",
    ),
    # ── Positive / good (36–50) ───────────────────────────────────────────────
    (
        "Great trip today. Roads were clear, timing was spot on, and I felt confident the whole way. "
        "This is why I enjoy this job — when everything clicks, it's genuinely satisfying.",
        5,
        "none",
    ),
    (
        "Really pleased with today's run. New route turned out to be faster than I expected, "
        "and the truck handled it well. Arrived 20 minutes early. Feeling fresh and positive.",
        5,
        "none",
    ),
    (
        "Excellent conditions today. Light traffic, good weather, smooth delivery. "
        "I felt sharp and in control the entire trip. Days like this remind me why I chose this work.",
        5,
        "none",
    ),
    (
        "Had a really productive day. Managed all three deliveries on time, no vehicle issues, "
        "and found a shortcut that saved about 10 minutes. Happy with how it went.",
        5,
        "none",
    ),
    (
        "Feeling positive after today's run. The route was challenging in parts, "
        "but I navigated it well and stayed calm throughout. Good energy from start to finish.",
        5,
        "none",
    ),
    (
        "One of the better shifts I've had recently. Light load, familiar route, "
        "and the roads cooperated. I felt relaxed and focused the whole way.",
        5,
        "none",
    ),
    (
        "Good drive overall. I had a brief moment of uncertainty near a construction zone, "
        "but I slowed down, reassessed, and moved through safely. Feeling confident.",
        4,
        "none",
    ),
    (
        "Today went smoothly. Traffic was manageable, the handover at the dock was quick, "
        "and I kept good momentum throughout. Mild fatigue at the very end but nothing concerning.",
        4,
        "mild",
    ),
    (
        "Really enjoyed today's drive. The early start meant less traffic, "
        "and I made excellent time on the expressway. Felt energised and in the zone.",
        5,
        "none",
    ),
    (
        "Good shift. The vehicle felt responsive, the route was well-planned, "
        "and I got through without any delays. A bit of tiredness after a full day, but overall very positive.",
        4,
        "mild",
    ),
    (
        "Felt sharp and alert today. No distractions, no incidents. "
        "I took the new coastal route for the first time and it was genuinely enjoyable — less stop-start than the main road.",
        5,
        "none",
    ),
    (
        "Very smooth run from start to finish. Clear skies, light load, and I was fully rested going in. "
        "Delivered ahead of schedule and the client was happy. A great end to the week.",
        5,
        "none",
    ),
    (
        "Happy with how I handled today. There was a small incident on the expressway — "
        "a stalled vehicle causing a slowdown — but I anticipated it early and rerouted without losing time.",
        4,
        "none",
    ),
    (
        "Good day on the road. I felt calm and in control the whole shift, "
        "even when the final drop-off location was harder to access than the map showed. Problem-solved it well.",
        4,
        "none",
    ),
    (
        "Couldn't have asked for a better shift. New truck, open roads, and a manageable schedule. "
        "I finished early, the cargo was secure throughout, and I'm heading home feeling genuinely good about the day.",
        5,
        "none",
    ),
]


FEEDBACK_POOL: list[tuple[str, int, str]] = [
    (_normalize_feedback_message(message, rating, fatigue), rating, fatigue)
    for message, rating, fatigue in _BASE_FEEDBACK_POOL
]
