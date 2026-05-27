#!/usr/bin/env python3
"""
Bill Teubner — 16-Day Social Media Auto-Poster
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
        "personal": "Riding out in the Colorado plains. When you are on horseback in wide open country, your perspective shifts. You stop looking at the ground right in front of you and start looking at the horizon.\n\nIn business, it is too easy to get trapped looking at the ground. The daily emails, the immediate fires, the monthly metrics. But if you never look up, you will ride right off a cliff.\n\nYou have to force yourself to take the long view. Where is your industry going in three years? What skills does your team need to develop today to be relevant tomorrow? Look up.\n\n#Vision #Leadership #LongGame #Strategy #CEO"
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

    if delta < 1 or delta > 16:
        log.info(f"Day {delta} is outside the 16-day calendar range. Nothing to post.")
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
