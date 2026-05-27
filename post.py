#!/usr/bin/env python3
"""
Bill Teubner — 32-Day Social Media Auto-Poster (Days 1-32)
Runs twice daily via Render cron jobs:
  - 3:45 AM MST (10:45 UTC) → Business post
  - 10:15 AM MST (17:15 UTC) → Personal post
Posts to Instagram and LinkedIn via Zernio REST API
"""

import os
import sys
import json
import logging
import requests
from datetime import date

# ── Config ────────────────────────────────────────────────────────────────────
ZERNIO_KEY   = os.environ.get("ZERNIO_KEY", "")
IG_ACCOUNT   = os.environ.get("IG_ACCOUNT",  "6a12f65a2b2567671a2a90d6")
LI_ACCOUNT   = os.environ.get("LI_ACCOUNT",  "6a12f6ac2b2567671a2a931a")
POST_TYPE    = os.environ.get("POST_TYPE",    "business")  # "business" or "personal"
START_DATE   = date(2026, 5, 26)   # Day 1 = May 26, 2026

ZERNIO_API   = "https://zernio.com/api/v1"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Fixed CDN URLs (4:5 ratio, no text cutoff) ───────────────────────────────
CDN = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663427489423"

GRAPHICS = {
    # Days 1-16 (May 26 - June 10)
    1:  {"business": f"{CDN}/AiZiIndeiwiepVkC.png", "personal": f"{CDN}/tnkDAdNnNoATiZNi.png"},
    2:  {"business": f"{CDN}/ltuqPhMBPcUIQdas.png", "personal": f"{CDN}/yvwHPrRiIctaLAbR.png"},
    3:  {"business": f"{CDN}/NDfvvFIvBLroIDxB.png", "personal": f"{CDN}/spCiZLbJsPPOOEsA.png"},
    4:  {"business": f"{CDN}/mSxHOHeCioDgKjLG.png", "personal": f"{CDN}/dafYTJzcuZhfVjag.png"},
    5:  {"business": f"{CDN}/DUOdlifsYItKFlpk.png", "personal": f"{CDN}/SRyouKmqUxNsviXQ.png"},
    6:  {"business": f"{CDN}/UkWLBFlLESyShxwq.png", "personal": f"{CDN}/JXajSBjBMWycTlgB.png"},
    7:  {"business": f"{CDN}/ukhVluWVxasWBniB.png", "personal": f"{CDN}/gfetPZdFXoubBxuw.png"},
    8:  {"business": f"{CDN}/vXbRmSJTdXngfuWl.png", "personal": f"{CDN}/WIVALwiqwEYoocLb.png"},
    9:  {"business": f"{CDN}/VjTKiOEMCmFUzGMi.png", "personal": f"{CDN}/vsizuGOVTJzmFVWU.png"},
    10: {"business": f"{CDN}/lPqmAYmEIqglddYR.png", "personal": f"{CDN}/oHvndBAUEtoUSWjy.png"},
    11: {"business": f"{CDN}/ROkGxvwVnLXcOfWy.png", "personal": f"{CDN}/idmYHcgRKgdFXCzj.png"},
    12: {"business": f"{CDN}/xGdUvBDfxWFkxKEx.png", "personal": f"{CDN}/ThFCCqrhgadOGTCO.png"},
    13: {"business": f"{CDN}/onVVIdctgQDJLIHI.png", "personal": f"{CDN}/VecOzgQAIoSwJvtr.png"},
    14: {"business": f"{CDN}/SxekRjGEeHSDCDVb.png", "personal": f"{CDN}/fGggbrATQKecYbMx.png"},
    15: {"business": f"{CDN}/JVSgboxBLHOEHPTh.png", "personal": f"{CDN}/oGqwZhVoFyRaXaIF.png"},
    16: {"business": f"{CDN}/XotvNducFdowJowC.png", "personal": f"{CDN}/xLYxwbUTwOEWuTOx.png"},
    # Days 17-32 (June 11 - June 26)
    17: {"business": f"{CDN}/haIwZfGsvDOAxOaF.png", "personal": f"{CDN}/WHGdWJYwUhijszOF.png"},
    18: {"business": f"{CDN}/FZIcLCEygLsBOeTs.png", "personal": f"{CDN}/NinUVgrDaMtddFiW.png"},
    19: {"business": f"{CDN}/tbhglzVjgkoFgWwL.png", "personal": f"{CDN}/LzmihnXyJRkdAAIO.png"},
    20: {"business": f"{CDN}/wnzFbhcAJcjCTdli.png", "personal": f"{CDN}/owbnDJodiwBIOSEi.png"},
    21: {"business": f"{CDN}/jYVAAXjRXPAfbXUX.png", "personal": f"{CDN}/ZhRQBShKXCYXwmkK.png"},
    22: {"business": f"{CDN}/QPhdDZNWvIFaZnLW.png", "personal": f"{CDN}/sZidOqrxvQXCrfCR.png"},
    23: {"business": f"{CDN}/hbYygjKAXfexZRcY.png", "personal": f"{CDN}/PQWOPsXmHzuEjQZi.png"},
    24: {"business": f"{CDN}/mCoQaalVUXHoZJDR.png", "personal": f"{CDN}/AmFETMaZWmroVqaT.png"},
    25: {"business": f"{CDN}/vQAGqhaTupNMNQhg.png", "personal": f"{CDN}/pnuNkxXbyrhHPUzq.png"},
    26: {"business": f"{CDN}/HdMgQXLETKnYciAI.png", "personal": f"{CDN}/XIhwJgDwmsinvAXo.png"},
    27: {"business": f"{CDN}/jdZvTjWNcBaawtrT.png", "personal": f"{CDN}/OjnofbULvkJNUtOV.png"},
    28: {"business": f"{CDN}/WzMZTnJGuOIynjHj.png", "personal": f"{CDN}/AfHNCWKMjpWtVJSc.png"},
    29: {"business": f"{CDN}/zFFfPiHIRrmOeUcS.png", "personal": f"{CDN}/sQYecoUDlKmArEaq.png"},
    30: {"business": f"{CDN}/JMNcgdkUAIMsSMBe.png", "personal": f"{CDN}/RkEXMTGlnBUuqwTv.png"},
    31: {"business": f"{CDN}/ubisGtbCqnAsZLJh.png", "personal": f"{CDN}/QciQgAgURGhirEoi.png"},
    32: {"business": f"{CDN}/oNFhYXxyrhJydExb.png", "personal": f"{CDN}/ICUhFgjaEzdPrOfk.png"},
}

