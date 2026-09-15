export interface QuizQuestion {
  question: string;
  choices: string[];
  correctIndex: number;
}

export interface Station {
  /** Must match app.services.education.glossary.INDICATOR_GLOSSARY's keys
   * on the backend exactly -- this is how a station's briefing is fetched. */
  name: string;
  quiz: QuizQuestion[];
}

// Every question is grounded in the exact facts of the backend briefing for
// that station (app/services/education/glossary.py) -- certification tests
// recall of real content, not invented trivia.
export const STATIONS: Station[] = [
  {
    name: "US CPI YoY",
    quiz: [
      {
        question: "What does the Consumer Price Index measure?",
        choices: [
          "The average change in prices consumers pay for a basket of goods and services",
          "The total value of goods and services produced in the economy",
          "The number of people employed in the private sector",
          "The interest rate the Fed pays banks on reserves",
        ],
        correctIndex: 0,
      },
      {
        question: "Following the textbook chain, a hotter-than-expected CPI print typically does what to Gold?",
        choices: [
          "Pushes Gold higher, since inflation increases its value",
          "Pressures Gold lower, since it raises Fed-hike expectations and yields",
          "Has no effect on Gold whatsoever",
          "Always causes Gold to halt trading",
        ],
        correctIndex: 1,
      },
      {
        question: "Is US CPI YoY an inverted indicator?",
        choices: ["Yes, a higher print is dovish", "No — a higher print is the hawkish outcome", "Only during recessions", "Only for core CPI"],
        correctIndex: 1,
      },
      {
        question: "Why do markets often watch \"core CPI\" more closely than the headline number?",
        choices: [
          "Core CPI is always higher than headline",
          "Core CPI excludes food and energy, which are volatile and don't reflect underlying demand-driven inflation",
          "Core CPI is released a day earlier",
          "Headline CPI isn't seasonally adjusted",
        ],
        correctIndex: 1,
      },
    ],
  },
  {
    name: "US Nonfarm Payrolls",
    quiz: [
      {
        question: "What does Nonfarm Payrolls measure?",
        choices: [
          "The unemployment rate for the prior month",
          "The net change in paid US workers, excluding farm and some government workers",
          "The total wages paid across the economy",
          "The number of job openings advertised",
        ],
        correctIndex: 1,
      },
      {
        question: "Why do markets often wait for more than just the headline NFP number before reacting?",
        choices: [
          "NFP is released with a week's delay",
          "It's noisy and heavily revised, so markets also check the unemployment rate and wage data in the same report",
          "NFP is never market-moving",
          "NFP only covers government workers",
        ],
        correctIndex: 1,
      },
      {
        question: "Is Nonfarm Payrolls an inverted indicator?",
        choices: ["No — a higher print is the hawkish/strong-economy outcome", "Yes, a higher print is dovish", "It depends on the president", "Only in an election year"],
        correctIndex: 0,
      },
      {
        question: "What should you compare a single NFP print against, given how volatile it is?",
        choices: ["Only the prior month", "The 3-month and 12-month averages, not just the single print", "The stock market's daily return", "Nothing — always trust the single print"],
        correctIndex: 1,
      },
    ],
  },
  {
    name: "US Unemployment Rate",
    quiz: [
      {
        question: "What does the Unemployment Rate measure?",
        choices: [
          "The share of the labor force that is jobless and actively looking for work",
          "The number of new jobs created last month",
          "The percentage of people receiving unemployment benefits",
          "The total number of unemployed people, in absolute terms",
        ],
        correctIndex: 0,
      },
      {
        question: "Is the Unemployment Rate an inverted indicator?",
        choices: [
          "No, higher is always hawkish",
          "Yes — a HIGHER print is the DOVISH outcome, the opposite of most releases",
          "It depends on which country",
          "It's neutral and never affects markets",
        ],
        correctIndex: 1,
      },
      {
        question: "Per the \"Sahm Rule,\" what has historically signaled a recession is already under way?",
        choices: ["Unemployment falling below 3%", "A rise of 0.5 percentage points or more from its 12-month low", "Unemployment staying flat for 6 months", "Unemployment exceeding 20%"],
        correctIndex: 1,
      },
      {
        question: "A rising unemployment rate could reflect more people losing jobs, or what less-bad explanation?",
        choices: ["More people entering the labor force to look for work", "A stock market crash", "A change in how CPI is calculated", "A Fed rate hike"],
        correctIndex: 0,
      },
    ],
  },
  {
    name: "US ISM Manufacturing PMI",
    quiz: [
      {
        question: "What does a PMI reading above 50 signal?",
        choices: ["Contraction in the sector", "Expansion in the sector", "A recession", "A currency devaluation"],
        correctIndex: 1,
      },
      {
        question: "Why is ISM Manufacturing PMI considered an early read on the economy?",
        choices: [
          "It's released on the first business day of the month, ahead of most other data",
          "It's only published once a year",
          "It's identical to GDP",
          "It only covers government spending",
        ],
        correctIndex: 0,
      },
      {
        question: "Which sub-components of PMI often lead the headline figure?",
        choices: ["Employment and shipping costs", "New Orders and Employment", "Weather and holidays", "Currency exchange rates"],
        correctIndex: 1,
      },
      {
        question: "Beyond beating or missing consensus, what threshold matters for PMI?",
        choices: ["Whether it printed on a Monday", "Whether it's above or below the 50.0 expansion/contraction line", "The color of the report cover", "Whether the month is odd or even"],
        correctIndex: 1,
      },
    ],
  },
  {
    name: "FOMC Rate Decision (Upper Bound)",
    quiz: [
      {
        question: "What does the FOMC rate decision set?",
        choices: ["The exchange rate between USD and EUR", "The target range for the federal funds rate", "The US government's budget deficit", "The price of gold"],
        correctIndex: 1,
      },
      {
        question: "Why does the market often react more to the statement/press conference than the rate decision itself?",
        choices: [
          "The press conference is longer",
          "The decision is usually already priced in; forward guidance carries the real surprise",
          "The statement is read by a different person",
          "It doesn't — the decision always matters more",
        ],
        correctIndex: 1,
      },
      {
        question: "What is the \"dot plot\"?",
        choices: ["A chart of historical GDP", "Each FOMC member's individual rate projections", "A map of Federal Reserve branch locations", "A chart of stock market volatility"],
        correctIndex: 1,
      },
      {
        question: "A hawkish surprise from the Fed typically does what to Gold?",
        choices: [
          "Pushes Gold higher",
          "Pressures Gold lower, since higher real yields raise the opportunity cost of holding a non-yielding asset",
          "Has no effect",
          "Only affects Gold-mining stocks",
        ],
        correctIndex: 1,
      },
    ],
  },
  {
    name: "China Manufacturing PMI",
    quiz: [
      {
        question: "Why does China's Manufacturing PMI matter globally?",
        choices: [
          "China is the world's largest manufacturer and commodity importer",
          "It's the only PMI published worldwide",
          "It determines the US Fed's interest rate",
          "It measures Chinese consumer confidence only",
        ],
        correctIndex: 0,
      },
      {
        question: "What is the Caixin PMI, and why is it watched alongside the official NBS PMI?",
        choices: [
          "It's identical to the NBS PMI",
          "A privately-compiled PMI weighted toward smaller, export-oriented firms, useful as a cross-check",
          "A US-published estimate of China's economy",
          "A measure covering only Chinese real estate",
        ],
        correctIndex: 1,
      },
      {
        question: "A stronger China PMI print tends to support which assets?",
        choices: ["US Treasury bonds only", "Commodities with heavy Chinese demand exposure, like oil and industrial metals", "Only Chinese equities", "Nothing — it's an ignored, lagging indicator"],
        correctIndex: 1,
      },
      {
        question: "Is China Manufacturing PMI an inverted indicator?",
        choices: ["No — higher means stronger growth, same convention as the US ISM PMI", "Yes, always", "Only during the Lunar New Year", "It has no direction at all"],
        correctIndex: 0,
      },
    ],
  },
  {
    name: "ECB Deposit Rate Decision",
    quiz: [
      {
        question: "What does the ECB Deposit Rate set?",
        choices: [
          "The rate the ECB pays banks for holding money overnight — the Eurozone's main policy-rate anchor",
          "The exchange rate for EUR/USD directly",
          "Germany's national budget",
          "The price of Eurozone government bonds only",
        ],
        correctIndex: 0,
      },
      {
        question: "What does the ECB rate decision primarily drive, relative to the Fed's own expected path?",
        choices: ["Oil prices exclusively", "EUR/USD, through the interest-rate differential between the two central banks", "Japanese equities", "Nothing measurable"],
        correctIndex: 1,
      },
      {
        question: "The ECB held rates at or near zero for roughly a decade after which event?",
        choices: ["The 1990s recession", "The 2011-2012 Eurozone debt crisis, until the 2022-2023 hiking cycle", "World War II", "The dot-com bubble"],
        correctIndex: 1,
      },
      {
        question: "Besides the rate itself, what else can move markets at an ECB meeting?",
        choices: ["Nothing else matters", "Vote splits and language on the pace of balance-sheet reduction (quantitative tightening)", "The room's seating chart", "The president's tie color"],
        correctIndex: 1,
      },
    ],
  },
  {
    name: "US GDP QoQ Annualized",
    quiz: [
      {
        question: "What does \"annualized\" mean in US GDP QoQ Annualized?",
        choices: [
          "It's the actual full-year growth number",
          "It expresses what the quarter's growth rate would compound to over a full year",
          "It's adjusted for inflation only",
          "It measures only government spending",
        ],
        correctIndex: 1,
      },
      {
        question: "Why do markets often react less sharply to GDP than to CPI or the jobs report?",
        choices: [
          "GDP is backward-looking and gets revised twice more, so it's often treated as confirmation, not a fresh surprise",
          "GDP is never accurate",
          "GDP is released weekly",
          "Markets are closed when GDP releases",
        ],
        correctIndex: 0,
      },
      {
        question: "Which kind of growth is generally considered \"lower quality,\" more likely to reverse?",
        choices: ["Growth driven by consumer spending", "Growth driven by inventory accumulation rather than consumer spending", "Growth driven by exports", "All growth is equal quality"],
        correctIndex: 1,
      },
      {
        question: "What was notable about US GDP in 2020?",
        choices: [
          "It grew steadily all year",
          "It contracted at a record 31.4% annualized rate in Q2, then rebounded at a record 33.4% pace the next quarter",
          "It was not measured that year",
          "It stayed exactly flat",
        ],
        correctIndex: 1,
      },
    ],
  },
];
