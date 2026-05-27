#!/usr/bin/env python3
"""
Bill Teubner — 16-Day Social Media Auto-Poster
Runs twice daily via Render cron jobs:
  - 3:45 AM MST (10:45 UTC) → Business post
  - 10:15 AM MST (17:15 UTC) → Personal post
Posts to Instagram and LinkedIn via Zernio CLI
"""

import os
import sys
import json
import logging
import subprocess
from datetime import date, datetime

# ── Config ────────────────────────────────────────────────────────────────────
ZERNIO_KEY   = os.environ.get("ZERNIO_KEY", "sk_765d2e08eb72d83199029aa5274ea95ee9102aca93d8a8442b7dde6163a942e7")
IG_ACCOUNT   = os.environ.get("IG_ACCOUNT",  "6a12f65a2b2567671a2a90d6")
LI_ACCOUNT   = os.environ.get("LI_ACCOUNT",  "6a12f6ac2b2567671a2a931a")
POST_TYPE    = os.environ.get("POST_TYPE",    "business")  # "business" or "personal"
START_DATE   = date(2026, 5, 26)   # Day 1 = May 26, 2026

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
        "business": """For the last three years, brands treated AI like a science experiment. Fund a pilot, issue a press release, repeat. That era is over.

The conversation has finally moved from hype to economics. We are entering the phase of Agentic AI—where systems do not just analyze or recommend; they execute. Recent data shows that Agentic AI is reshaping the entire marketing workflow, with the potential to automate routine tasks and free up teams for high-value strategic work.

If you are still treating AI as just a chatbot, you are missing the bigger picture. The brands that win will be the ones that rebuild their operating models around these new capabilities. At THAT Agency, we are helping clients navigate this exact transition. The ROI is no longer in question; the only question is how fast you can adapt.

#AgenticAI #DigitalMarketing #MarketingStrategy #BusinessGrowth #THATAgency""",
        "personal": """What stepping out of a perfectly good airplane and running a 22-year agency have in common: you do not survive either by avoiding risk. You survive by understanding it.

When I started skydiving, the biggest lesson was not about the thrill; it was about the system. You check your gear, you understand the variables, and you execute the plan. Business is exactly the same. The market shifts, algorithms change, and new technologies like AI disrupt everything we know.

You cannot avoid the risk of disruption. But if you have the right systems in place, you can navigate it safely and come out ahead. Risk is just an opportunity that has not been managed yet.

#Leadership #RiskManagement #Entrepreneurship #Mindset #BusinessStrategy"""
    },
    2: {
        "business": """The old playbook of "click these ten blue links" is changing fast. Between AI summaries and digital assistants, the way people shop and find information has fundamentally shifted.

First, we had SEO. Then came AEO (Answer Engine Optimization). Now, we are looking at ASO—Agentic Search Optimization. Why does this matter, especially for e-commerce? Because soon, AI agents will be making purchases for us. They will be the ones searching the web, comparing products, and making decisions based on data, not flashy ads.

If your brand is not optimized for how AI agents read and interpret data, you are going to become invisible. THAT Agency is already building the frameworks to ensure our clients stay discoverable in an agent-driven world.

#SEO #ASO #Ecommerce #SearchMarketing #THATAgency""",
        "personal": """Rock climbing teaches you something that no boardroom ever will: the only way forward is up, and the only way up is one move at a time.

When you are on the wall, there is no multitasking. There is no checking your phone. There is just the next hold, the next breath, and the next decision. That level of singular focus is something I try to bring back to the agency every Monday morning.

In business, we get distracted by a hundred different priorities. The leaders who win are the ones who can identify the next hold and commit to it completely.

#RockClimbing #Focus #Leadership #Mindset #Entrepreneurship"""
    },
    3: {
        "business": """AI is the number one priority for marketers right now, but it is also one of the hardest things to implement properly. Why? Because AI only works as well as the data you feed it.

Recent industry surveys show that while AI adoption is accelerating, most teams are still struggling with fragmented data. If your customer data is scattered across different platforms, your AI cannot build personalized campaigns. It will just generate disjointed experiences.

Before you invest heavily in the latest AI tools, fix your data foundation. Unified data is the prerequisite for effective AI marketing. If you need help getting your data house in order, THAT Agency has the blueprint.

#DataStrategy #MarketingTech #ArtificialIntelligence #CustomerExperience #THATAgency""",
        "personal": """Mountaineering teaches you a lot about pacing. You do not conquer the summit in the first hour. It is a slow, deliberate grind where endurance matters more than speed.

Building a business over 22 years feels very similar. There are steep climbs, unexpected weather changes, and moments where you have to dig deep just to take the next step. The companies that last are not always the fastest; they are the ones with the endurance to keep climbing when the conditions get tough.

Pace yourself, trust your systems, and keep your eyes on the summit.

#Endurance #BusinessJourney #Mountaineering #Leadership #Mindset"""
    },
    4: {
        "business": """Recent data shows that Google's AI Overviews are now appearing in 58% of searches — and they are cutting traditional click-through rates by up to 89%.

If your entire marketing strategy relies on people clicking a blue link to read a 2,000-word blog post, you are in trouble. Google is no longer a search engine; it is an answer engine. It wants to keep users on its platform, not send them to yours.

The solution? Stop optimizing for clicks and start optimizing for authority. You need to be the source the AI cites, not just a link on page two. At THAT Agency, we are shifting our clients from traditional SEO to Answer Engine Optimization (AEO) to ensure they remain the definitive voice in their industry. The traffic game has changed. Have you?

#GoogleAI #SEO #AEO #DigitalMarketing #SearchStrategy #THATAgency""",
        "personal": """I took this photo in Hawaii recently. "WARNING: Strong Current. High Surf."

In diving, aviation, and business, the warning signs are almost always there before things go wrong. The problem is not a lack of information; it is a lack of attention. We get comfortable. We assume the current will not pull us under because it did not pull us under yesterday.

Right now, the warning signs in digital marketing are flashing bright red. AI is fundamentally changing how consumers find and buy products. The current is shifting. You can ignore the signs and hope for the best, or you can adjust your strategy and ride the wave. I know which one I am choosing.

#Leadership #RiskManagement #BusinessStrategy #Mindset #Adaptability"""
    },
    5: {
        "business": """Too many leaders treat AI like a vending machine: put a prompt in, get a finished marketing campaign out. That is a recipe for generic, invisible content.

AI is not a vending machine. It is a power tool. It amplifies the skill of the person using it. If you have a weak strategy, AI will just help you execute that weak strategy faster. But if you have a deep understanding of your customer, a strong brand voice, and a clear objective, AI becomes the ultimate leverage.

Stop looking for AI to do the thinking for you. Use it to scale the thinking you have already done.

#ArtificialIntelligence #MarketingStrategy #Leadership #BusinessGrowth #THATAgency""",
        "personal": """Building a horse stall from scratch. Tool belt on, sawdust everywhere.

There is a misconception that as you grow as a CEO, you should stop getting your hands dirty. You delegate everything. You stay at the 30,000-foot view.

I disagree. Whether I am building a barn on the weekend or digging into a new AI search algorithm at the agency, I believe you have to stay connected to the work. You cannot lead a team through a massive technological shift if you do not understand the tools they are using.

Keep building. Keep learning. Keep your hands dirty.

#CEO #Leadership #BuilderMindset #ContinuousLearning #Entrepreneurship"""
    },
    6: {
        "business": """We just wrapped up Google Marketing Live 2026, and the message was clear: AI is now woven into every layer of the advertiser experience.

But here is the reality check: the brands that win this year will not be the ones who chase every new AI feature announced on stage. The winners will be the ones who integrate AI into their existing workflows to solve actual customer problems.

Speed is important, but direction matters more. Do not let the hype cycle distract you from the fundamentals of good marketing: knowing your audience, delivering value, and measuring outcomes.

#GoogleMarketingLive #AI #MarketingFundamentals #BusinessStrategy #THATAgency""",
        "personal": """Diving the Silfra fissure in Iceland. Crystal clear water, visibility that goes on forever, and absolute silence.

When you are deep underwater, distractions disappear. You are hyper-focused on your breathing, your gear, and your immediate environment. It is a level of clarity that is hard to find on the surface.

I try to bring that same focus to business. In a world where we are constantly bombarded by new tools, new platforms, and new crises, the ability to tune out the noise and focus on what actually matters is a superpower. Find your clarity.

#ScubaDiving #Focus #Leadership #Clarity #Mindset"""
    },
    7: {
        "business": """Every time Google updates its algorithm, someone declares SEO is dead. It is not dead. It just evolved.

We went from keyword stuffing to intent matching. Now, we are moving from Search Engine Optimization to Answer Engine Optimization (AEO). The goal is no longer just ranking on page one; it is being the definitive answer the AI cites when a user asks a question.

At THAT Agency, we are not abandoning SEO. We are upgrading it. If your agency is still selling you 2019 SEO tactics in 2026, you are losing ground every single day.

#SEO #AEO #DigitalMarketing #SearchStrategy #THATAgency""",
        "personal": """Whitewater rafting with the kids. It looks like pure chaos from the outside. Water everywhere, rocks, unpredictable currents.

But if you know how to read the river, it is not chaos. It is physics. You paddle with the current, you angle off the rocks, and you communicate with your team.

Business is exactly the same. When a massive shift hits — like AI completely upending digital marketing — it feels like chaos. But the leaders who survive are the ones who stop panicking and start reading the river. Build a system. Communicate with your team. Paddle forward.

#Leadership #RiskManagement #SystemsThinking #BusinessStrategy #Mindset"""
    },
    8: {
        "business": """"You do not need more time. You need more focus." — Dan Martell

Dan Martell is right. I see so many marketing teams burning out trying to be everywhere at once. They are churning out mediocre content on six different platforms and wondering why nothing is converting.

Content marketing in 2026 is not about volume. It is about density. One deeply researched, highly valuable piece of content will outperform 50 generic AI-generated blog posts every time.

At THAT Agency, our content strategy is simple: solve the customer's actual problem. If you do that, the algorithm will reward you. Stop trading focus for volume.

#ContentMarketing #DanMartell #MarketingStrategy #Focus #THATAgency""",
        "personal": """Riding out in the Colorado plains. When you are on horseback in wide open country, your perspective shifts. You stop looking at the ground right in front of you and start looking at the horizon.

In business, it is too easy to get trapped looking at the ground. The daily emails, the immediate fires, the monthly metrics. But if you never look up, you will ride right off a cliff.

You have to force yourself to take the long view. Where is your industry going in three years? What skills does your team need to develop today to be relevant tomorrow? Look up.

#Vision #Leadership #LongGame #Strategy #CEO"""
    },
    9: {
        "business": """"Attention is the new oil." — Gary Vaynerchuk

Gary V has been saying it for a decade, and it has never been more true. But here is the catch: in 2026, attention is harder to earn and easier to lose than ever before.

Social media management is no longer just scheduling posts. It is community building. It is rapid response. It is understanding the nuance between a LinkedIn thought leadership piece and an Instagram Story.

If your social media strategy is just broadcasting your sales pitch into the void, you are wasting your time. You have to earn the attention before you can ask for the sale.

#SocialMediaMarketing #GaryVee #AttentionEconomy #BrandBuilding #THATAgency""",
        "personal": """Exploring the waterfalls in New Zealand with Katie.

The moment you stop being curious is the moment you start becoming obsolete. In digital marketing, the landscape changes every six months. If you are not genuinely curious about how new technologies work, how consumer behavior is shifting, and how you can adapt, you will get left behind.

Curiosity is what drives exploration, whether you are hiking in a new country or testing a new AI model. Stay curious. Keep exploring.

#Curiosity #Exploration #ContinuousLearning #Mindset #Travel"""
    },
    10: {
        "business": """Gartner just released a report showing that marketing leaders expect AI automation to double by 2028. We are already seeing it happen in email marketing.

We are moving past basic segmentation. AI agents can now analyze a customer's browsing history, purchase patterns, and real-time behavior to deliver hyper-personalized emails at the exact moment they are most likely to convert.

At THAT Agency, we are integrating predictive analytics into our clients' email workflows. The result? Higher open rates, better engagement, and actual revenue growth. Email is not dead; it just got a massive upgrade.

#EmailMarketing #MarketingAutomation #AI #DataDriven #THATAgency""",
        "personal": """Michelle and I have been building THAT Agency together for 22 years.

There is a myth of the solo founder who builds an empire entirely on their own. It is nonsense. Every successful business is built on partnerships. It is built on trust, shared vision, and the ability to complement each other's strengths.

Whether it is your spouse, your business partner, or your leadership team — surround yourself with people who challenge you and support you. You cannot build anything lasting alone.

#Partnership #BusinessGrowth #AgencyLife #Teamwork #Leadership"""
    },
    11: {
        "business": """"You do not get paid for the hour. You get paid for the value you bring to the hour." — Alex Hormozi

Alex Hormozi nails it here. This is exactly why AI is such a massive disruptor in marketing.

AI does not replace the marketer; it replaces the busywork. It takes the tasks that used to take three hours and compresses them into three minutes. That means your team can spend their time on high-value strategic thinking instead of low-value execution.

If you are billing clients for hours instead of value, AI is a threat. If you are focused on delivering outcomes, AI is the greatest leverage you have ever had.

#AlexHormozi #ValueCreation #AI #MarketingAgency #THATAgency""",
        "personal": """Cutting down our own Christmas tree. No screens, no notifications, just cold air and family tradition.

In an industry that moves at the speed of light, the ability to completely unplug is a competitive advantage. You cannot make high-level strategic decisions if your brain is constantly fried by the daily grind.

You have to build intentional friction into your life. Put the phone away. Go outside. Do something physical. The best ideas rarely happen while you are staring at a screen.

#WorkLifeBalance #MentalHealth #Unplug #FamilyTime #CEO"""
    },
    12: {
        "business": """"Some people do not like change, but you need to embrace change if the alternative is disaster." — Elon Musk

Elon Musk's quote perfectly describes the current state of search marketing.

The shift from traditional search to AI-driven Answer Engines is not a minor algorithm update. It is a fundamental change in how information is discovered. Brands that refuse to adapt their SEO strategies to account for AI Overviews and Agentic Search are choosing disaster.

At THAT Agency, we are helping our clients navigate this transition. Change is uncomfortable, but irrelevance is fatal. Embrace the shift.

#ElonMusk #SearchMarketing #AEO #Innovation #THATAgency""",
        "personal": """Iceland. Bright green jacket, orange pants, and an Icelandic horse. You do not always get to choose the conditions, but you always get to choose how you respond.

Adaptability is the single most important trait for a leader today. The market will shift. Competitors will emerge. Technology will disrupt your business model.

If your response to change is rigidity, you will break. If your response is curiosity and adaptation, you will thrive. Stay flexible.

#Adaptability #Leadership #Iceland #Resilience #Mindset"""
    },
    13: {
        "business": """Stop Guessing. Start Measuring.

"If you cannot measure it, you cannot improve it." It is an old cliche, but in 2026, it is the absolute truth.

With the integration of AI into analytics platforms, there is zero excuse for running marketing campaigns based on gut feeling. We now have the ability to track the entire customer journey, predict churn, and optimize spend in real-time.

At THAT Agency, every strategy we build is grounded in data. Creative gets the attention, but data drives the revenue. Stop guessing.

#DataAnalytics #MarketingStrategy #ROI #BusinessGrowth #THATAgency""",
        "personal": """Horseback riding in the snow with Katie.

As a CEO, your mind is almost always living in the future. You are planning next quarter, next year, the next big pivot. It is necessary for the business, but it is dangerous for your life.

You have to train yourself to be present. When you are with your team, be with your team. When you are with your family, be with your family. The future will still be there tomorrow. Be where your feet are today.

#Presence #Mindfulness #Family #Leadership #CEO"""
    },
    14: {
        "business": """"An agency's job is not to say yes to everything. It is to say no to the wrong things." — Drew McLellan

Drew McLellan understands the true value of an agency partnership.

If you hire an agency and they just execute exactly what you tell them to do without pushing back, you did not hire an agency. You hired order-takers.

A real strategic partner will tell you when your idea will not work. They will tell you when you are wasting money. At THAT Agency, we view our role as strategic advisors first, and executors second. We succeed when our clients succeed, and sometimes that means saying no.

#DrewMcLellan #AgencyLife #StrategicPartnership #Marketing #THATAgency""",
        "personal": """Secret Stash Pizzeria in Breckenridge after a long day in the snow. @secretstashcb

I believe in working incredibly hard. I believe in building systems, driving growth, and pushing the limits of what our agency can do. But I also believe that if you do not take the time to enjoy the rewards of that hard work, you are missing the point.

Celebrate the wins. Take the trip. Eat the pizza. The work will always be there.

#WorkHardPlayHard #Breckenridge #Lifestyle #Entrepreneurship #Balance"""
    },
    15: {
        "business": """We talk a lot about AI automation, predictive analytics, and Agentic Search. But let's not forget the most important element of marketing: the human on the other side of the screen.

AI can write a perfectly optimized email, but it cannot understand the emotional nuance of a customer's pain point. It can generate an image, but it cannot build genuine trust.

The future of marketing is not AI replacing humans. It is AI empowering humans to be more empathetic, more responsive, and more creative. Technology is the tool; connection is the goal.

#Empathy #HumanConnection #AIMarketing #FutureOfWork #THATAgency""",
        "personal": """Scuba wreck diving in the dark is not for the faint of heart. It requires absolute focus, precise communication, and a reliance on your training when things get complicated.

I often think about those dives when we are launching a complex marketing campaign or navigating a major shift in search technology. You cannot see everything that is coming, but you can prepare for the environment. You trust your team, you trust your instruments, and you stick to the plan.

Whether you are 100 feet underwater or steering a company through a technological revolution, preparation is the only thing that keeps you moving forward.

#Leadership #Preparation #Teamwork #ScubaDiving #BusinessGrowth"""
    },
    16: {
        "business": """Your SEO team does not talk to your social media team. Your email marketing is completely disconnected from your content strategy. Sound familiar?

This siloed approach is killing your ROI. Consumers do not experience your brand in silos. They read a blog post, see an Instagram ad, and then get an email. The experience needs to be seamless.

At THAT Agency, we build integrated, full-funnel marketing strategies. SEO, Content, Social, and Email all working together toward a single objective: revenue. Stop operating in silos.

#IntegratedMarketing #FullFunnel #DigitalStrategy #MarketingROI #THATAgency""",
        "personal": """Skiing at Crested Butte with Michelle.

When we started THAT Agency 22 years ago, the digital landscape looked completely different. We have navigated dot-com crashes, the rise of social media, the shift to mobile, and now the AI revolution.

The secret to longevity is not predicting the future perfectly. It is building a foundation strong enough to withstand the shifts, and having the right people by your side to navigate them. Here is to the next 22 years.

#Longevity #BusinessBuilding #Partnership #AgencyLife #CrestedButte"""
    },
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = date.today()
    delta = (today - START_DATE).days + 1  # Day 1 = start date

    if delta < 1 or delta > 16:
        log.info(f"Day {delta} is outside the 16-day calendar range. Nothing to post.")
        sys.exit(0)

    post_type = POST_TYPE  # "business" or "personal"
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

    # Post via Zernio CLI
    accounts = f"{IG_ACCOUNT},{LI_ACCOUNT}"
    cmd = [
        "zernio", "posts:create",
        "--accounts", accounts,
        "--text", text,
        "--media", image_url,
        "--publish-now"
    ]

    log.info(f"Running Zernio CLI...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        log.info(f"stdout: {result.stdout[:500]}")
        if result.stderr:
            log.warning(f"stderr: {result.stderr[:500]}")
        if result.returncode != 0:
            log.error(f"Zernio CLI returned exit code {result.returncode}")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        log.error("Zernio CLI timed out after 120 seconds")
        sys.exit(1)
    except Exception as e:
        log.error(f"Failed to run Zernio CLI: {e}")
        sys.exit(1)

    log.info(f"=== Day {delta} {post_type} post published successfully. ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