# ── Post Copy ─────────────────────────────────────────────────────────────────
CONTENT = {
    1: {
        "business": "For the last three years, brands treated AI like a science experiment. Fund a pilot, issue a press release, repeat. That era is over.\n\nThe conversation has finally moved from hype to economics. We are entering the phase of Agentic AI\u2014where systems do not just analyze or recommend; they execute. Recent data shows that Agentic AI is reshaping the entire marketing workflow, with the potential to automate routine tasks and free up teams for high-value strategic work.\n\nIf you are still treating AI as just a chatbot, you are missing the bigger picture. The brands that win will be the ones that rebuild their operating models around these new capabilities. At THAT Agency, we are helping clients navigate this exact transition. The ROI is no longer in question; the only question is how fast you can adapt.\n\n#AgenticAI #DigitalMarketing #MarketingStrategy #BusinessGrowth #THATAgency",
        "personal": "What stepping out of a perfectly good airplane and running a 22-year agency have in common: you do not survive either by avoiding risk. You survive by understanding it.\n\nWhen I started skydiving, the biggest lesson was not about the thrill; it was about the system. You check your gear, you understand the variables, and you execute the plan. Business is exactly the same. The market shifts, algorithms change, and new technologies like AI disrupt everything we know.\n\nYou cannot avoid the risk of disruption. But if you have the right systems in place, you can navigate it safely and come out ahead. Risk is just an opportunity that has not been managed yet.\n\n#Leadership #RiskManagement #Entrepreneurship #Mindset #BusinessStrategy"
    },
    2: {
        "business": "The old playbook of \"click these ten blue links\" is changing fast. Between AI summaries and digital assistants, the way people shop and find information has fundamentally shifted.\n\nFirst, we had SEO. Then came AEO (Answer Engine Optimization). Now, we are looking at ASO\u2014Agentic Search Optimization. Why does this matter, especially for e-commerce? Because soon, AI agents will be making purchases for us. They will be the ones searching the web, comparing products, and making decisions based on data, not flashy ads.\n\nIf your brand is not optimized for how AI agents read and interpret data, you are going to become invisible. THAT Agency is already building the frameworks to ensure our clients stay discoverable in an agent-driven world.\n\n#SEO #ASO #Ecommerce #SearchMarketing #THATAgency",
        "personal": "Rock climbing teaches you something that no boardroom ever will: the only way forward is up, and the only way up is one move at a time.\n\nWhen you are on the wall, there is no multitasking. There is no checking your phone. There is just the next hold, the next breath, and the next decision. That level of singular focus is something I try to bring back to the agency every Monday morning.\n\nIn business, we get distracted by a hundred different priorities. The leaders who win are the ones who can identify the next hold and commit to it completely.\n\n#RockClimbing #Focus #Leadership #Mindset #Entrepreneurship"
    },
    3: {
        "business": "AI is the number one priority for marketers right now, but it is also one of the hardest things to implement properly. Why? Because AI only works as well as the data you feed it.\n\nRecent industry surveys show that while AI adoption is accelerating, most teams are still struggling with fragmented data. If your customer data is scattered across different platforms, your AI cannot build personalized campaigns. It will just generate disjointed experiences.\n\nBefore you invest heavily in the latest AI tools, fix your data foundation. Unified data is the prerequisite for effective AI marketing. If you need help getting your data house in order, THAT Agency has the blueprint.\n\n#DataStrategy #MarketingTech #ArtificialIntelligence #CustomerExperience #THATAgency",
        "personal": "Mountaineering teaches you a lot about pacing. You do not conquer the summit in the first hour. It is a slow, deliberate grind where endurance matters more than speed.\n\nBuilding a business over 22 years feels very similar. There are steep climbs, unexpected weather changes, and moments where you have to dig deep just to take the next step. The companies that last are not always the fastest; they are the ones with the endurance to keep climbing when the conditions get tough.\n\nPace yourself, trust your systems, and keep your eyes on the summit.\n\n#Endurance #BusinessJourney #Mountaineering #Leadership #Mindset"
    },
    4: {
        "business": "Recent data shows that Google's AI Overviews are now appearing in 58% of searches \u2014 and they are cutting traditional click-through rates by up to 89%.\n\nIf your entire marketing strategy relies on people clicking a blue link to read a 2,000-word blog post, you are in trouble. Google is no longer a search engine; it is an answer engine. It wants to keep users on its platform, not send them to yours.\n\nThe solution? Stop optimizing for clicks and start optimizing for authority. You need to be the source the AI cites, not just a link on page two. At THAT Agency, we are shifting our clients from traditional SEO to Answer Engine Optimization (AEO) to ensure they remain the definitive voice in their industry. The traffic game has changed. Have you?\n\n#GoogleAI #SEO #AEO #DigitalMarketing #SearchStrategy #THATAgency",
        "personal": "I took this photo in Hawaii recently. \"WARNING: Strong Current. High Surf.\"\n\nIn diving, aviation, and business, the warning signs are almost always there before things go wrong. The problem is not a lack of information; it is a lack of attention. We get comfortable. We assume the current will not pull us under because it did not pull us under yesterday.\n\nRight now, the warning signs in digital marketing are flashing bright red. AI is fundamentally changing how consumers find and buy products. The current is shifting. You can ignore the signs and hope for the best, or you can adjust your strategy and ride the wave. I know which one I am choosing.\n\n#Leadership #RiskManagement #BusinessStrategy #Mindset #Adaptability"
    },
    5: {
        "business": "Too many leaders treat AI like a vending machine: put a prompt in, get a finished marketing campaign out. That is a recipe for generic, invisible content.\n\nAI is not a vending machine. It is a power tool. It amplifies the skill of the person using it. If you have a weak strategy, AI will just help you execute that weak strategy faster. But if you have a deep understanding of your customer, a strong brand voice, and a clear objective, AI becomes the ultimate leverage.\n\nStop looking for AI to do the thinking for you. Use it to scale the thinking you have already done.\n\n#ArtificialIntelligence #MarketingStrategy #Leadership #BusinessGrowth #THATAgency",
        "personal": "Building a horse stall from scratch. Tool belt on, sawdust everywhere.\n\nThere is a misconception that as you grow as a CEO, you should stop getting your hands dirty. You delegate everything. You stay at the 30,000-foot view.\n\nI disagree. Whether I am building a barn on the weekend or digging into a new AI search algorithm at the agency, I believe you have to stay connected to the work. You cannot lead a team through a massive technological shift if you do not understand the tools they are using.\n\nKeep building. Keep learning. Keep your hands dirty.\n\n#CEO #Leadership #BuilderMindset #ContinuousLearning #Entrepreneurship"
    },
    6: {
        "business": "We just wrapped up Google Marketing Live 2026, and the message was clear: AI is now woven into every layer of the advertiser experience.\n\nBut here is the reality check: the brands that win this year will not be the ones who chase every new AI feature announced on stage. The winners will be the ones who integrate AI into their existing workflows to solve actual customer problems.\n\nSpeed is important, but direction matters more. Do not let the hype cycle distract you from the fundamentals of good marketing: knowing your audience, delivering value, and measuring outcomes.\n\n#GoogleMarketingLive #AI #MarketingFundamentals #BusinessStrategy #THATAgency",
        "personal": "Diving the Silfra fissure in Iceland. Crystal clear water, visibility that goes on forever, and absolute silence.\n\nWhen you are deep underwater, distractions disappear. You are hyper-focused on your breathing, your gear, and your immediate environment. It is a level of clarity that is hard to find on the surface.\n\nI try to bring that same focus to business. In a world where we are constantly bombarded by new tools, new platforms, and new crises, the ability to tune out the noise and focus on what actually matters is a superpower. Find your clarity.\n\n#ScubaDiving #Focus #Leadership #Clarity #Mindset"
    },
    7: {
        "business": "Every time Google updates its algorithm, someone declares SEO is dead. It is not dead. It just evolved.\n\nWe went from keyword stuffing to intent matching. Now, we are moving from Search Engine Optimization to Answer Engine Optimization (AEO). The goal is no longer just ranking on page one; it is being the definitive answer the AI cites when a user asks a question.\n\nAt THAT Agency, we are not abandoning SEO. We are upgrading it. If your agency is still selling you 2019 SEO tactics in 2026, you are losing ground every single day.\n\n#SEO #AEO #DigitalMarketing #SearchStrategy #THATAgency",
        "personal": "Whitewater rafting with the kids. It looks like pure chaos from the outside. Water everywhere, rocks, unpredictable currents.\n\nBut if you know how to read the river, it is not chaos. It is physics. You paddle with the current, you angle off the rocks, and you communicate with your team.\n\nBusiness is exactly the same. When a massive shift hits \u2014 like AI completely upending digital marketing \u2014 it feels like chaos. But the leaders who survive are the ones who stop panicking and start reading the river. Build a system. Communicate with your team. Paddle forward.\n\n#Leadership #RiskManagement #SystemsThinking #BusinessStrategy #Mindset"
    },
    8: {
        "business": "\"You do not need more time. You need more focus.\" \u2014 Dan Martell\n\nDan Martell is right. I see so many marketing teams burning out trying to be everywhere at once. They are churning out mediocre content on six different platforms and wondering why nothing is converting.\n\nContent marketing in 2026 is not about volume. It is about density. One deeply researched, highly valuable piece of content will outperform 50 generic AI-generated blog posts every time.\n\nAt THAT Agency, our content strategy is simple: solve the customer's actual problem. If you do that, the algorithm will reward you. Stop trading focus for volume.\n\n#ContentMarketing #DanMartell #MarketingStrategy #Focus #THATAgency",
        "personal": "Riding out in the Colorado plains. When you are on horseback in wide open country, your perspective shifts. You stop looking at the ground right in front of you and start looking at the horizon.\n\nIn business, it is too easy to get trapped looking at the ground. The daily emails, the immediate fires, the monthly metrics. But if you never look up, you will ride right off a cliff.\n\nYou have to force yourself to take the long view. Carve out time every week to look at the horizon. That is where the real strategy lives.\n\n#Leadership #StrategicThinking #Perspective #BusinessStrategy #Mindset"
    },
    9: {
        "business": "\"Attention is the new oil.\" \u2014 Gary Vaynerchuk\n\nGary V has been saying it for a decade, and it has never been more true. But here is the catch: in 2026, attention is harder to earn and easier to lose than ever before.\n\nSocial media management is no longer just scheduling posts. It is community building. It is rapid response. It is understanding the nuance between a LinkedIn thought leadership piece and an Instagram Story.\n\nIf your social media strategy is just broadcasting your sales pitch into the void, you are wasting your time. You have to earn the attention before you can ask for the sale.\n\n#SocialMediaMarketing #GaryVee #AttentionEconomy #BrandBuilding #THATAgency",
        "personal": "Exploring the waterfalls in New Zealand with Katie.\n\nThe moment you stop being curious is the moment you start becoming obsolete. In digital marketing, the landscape changes every six months. If you are not genuinely curious about how new technologies work, how consumer behavior is shifting, and how you can adapt, you will get left behind.\n\nCuriosity is what drives exploration, whether you are hiking in a new country or testing a new AI model. Stay curious. Keep exploring.\n\n#Curiosity #Exploration #ContinuousLearning #Mindset #Travel"
    },
    10: {
        "business": "Gartner just released a report showing that marketing leaders expect AI automation to double by 2028. We are already seeing it happen in email marketing.\n\nWe are moving past basic segmentation. AI agents can now analyze a customer's browsing history, purchase patterns, and real-time behavior to deliver hyper-personalized emails at the exact moment they are most likely to convert.\n\nAt THAT Agency, we are integrating predictive analytics into our clients' email workflows. The result? Higher open rates, better engagement, and actual revenue growth. Email is not dead; it just got a massive upgrade.\n\n#EmailMarketing #MarketingAutomation #AI #DataDriven #THATAgency",
        "personal": "Michelle and I have been building THAT Agency together for 22 years.\n\nThere is a myth of the solo founder who builds an empire entirely on their own. It is nonsense. Every successful business is built on partnerships. It is built on trust, shared vision, and the ability to complement each other's strengths.\n\nWhether it is your spouse, your business partner, or your leadership team \u2014 surround yourself with people who challenge you and support you. You cannot build anything lasting alone.\n\n#Partnership #BusinessGrowth #AgencyLife #Teamwork #Leadership"
    },
    11: {
        "business": "\"You do not get paid for the hour. You get paid for the value you bring to the hour.\" \u2014 Alex Hormozi\n\nAlex Hormozi nails it here. This is exactly why AI is such a massive disruptor in marketing.\n\nAI does not replace the marketer; it replaces the busywork. It takes the tasks that used to take three hours and compresses them into three minutes. That means your team can spend their time on high-value strategic thinking instead of low-value execution.\n\nIf you are billing clients for hours instead of value, AI is a threat. If you are focused on delivering outcomes, AI is the greatest leverage you have ever had.\n\n#AlexHormozi #ValueCreation #AI #MarketingAgency #THATAgency",
        "personal": "Cutting down our own Christmas tree. No screens, no notifications, just cold air and family tradition.\n\nIn an industry that moves at the speed of light, the ability to completely unplug is a competitive advantage. You cannot make high-level strategic decisions if your brain is constantly fried by the daily grind.\n\nYou have to build intentional friction into your life. Put the phone away. Go outside. Do something physical. The best ideas rarely happen while you are staring at a screen.\n\n#WorkLifeBalance #MentalHealth #Unplug #FamilyTime #CEO"
    },
    12: {
        "business": "\"Some people do not like change, but you need to embrace change if the alternative is disaster.\" \u2014 Elon Musk\n\nElon Musk's quote perfectly describes the current state of search marketing.\n\nThe shift from traditional search to AI-driven Answer Engines is not a minor algorithm update. It is a fundamental change in how information is discovered. Brands that refuse to adapt their SEO strategies to account for AI Overviews and Agentic Search are choosing disaster.\n\nAt THAT Agency, we are helping our clients navigate this transition. Change is uncomfortable, but irrelevance is fatal. Embrace the shift.\n\n#ElonMusk #SearchMarketing #AEO #Innovation #THATAgency",
        "personal": "Iceland. Bright green jacket, orange pants, and an Icelandic horse. You do not always get to choose the conditions, but you always get to choose how you respond.\n\nAdaptability is the single most important trait for a leader today. The market will shift. Competitors will emerge. Technology will disrupt your business model.\n\nIf your response to change is rigidity, you will break. If your response is curiosity and adaptation, you will thrive. Stay flexible.\n\n#Adaptability #Leadership #Iceland #Resilience #Mindset"
    },
    13: {
        "business": "Stop Guessing. Start Measuring.\n\n\"If you cannot measure it, you cannot improve it.\" It is an old cliche, but in 2026, it is the absolute truth.\n\nWith the integration of AI into analytics platforms, there is zero excuse for running marketing campaigns based on gut feeling. We now have the ability to track the entire customer journey, predict churn, and optimize spend in real-time.\n\nAt THAT Agency, every strategy we build is grounded in data. Creative gets the attention, but data drives the revenue. Stop guessing.\n\n#DataAnalytics #MarketingStrategy #ROI #BusinessGrowth #THATAgency",
        "personal": "Horseback riding in the snow with Katie.\n\nAs a CEO, your mind is almost always living in the future. You are planning next quarter, next year, the next big pivot. It is necessary for the business, but it is dangerous for your life.\n\nYou have to train yourself to be present. When you are with your team, be with your team. When you are with your family, be with your family. The future will still be there tomorrow. Be where your feet are today.\n\n#Presence #Mindfulness #Family #Leadership #CEO"
    },
    14: {
        "business": "\"An agency's job is not to say yes to everything. It is to say no to the wrong things.\" \u2014 Drew McLellan\n\nDrew McLellan understands the true value of an agency partnership.\n\nIf you hire an agency and they just execute exactly what you tell them to do without pushing back, you did not hire an agency. You hired order-takers.\n\nA real strategic partner will tell you when your idea will not work. They will tell you when you are wasting money. At THAT Agency, we view our role as strategic advisors first, and executors second. We succeed when our clients succeed, and sometimes that means saying no.\n\n#DrewMcLellan #AgencyLife #StrategicPartnership #Marketing #THATAgency",
        "personal": "Secret Stash Pizzeria in Breckenridge after a long day in the snow. @secretstashcb\n\nI believe in working incredibly hard. I believe in building systems, driving growth, and pushing the limits of what our agency can do. But I also believe that if you do not take the time to enjoy the rewards of that hard work, you are missing the point.\n\nCelebrate the wins. Take the trip. Eat the pizza. The work will always be there.\n\n#WorkHardPlayHard #Breckenridge #Lifestyle #Entrepreneurship #Balance"
    },
    15: {
        "business": "We talk a lot about AI automation, predictive analytics, and Agentic Search. But let's not forget the most important element of marketing: the human on the other side of the screen.\n\nAI can write a perfectly optimized email, but it cannot understand the emotional nuance of a customer's pain point. It can generate an image, but it cannot build genuine trust.\n\nThe future of marketing is not AI replacing humans. It is AI empowering humans to be more empathetic, more responsive, and more creative. Technology is the tool; connection is the goal.\n\n#Empathy #HumanConnection #AIMarketing #FutureOfWork #THATAgency",
        "personal": "Scuba wreck diving in the dark is not for the faint of heart. It requires absolute focus, precise communication, and a reliance on your training when things get complicated.\n\nI often think about those dives when we are launching a complex marketing campaign or navigating a major shift in search technology. You cannot see everything that is coming, but you can prepare for the environment. You trust your team, you trust your instruments, and you stick to the plan.\n\nWhether you are 100 feet underwater or steering a company through a technological revolution, preparation is the only thing that keeps you moving forward.\n\n#Leadership #Preparation #Teamwork #ScubaDiving #BusinessGrowth"
    },
    16: {
        "business": "Your SEO team does not talk to your social media team. Your email marketing is completely disconnected from your content strategy. Sound familiar?\n\nThis siloed approach is killing your ROI. Consumers do not experience your brand in silos. They read a blog post, see an Instagram ad, and then get an email. The experience needs to be seamless.\n\nAt THAT Agency, we build integrated, full-funnel marketing strategies. SEO, Content, Social, and Email all working together toward a single objective: revenue. Stop operating in silos.\n\n#IntegratedMarketing #FullFunnel #DigitalStrategy #MarketingROI #THATAgency",
        "personal": "Skiing at Crested Butte with Michelle.\n\nWhen we started THAT Agency 22 years ago, the digital landscape looked completely different. We have navigated dot-com crashes, the rise of social media, the shift to mobile, and now the AI revolution.\n\nThe secret to longevity is not predicting the future perfectly. It is building a foundation strong enough to withstand the shifts, and having the right people by your side to navigate them. Here is to the next 22 years.\n\n#Longevity #BusinessBuilding #Partnership #AgencyLife #CrestedButte"
    },
    # ── Days 17-32 (June 11 - June 26) ──────────────────────────────────────────
    17: {
        "business": "Google's AI Overviews are now appearing for over 50% of informational searches. What does that mean for your business? It means the \"zero-click\" search is the new reality. Users are getting their answers directly on the search page without ever clicking a link.\n\nIf your SEO strategy is still focused purely on ranking #1 for blue links, you are optimizing for a game that is already over. The new goal is Answer Engine Optimization (AEO)\u2014structuring your content so that AI models cite you as the source. It requires a shift from keyword stuffing to entity authority and structured data.\n\nIs your website ready to be the answer, not just a link? Let's talk about future-proofing your search visibility.\n\n#SEO #AEO #DigitalMarketing #AI #BusinessGrowth #THATAgency",
        "personal": "In diving, as in business, the real work happens before you ever hit the water. You check your gear, review the plan, and anticipate the variables. Once you are submerged, you execute.\n\nI see too many leaders trying to build the plan while they are already in the deep end. It leads to panic, poor decisions, and wasted resources. Take the time to build the system on dry land. When the pressure hits, you want to rely on your preparation, not your ability to improvise.\n\n#Leadership #Preparation #BusinessStrategy #ScubaDiving #Execution"
    },
    18: {
        "business": "The inbox rules have changed. Email deliverability is not just about technical setup; it is about relevance, proving your message deserves to be read.\n\nWe are seeing a massive shift in email marketing. Blasting the same generic newsletter to your entire list is a fast track to the spam folder. AI is allowing us to move from mass communication to personalized, dynamic content at scale. By leveraging AI to segment audiences and tailor messaging based on behavior, we are seeing open rates and engagement climb.\n\nStop sending noise. Start sending value.\n\n#EmailMarketing #AI #MarketingStrategy #LeadGeneration #THATAgency",
        "personal": "The summit is the goal, but the climb is where the value is created. Whether it's scaling a peak or scaling an agency, the difficult stretches are what build resilience and capability.\n\nYou don't learn much on the easy days. Embrace the friction. It's the only way to grow.\n\n#GrowthMindset #Leadership #Mountaineering #BusinessGrowth #Resilience"
    },
    19: {
        "business": "AI writes faster. Attention spans shrink. Trust shifts to people, not logos. This is the reality of content marketing in 2026.\n\nAnyone can generate a 1,000-word blog post in seconds. The internet is flooded with commodity content. To stand out, you need E-E-A-T: Experience, Expertise, Authority, and Trust. Your content must offer unique insights, original data, and a distinct point of view.\n\nStop trying to out-publish the machines. Start out-thinking them.\n\n#ContentMarketing #AI #BrandAuthority #MarketingStrategy #THATAgency",
        "personal": "Sometimes you need to get above the noise to see the full picture. When you are in the weeds of daily operations, every problem feels massive. Stepping back\u2014whether that's flying, climbing, or just taking a strategic retreat\u2014allows you to see the patterns and the path forward.\n\nWhere are you finding your perspective today?\n\n#Perspective #Aviation #Leadership #StrategicThinking #BusinessOwner"
    },
    20: {
        "business": "Local SEO is evolving rapidly. With AI overviews synthesizing local business data, your Google Business Profile is more critical than ever. It's not just about having a profile; it's about having a comprehensive, active, and highly-rated presence.\n\nAI models look for consensus and authority. Are your reviews strong? Is your information consistent across the web? If you want to dominate local search in 2026, you need to feed the AI the right signals.\n\n#LocalSEO #DigitalMarketing #SmallBusiness #AI #THATAgency",
        "personal": "You can have the best strategy in the world, but if the team isn't rowing in the same direction, you're going nowhere. Alignment requires clear communication, shared goals, and mutual trust.\n\nIt's not something that happens by accident; it requires intentional leadership. How are you keeping your team aligned?\n\n#Teamwork #Leadership #BusinessStrategy #Alignment"
    },
    21: {
        "business": "E-commerce is entering the era of Agentic Search Optimization (ASO). Soon, AI agents won't just find products for consumers; they will make the purchases.\n\nTo win in this environment, your product data must be structured flawlessly. Universal Commerce Protocols and detailed attributes are the new storefront. If an AI agent can't understand your product specs, pricing, and availability instantly, it will buy from your competitor.\n\nIs your e-commerce site ready for machine customers?\n\n#Ecommerce #ASO #AI #DigitalMarketing #THATAgency",
        "personal": "The landscape is always changing. The weather shifts, the current changes, the market evolves. The organizations that survive aren't the ones that try to fight the current; they are the ones that learn to navigate it.\n\nAdaptability is the ultimate competitive advantage.\n\n#Adaptability #Leadership #ChangeManagement #BusinessGrowth #Exploration"
    },
    22: {
        "business": "\"Brand is the No. 1 CMO priority for 2026.\" Why? Because in a world of AI-generated answers, brand trust is the ultimate differentiator.\n\nSocial media is no longer just a distribution channel; it's a trust-building engine. It's where you demonstrate expertise, engage with your community, and humanize your business. If your social strategy is just broadcasting links, you are missing the point.\n\nBuild the brand, and the algorithms will follow.\n\n#SocialMediaMarketing #BrandBuilding #DigitalStrategy #Marketing #THATAgency",
        "personal": "Clarity comes from focus. When you are underwater, the distractions of the surface disappear. You are forced to focus on your breathing, your buddy, and your immediate environment.\n\nBusiness requires the same level of intentional focus. Cut the noise. Identify the critical few things that actually move the needle, and ignore the rest.\n\n#Focus #ScubaDiving #Leadership #Productivity #BusinessOwner"
    },
    23: {
        "business": "Silos kill ROI. If your SEO team isn't talking to your content team, and your social team is operating in a vacuum, you are wasting money.\n\nIntegrated marketing is the only way to build a cohesive brand presence that AI models and human customers trust. At THAT Agency, we don't do isolated tactics. We build integrated systems that drive measurable revenue.\n\n#MarketingStrategy #IntegratedMarketing #ROI #BusinessGrowth #THATAgency",
        "personal": "Success is rarely the result of one massive leap. It's the compounding effect of consistent, disciplined effort over time. 22 years of building THAT Agency has taught me that the long game is the only game worth playing.\n\nStay curious, stay disciplined, and keep moving forward.\n\n#Consistency #Leadership #Entrepreneurship #BusinessGrowth #LongGame"
    },
    24: {
        "business": "\"If you can't measure it, you can't improve it.\" AI is giving us unprecedented access to predictive analytics and customer insights. But data is useless without interpretation.\n\nThe businesses that win in 2026 are the ones that use data to inform strategy, not just report on the past. Are you using your marketing data to look backward, or to steer forward?\n\n#DataAnalytics #MarketingStrategy #AI #BusinessIntelligence #THATAgency",
        "personal": "Every worthwhile endeavor involves risk. The key is understanding the difference between calculated risk and reckless gambling. In aviation, we mitigate risk through training, checklists, and situational awareness. In business, we mitigate risk through data, strategy, and strong systems.\n\nDon't avoid risk; learn to manage it.\n\n#RiskManagement #Aviation #Leadership #BusinessStrategy #Entrepreneur"
    },
    25: {
        "business": "AI is a powerful tool, but it's not a replacement for human empathy and strategic insight. The best marketing combines the efficiency of AI with the emotional intelligence of human marketers.\n\nUse AI to analyze data, draft outlines, and automate workflows. Use humans to build relationships, craft compelling narratives, and make strategic leaps.\n\n#AI #MarketingStrategy #DigitalMarketing #FutureOfWork #THATAgency",
        "personal": "You can't run at 100% all the time. Sometimes the most productive thing you can do is step away from the screens and get outside. Nature has a way of resetting the system and providing clarity that you won't find in a spreadsheet.\n\nMake time to unplug.\n\n#WorkLifeBalance #Outdoors #Leadership #MentalHealth #Entrepreneur"
    },
    26: {
        "business": "Lead generation has fundamentally changed. The old playbook of gated PDFs and generic drip campaigns is losing effectiveness. Today's buyers want immediate value and personalized interactions.\n\nWe are using AI-driven conversational tools and highly targeted content to capture and qualify leads faster and more efficiently. Is your lead gen strategy stuck in 2020?\n\n#LeadGeneration #MarketingStrategy #B2BMarketing #SalesFunnel #THATAgency",
        "personal": "A business that relies entirely on the founder's daily involvement is a job, not an asset. Building scalable systems is the hardest part of entrepreneurship, but it's the only way to achieve true growth.\n\nDocument your processes, empower your team, and build a machine that runs whether you are in the office or on a mountain.\n\n#SystemsThinking #Entrepreneurship #BusinessGrowth #Leadership #Scale"
    },
    27: {
        "business": "Video is no longer optional; it's the baseline. From YouTube to short-form social content, video is how modern consumers prefer to learn and engage. Furthermore, AI models are increasingly citing video transcripts in their overviews.\n\nIf you aren't producing high-quality video content, you are invisible to a massive segment of your audience.\n\n#VideoMarketing #ContentStrategy #DigitalMarketing #BrandVisibility #THATAgency",
        "personal": "Nothing great is built alone. Whether it's a dive buddy, a co-pilot, or a business partner, having someone you trust implicitly changes the equation.\n\nSurround yourself with people who challenge you, support you, and share your vision.\n\n#Partnership #Teamwork #Leadership #BusinessGrowth #Relationships"
    },
    28: {
        "business": "\"The only constant in SEO is change.\" Google's recent core updates and the rollout of AI Overviews have caused massive volatility. The brands that survive these shifts are the ones with a diversified traffic strategy and a commitment to high-quality, user-centric content.\n\nDon't chase the algorithm; chase the user.\n\n#SEO #AlgorithmUpdate #DigitalMarketing #MarketingStrategy #THATAgency",
        "personal": "You wouldn't dive with faulty gear, and you shouldn't run a business with outdated tools. Investing in the right technology\u2014whether it's a CRM, an analytics platform, or AI infrastructure\u2014is an investment in your team's efficiency and your company's future.\n\nEquip your team to win.\n\n#Technology #BusinessOperations #Leadership #Efficiency #Entrepreneur"
    },
    29: {
        "business": "Acquiring a new customer is expensive. Retaining an existing one is profitable. Are you putting as much effort into your post-sale marketing as you are into your lead generation?\n\nEmail marketing, personalized content, and proactive customer service are critical for maximizing lifetime value. Don't let a leaky bucket ruin your growth.\n\n#CustomerRetention #MarketingStrategy #BusinessGrowth #LTV #THATAgency",
        "personal": "The moment you think you know it all is the moment you start falling behind. The digital landscape is evolving faster than ever.\n\nStay curious. Read, experiment, and be willing to unlearn what used to work. The best leaders are lifelong learners.\n\n#LifelongLearning #Leadership #Curiosity #PersonalGrowth #Entrepreneur"
    },
    30: {
        "business": "SEO is a long-term investment, not a short-term expense. While paid ads stop generating traffic the moment you stop paying, a strong organic presence pays dividends for years.\n\nIn the era of AI search, building that foundational authority is more critical than ever. Are you investing in your digital real estate?\n\n#SEO #ROI #DigitalMarketing #BusinessStrategy #THATAgency",
        "personal": "Every project, every climb, every business venture hits a wall at some point. The difference between success and failure isn't the absence of obstacles; it's the determination to find a way over, under, or through them.\n\nKeep pushing.\n\n#Resilience #Determination #Leadership #BusinessGrowth #Mindset"
    },
    31: {
        "business": "Your customers don't live on just one platform, and your marketing shouldn't either. An effective omnichannel strategy ensures that your message is consistent and reinforcing across search, social, email, and paid channels.\n\nIt's about creating a seamless experience that guides the customer from discovery to conversion.\n\n#Omnichannel #MarketingStrategy #DigitalMarketing #CustomerJourney #THATAgency",
        "personal": "We spend so much time focused on the next goal that we often forget to celebrate the milestones along the way. Take the time to acknowledge the hard work of your team and the progress you've made.\n\nIt builds morale and fuels the next push.\n\n#TeamCulture #Leadership #Milestones #BusinessGrowth #Gratitude"
    },
    32: {
        "business": "The shift toward AI-driven search and discovery is permanent. Agencies and businesses must adapt early or risk irrelevance. At THAT Agency, our mission is to future-proof our clients' marketing systems against technological disruption.\n\nWe build scalable processes that outperform one-off solutions. Let's build for the future.\n\n#FutureProof #DigitalMarketing #AI #BusinessStrategy #THATAgency",
        "personal": "There is always another mountain to climb, another depth to explore, another challenge to solve. That's what keeps it interesting.\n\nStay curious, stay disciplined, and always be willing to navigate new frontiers.\n\n#Exploration #Leadership #NextFrontier #Entrepreneurship #Vision"
    },
}


