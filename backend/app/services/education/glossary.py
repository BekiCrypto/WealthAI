"""The indicator glossary: an explicit, educational briefing for every
economic release this app tracks.

This is deliberately separate from the prediction engine's heuristic
scenario tables (CATEGORY_ASSET_IMPACT, the surprise-probability model).
Those answer "what might this release do to prices, right now, given the
current regime." This module answers a different question: "what is this
number, why does anyone watch it, and how do I read it myself" -- the
knowledge a reader needs to evaluate the app's calls rather than just trust
them. Every field is prose written to teach, not a data point to compute.

Keyed by the exact EconomicEvent.name used in the seeded calendar
(economic_calendar.py) so a lookup is a straight dict hit; get_education()
falls back to a generic per-category briefing for any future event name
that doesn't have a hand-written entry yet, so the app never has "nothing to
say" about a release -- only a less specific answer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorBriefing:
    name: str
    category: str
    what_it_is: str
    why_it_matters: str
    market_impact_chain: str
    how_to_read: str
    historical_context: str
    watch_for: str
    inverted: bool = False


INDICATOR_GLOSSARY: dict[str, IndicatorBriefing] = {
    "US CPI YoY": IndicatorBriefing(
        name="US CPI YoY",
        category="inflation",
        what_it_is=(
            "The Consumer Price Index measures the average change in prices paid by urban "
            "consumers for a basket of goods and services -- housing, food, energy, medical "
            "care, and more -- compared with the same month a year earlier. Published monthly "
            "by the US Bureau of Labor Statistics, it's the government's headline inflation "
            "gauge."
        ),
        why_it_matters=(
            "Price stability is one of the Federal Reserve's two legal mandates (the other is "
            "maximum employment). When CPI runs persistently above the Fed's ~2% target, the "
            "Fed is more likely to keep rates higher for longer or hike further; when it cools "
            "convincingly, the Fed has more room to cut. Because Fed policy sets the price of "
            "money for the entire global financial system, CPI is one of the single most "
            "market-moving releases each month."
        ),
        market_impact_chain=(
            "The textbook chain: a hotter-than-expected print raises the market's expected path "
            "for the Fed funds rate -> nominal and real bond yields rise -> a higher-yielding "
            "dollar becomes more attractive relative to non-yielding assets -> Gold (which pays "
            "no yield) and richly-valued growth stocks/crypto (more sensitive to the discount "
            "rate) tend to come under pressure. A cooler print runs the same chain in reverse. "
            "This app's Macro Brain always re-checks this chain against the *current* regime "
            "rather than assuming it fires every time -- in a 'bad news is good news' market, a "
            "hot print doesn't always move things the textbook way."
        ),
        how_to_read=(
            "Not inverted: a higher print is the hawkish outcome. Watch year-over-year for the "
            "underlying trend and month-over-month for momentum. 'Core CPI' (ex food & energy) "
            "usually matters more to markets than the headline number, since food and energy "
            "prices are volatile and don't reflect underlying demand-driven inflation."
        ),
        historical_context=(
            "US CPI surged above 9% YoY in mid-2022 -- the highest in four decades -- which "
            "triggered the fastest Fed hiking cycle since the early 1980s and one of the worst "
            "years on record for stocks and bonds falling together."
        ),
        watch_for=(
            "Revisions to prior months; whether a surprise is concentrated in one volatile "
            "category (used cars, airfares) or broad-based across shelter and services; and how "
            "'supercore' (core services excluding housing) -- a measure the Fed has emphasized "
            "in recent years -- is trending."
        ),
    ),
    "US Nonfarm Payrolls": IndicatorBriefing(
        name="US Nonfarm Payrolls",
        category="employment",
        what_it_is=(
            "The net change in the number of paid US workers during the prior month, excluding "
            "farm workers, government employees, and a few other categories. Released monthly "
            "by the Bureau of Labor Statistics as the headline of the broader monthly 'jobs "
            "report.'"
        ),
        why_it_matters=(
            "Employment is the other half of the Fed's dual mandate. A labor market adding jobs "
            "faster than expected signals an economy resilient enough to tolerate higher rates; "
            "a sharp slowdown signals the economy may need support (rate cuts) sooner rather "
            "than later."
        ),
        market_impact_chain=(
            "Similar chain to CPI: a strong print lifts rate-path expectations -> yields rise -> "
            "USD firms -> Gold and growth assets face headwinds. But payrolls is noisier and "
            "subject to large revisions, so markets often wait for the unemployment rate and "
            "wage data in the same report before committing to a reaction."
        ),
        how_to_read=(
            "Not inverted: a higher print is the strong-economy/hawkish outcome. Compare against "
            "the 3-month and 12-month average rather than the single print -- month-to-month "
            "NFP is genuinely volatile and gets revised, sometimes by large amounts, in the "
            "following two reports."
        ),
        historical_context=(
            "NFP showed the US economy losing over 20 million jobs in April 2020 during the "
            "pandemic shutdown -- the largest one-month decline on record -- then some of the "
            "largest monthly gains on record during the reopening that followed."
        ),
        watch_for=(
            "Average hourly earnings (wage growth) and the labor-force participation rate "
            "released in the same report often matter as much as the headline: strong job growth "
            "with cooling wages is a very different signal than strong job growth with hot wages."
        ),
    ),
    "US Unemployment Rate": IndicatorBriefing(
        name="US Unemployment Rate",
        category="employment",
        what_it_is=(
            "The share of the labor force that is jobless and actively looking for work, drawn "
            "from the household-survey half of the monthly jobs report (separate from the "
            "employer-survey-based Nonfarm Payrolls)."
        ),
        why_it_matters=(
            "It's the most-watched single gauge of labor-market slack, referenced directly in "
            "the Fed's mandate and in the 'Sahm Rule' recession indicator -- a rise of 0.5 "
            "percentage points or more from its 12-month low has historically signaled a "
            "recession is already under way."
        ),
        market_impact_chain=(
            "This is where getting the direction backwards is easiest: a HIGHER unemployment "
            "rate means a WEAKER labor market, which is the dovish outcome for Fed policy (more "
            "likely to cut, less likely to hike) -- the opposite direction from CPI or payrolls. "
            "A rise tends to pull yields down and soften the dollar; Gold tends to benefit from "
            "lower real yields, while equities can go either way since lower rates support "
            "valuations even as a weakening job market threatens earnings."
        ),
        how_to_read=(
            "INVERTED: higher = dovish, lower = hawkish -- backwards from most other indicators "
            "in this calendar. This app flags it explicitly with an 'inverted' badge on its "
            "outcome band rather than silently getting the color-coding backwards, which is a "
            "genuinely common mistake in retail tools."
        ),
        historical_context=(
            "The unemployment rate hit 14.7% in April 2020 -- the highest since Great "
            "Depression-era record-keeping began -- then fell to multi-decade lows near 3.4% by "
            "2023."
        ),
        watch_for=(
            "Whether a rising rate is driven by more people losing jobs (unambiguously weak) or "
            "more people entering the labor force to look for work (often a sign of confidence, "
            "and less bad than it looks) -- check the labor-force participation rate alongside "
            "it before assuming the worse explanation."
        ),
        inverted=True,
    ),
    "US ISM Manufacturing PMI": IndicatorBriefing(
        name="US ISM Manufacturing PMI",
        category="growth",
        what_it_is=(
            "A survey-based index from the Institute for Supply Management asking purchasing "
            "managers at manufacturing firms whether conditions -- new orders, production, "
            "employment, and more -- are improving, flat, or worsening. Above 50 signals "
            "expansion; below 50 signals contraction."
        ),
        why_it_matters=(
            "It's one of the earliest monthly reads of economic activity (released on the first "
            "business day of the month) with a long track record of leading turns in the broader "
            "cycle, making it a closely watched pure-growth gauge distinct from inflation or "
            "labor data."
        ),
        market_impact_chain=(
            "A stronger print signals a healthier growth outlook -- generally supportive for "
            "cyclical/equity risk appetite, and if strong enough to also stoke inflation "
            "concern, can modestly firm up rate expectations too. A weak print (especially a "
            "drop below 50) raises growth-slowdown worries, which can pressure equities and "
            "cyclical commodities like oil even as it sometimes supports bonds and rate-cut bets."
        ),
        how_to_read=(
            "Not inverted: higher = stronger growth. The 50.0 expansion/contraction line matters "
            "as much as beating or missing consensus -- a print of 49.5 against a 49.8 consensus "
            "is a small miss, but the sector is still contracting either way."
        ),
        historical_context=(
            "Manufacturing PMI plunged into the low 40s during the 2020 pandemic shock and again "
            "dipped below 50 for an extended stretch in 2022-2023 even as the broader, "
            "services-heavy US economy kept growing -- a reminder that manufacturing and the "
            "overall economy can diverge for long stretches."
        ),
        watch_for=(
            "The New Orders and Employment sub-components, which often lead the headline figure, "
            "and whether the separate (larger, services-focused) ISM Services PMI confirms or "
            "contradicts the manufacturing read."
        ),
    ),
    "FOMC Rate Decision (Upper Bound)": IndicatorBriefing(
        name="FOMC Rate Decision (Upper Bound)",
        category="central_bank",
        what_it_is=(
            "The Federal Open Market Committee's decision on the target range for the federal "
            "funds rate -- the rate banks charge each other for overnight loans of reserves, and "
            "the anchor for borrowing costs across the entire US economy."
        ),
        why_it_matters=(
            "This is the single most direct lever of US monetary policy. Every other indicator "
            "in this calendar -- CPI, jobs, growth -- matters largely *because* it feeds into "
            "what the Fed does with this one rate."
        ),
        market_impact_chain=(
            "A hike, or a hawkish hold/guidance, relative to what was already priced in lifts "
            "the entire yield curve, strengthens the dollar, and pressures Gold and "
            "long-duration assets (growth equities, crypto) whose valuations lean heavily on the "
            "discount rate. A cut or dovish surprise runs the chain in reverse. Critically, "
            "markets often react as much to the statement, the 'dot plot,' and the press "
            "conference as to the rate decision itself, because the decision is usually already "
            "almost fully priced in beforehand."
        ),
        how_to_read=(
            "Not inverted: a more-hawkish outcome is this event's 'beat' direction. Because the "
            "headline decision is typically well-telegraphed, the real market-moving surprise is "
            "usually in the forward guidance, not the number itself."
        ),
        historical_context=(
            "The Fed hiked at the fastest pace since the early 1980s across 2022-2023 -- from "
            "near-zero to over 5% -- to fight the post-pandemic inflation surge, then held at "
            "that peak for over a year before beginning to cut."
        ),
        watch_for=(
            "The dot plot (each member's individual rate projections), any change in the vote "
            "count (dissents), and specific wording changes in the statement versus the prior "
            "meeting -- these routinely move markets more than the decision itself."
        ),
    ),
    "China Manufacturing PMI": IndicatorBriefing(
        name="China Manufacturing PMI",
        category="growth",
        what_it_is=(
            "China's official (NBS) purchasing managers' index for manufacturing, built the same "
            "way as the US ISM PMI: above 50 signals expansion, below 50 signals contraction."
        ),
        why_it_matters=(
            "China is the world's largest manufacturer and commodity importer, so its factory "
            "activity is a leading indicator for global trade volumes and commodity demand "
            "specifically -- one of the most direct, timely reads on Chinese (and by extension "
            "global) growth momentum, arriving well before China's own quarterly GDP figures."
        ),
        market_impact_chain=(
            "A stronger print signals firmer Chinese industrial demand, tending to support "
            "commodities with heavy Chinese exposure (oil, industrial metals) and "
            "commodity-linked currencies, and can lift global cyclical-equity sentiment. A weak "
            "print raises global-growth concern and can pressure the same assets, sometimes "
            "triggering a flight to safe havens."
        ),
        how_to_read=(
            "Not inverted: higher = stronger growth. Because it's a government-compiled survey, "
            "many market participants also cross-check the privately-compiled Caixin PMI -- a "
            "different sample weighted more toward smaller, export-oriented firms."
        ),
        historical_context=(
            "China's PMI fell sharply in early 2020 and again during the strict 2022 COVID "
            "lockdowns, both times foreshadowing sharp (if temporary) drops in global commodity "
            "demand."
        ),
        watch_for=(
            "Divergence between the official NBS PMI and the private Caixin PMI, which can "
            "signal that state-owned and private/export-oriented firms are having very different "
            "experiences."
        ),
    ),
    "ECB Deposit Rate Decision": IndicatorBriefing(
        name="ECB Deposit Rate Decision",
        category="central_bank",
        what_it_is=(
            "The European Central Bank's decision on its deposit facility rate -- the rate the "
            "ECB pays commercial banks for holding money overnight, and the Eurozone's main "
            "policy-rate anchor, analogous to the Fed funds rate in the US."
        ),
        why_it_matters=(
            "It sets the cost of money for the entire Eurozone and is the primary driver of EUR "
            "interest-rate differentials against the US dollar and other major currencies -- one "
            "of the biggest single inputs into EUR/USD, the world's most heavily traded currency "
            "pair."
        ),
        market_impact_chain=(
            "A hawkish surprise (hike, or hawkish hold/guidance) tends to strengthen the euro and "
            "lift Eurozone yields, which mechanically weighs on the dollar through EUR/USD's "
            "relative pricing and can ripple into USD-denominated assets like Gold. A dovish "
            "surprise runs the same chain in reverse. The ECB's move *relative to* the Fed's own "
            "expected path usually matters more than the ECB decision viewed in isolation."
        ),
        how_to_read=(
            "Not inverted: a more-hawkish outcome is the 'beat' direction. As with the Fed, the "
            "press conference and updated economic projections often move markets more than the "
            "rate decision itself."
        ),
        historical_context=(
            "The ECB held rates at zero (and briefly negative on the deposit rate) for nearly a "
            "decade after the 2011-2012 Eurozone debt crisis, before hiking aggressively "
            "alongside the Fed in 2022-2023 against the same global inflation surge."
        ),
        watch_for=(
            "Any split in the Governing Council's vote, and language about the pace of "
            "balance-sheet reduction (quantitative tightening), which has become a second policy "
            "lever alongside the rate itself."
        ),
    ),
    "US GDP QoQ Annualized": IndicatorBriefing(
        name="US GDP QoQ Annualized",
        category="growth",
        what_it_is=(
            "The quarter-over-quarter change in the total value of goods and services produced "
            "in the US economy, expressed at an annualized rate -- what the quarter's growth "
            "would compound to over a full year. Published by the Bureau of Economic Analysis in "
            "advance, second, and 'final' estimates for each quarter."
        ),
        why_it_matters=(
            "It's the single broadest scorecard of the US economy, rolling consumption, "
            "investment, government spending, and trade into one headline number, and underlies "
            "the informal rule of thumb for a recession (two consecutive quarters of "
            "contraction) -- though the official NBER recession call uses a broader set of "
            "indicators."
        ),
        market_impact_chain=(
            "Strong growth generally supports equities directly through the earnings/economy "
            "channel, but if it's strong enough to also stoke inflation concern, it can "
            "simultaneously push yields up and pressure Gold/growth stocks through the rate "
            "channel -- the two effects can pull the same assets in opposite directions, which is "
            "part of why GDP's market reaction is often more muted than CPI's or the jobs "
            "report's."
        ),
        how_to_read=(
            "Not inverted: higher = stronger growth. GDP is backward-looking (it describes a "
            "quarter that already ended) and gets revised twice more after the first release, so "
            "markets often treat it more as confirmation of what real-time indicators (PMI, "
            "jobs, retail sales) already showed than as a fresh surprise."
        ),
        historical_context=(
            "US GDP contracted at a 31.4% annualized rate in Q2 2020 -- the sharpest quarterly "
            "drop on record -- then rebounded at a record 33.4% annualized pace the following "
            "quarter, showing how dramatically the annualization convention can amplify short, "
            "sharp shocks."
        ),
        watch_for=(
            "The composition of growth -- consumer spending versus inventory build-up versus "
            "government spending -- matters as much as the headline figure. Growth driven by "
            "inventory accumulation is generally considered lower-quality and more likely to "
            "reverse than growth driven by consumer spending."
        ),
    ),
}

# Generic fallback briefings by EconomicEvent.category, used for any event
# name that doesn't have a hand-written entry above yet -- so the app always
# has *something* educational to say, just less specific.
CATEGORY_FALLBACKS: dict[str, IndicatorBriefing] = {
    "inflation": IndicatorBriefing(
        name="Inflation release",
        category="inflation",
        what_it_is="A measure of how fast prices for goods and/or services are rising or falling economy-wide.",
        why_it_matters=(
            "Central banks target a specific inflation rate (commonly ~2%) and set interest "
            "rates largely in response to whether inflation is running above or below that "
            "target."
        ),
        market_impact_chain=(
            "Hotter inflation -> more hawkish rate expectations -> yields up -> USD up -> Gold "
            "and growth assets typically pressured. Cooler inflation runs the chain in reverse, "
            "though the current regime can change how strongly this plays out."
        ),
        how_to_read="Generally not inverted: a higher print is usually the hawkish outcome.",
        historical_context="Inflation surprises have been among the most reliable market-moving releases across major economies for decades.",
        watch_for="Whether the surprise is broad-based across categories or concentrated in one volatile component.",
    ),
    "employment": IndicatorBriefing(
        name="Employment release",
        category="employment",
        what_it_is="A measure of how many people are working, looking for work, or losing jobs.",
        why_it_matters="Labor-market health is a core input to central-bank policy and a direct read on consumer spending power.",
        market_impact_chain=(
            "A strong labor market generally supports hawkish rate expectations (yields/USD up, "
            "Gold/growth assets pressured); a weakening one supports dovish expectations. Check "
            "whether the specific release is inverted (e.g. an unemployment or claims figure) "
            "before assuming the direction."
        ),
        how_to_read="Check whether this specific indicator is a 'more is better' or 'more is worse' figure -- they are not all the same direction.",
        historical_context="Employment data has driven some of the sharpest single-day market moves on record, especially around recession turning points.",
        watch_for="Wage growth and participation-rate data released alongside headline figures, which often change the interpretation.",
    ),
    "growth": IndicatorBriefing(
        name="Growth release",
        category="growth",
        what_it_is="A measure of economic output, business activity, or forward-looking growth momentum.",
        why_it_matters="Growth data shapes both corporate-earnings expectations and, when strong enough to affect inflation, interest-rate expectations too.",
        market_impact_chain=(
            "Stronger growth generally supports equities and cyclical commodities directly, but "
            "can also firm up rate expectations if it raises inflation concern -- pulling the "
            "same assets in different directions depending on which effect dominates."
        ),
        how_to_read="Not inverted: higher generally signals a stronger economy.",
        historical_context="Growth indicators tend to lead or confirm turning points in the broader economic cycle.",
        watch_for="The composition and quality of the growth, not just the headline number.",
    ),
    "central_bank": IndicatorBriefing(
        name="Central bank decision",
        category="central_bank",
        what_it_is="A monetary-policy decision (typically an interest-rate setting) from a major central bank.",
        why_it_matters="Central-bank policy is the single biggest driver of the cost of money, and therefore of nearly every other asset's valuation.",
        market_impact_chain=(
            "A hawkish surprise lifts the relevant currency and yields, pressuring Gold and "
            "growth assets; a dovish surprise runs the chain in reverse."
        ),
        how_to_read="Not inverted: a more-hawkish outcome is generally the 'beat' direction. Forward guidance often matters more than the decision itself.",
        historical_context="Central-bank meetings are consistently among the most-watched, highest-volatility events on the economic calendar.",
        watch_for="Vote splits, updated economic projections, and specific language changes versus the prior statement.",
    ),
}


def get_education(event_name: str, category: str) -> IndicatorBriefing:
    """Looks up the hand-written briefing for this exact event name, falling
    back to a generic per-category briefing so every event has *something*
    educational attached, even one added to the calendar after this glossary
    was last updated.
    """
    return INDICATOR_GLOSSARY.get(event_name) or CATEGORY_FALLBACKS.get(
        category, CATEGORY_FALLBACKS["growth"]
    )