# ── Main ──────────────────────────────────────────────────────────────────────

def publish_post(text: str, image_url: str):
    """Publish a post to Instagram and LinkedIn via Zernio REST API."""
    headers = {
        "Authorization": f"Bearer {ZERNIO_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": text,
        "mediaItems": [
            {"type": "image", "url": image_url}
        ],
        "platforms": [
            {"platform": "instagram", "accountId": IG_ACCOUNT},
            {"platform": "linkedin", "accountId": LI_ACCOUNT}
        ],
        "publishNow": True
    }

    log.info(f"Posting to Zernio API...")
    resp = requests.post(f"{ZERNIO_API}/posts", headers=headers, json=payload, timeout=60)

    if resp.status_code in (200, 201):
        log.info(f"Success! Response: {resp.text[:300]}")
        return True
    else:
        log.error(f"Zernio API error {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)


def main():
    if not ZERNIO_KEY:
        log.error("ZERNIO_KEY environment variable not set!")
        sys.exit(1)

    today = date.today()
    delta = (today - START_DATE).days + 1  # Day 1 = start date

    if delta < 1 or delta > 32:
        log.info(f"Day {delta} is outside the 32-day calendar range. Nothing to post.")
        sys.exit(0)

    post_type = POST_TYPE
    log.info(f"=== Bill Teubner Social Poster — Day {delta} / {today} / {post_type} ===")

    day_content = CONTENT.get(delta)
    if not day_content:
        log.error(f"No content defined for Day {delta}")
        sys.exit(1)

    text = day_content.get(post_type)
    if not text:
        log.error(f"No {post_type} content for Day {delta}")
        sys.exit(1)

    image_url = GRAPHICS[delta][post_type]
    log.info(f"Image URL: {image_url}")

    publish_post(text, image_url)

    log.info(f"=== Day {delta} {post_type} post published successfully. ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
