#!/usr/bin/env python3
"""Build the Pathfinders Advisors static site into ./site (GitHub Pages ready).

Usage:  python3 build.py            # review build (noindex)
        python3 build.py --live     # launch build (indexable)

Only the Python standard library is used. Page bodies live in src/pages/*.html and
use {{TOKENS}} that are filled in here, so the header, footer, schema, reviews,
workshops, articles and FAQs come from one place.
"""
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC = ROOT_DIR / "src" / "pages"
OUT = ROOT_DIR / "site"
LIVE = "--live" in sys.argv

SITE = "https://www.pathfindersadvisors.com"
WP = SITE + "/wp-content/uploads/"
BOOK_URL = "https://link.insiderhub.co/widget/bookings/pf-advising-session"
WORKSHOP_URL = "https://workshop.pathfindersadvisors.com/"
VIDEO_URL = WP + "2026/10/College-Planning-for-Families.mp4"
LOGO = WP + "2025/01/Pathfinders_hor_RGB.png"
LOGO_600 = WP + "2025/01/Pathfinders_hor_RGB-600x126.png"
LOGO_300 = WP + "2025/01/Pathfinders_hor_RGB-300x63.png"
LOGO_STACK = WP + "2025/01/Pathfinders_stack_RGB.png"
ORG_NAME = "Pathfinders College & Career Advisors"
SOCIAL = {
    "facebook": "https://www.facebook.com/incollegeplanning/",
    "instagram": "https://www.instagram.com/pathfindersadvisors",
    "linkedin": "https://www.linkedin.com/company/pathfinders-college-career-advisors",
    "youtube": "https://www.youtube.com/@PathfindersAdvisors",
}
NOW = dt.datetime.now(dt.timezone.utc)
VERSION = NOW.strftime("%Y%m%d%H%M%S")

e = lambda s: html.escape(s, quote=True)  # noqa: E731

# --------------------------------------------------------------------------- icons
ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "school": '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/><path d="M22 10v6"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36z"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "dollar": '<path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "bar": '<path d="M12 20V10M18 20V4M6 20v-4"/>',
    "video": '<rect x="2" y="6" width="14" height="12" rx="2"/><path d="m22 8-6 4 6 4z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "map": '<path d="M9 3 3 6v15l6-3 6 3 6-3V3l-6 3-6-3z"/><path d="M9 3v15M15 6v15"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "play": '<path d="M8 5v14l11-7z" fill="currentColor" stroke="none"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "check": '<path d="M5 12.5 9.5 17 19 7.5"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/>',
}
SOCIAL_ICONS = {
    "facebook": '<path fill="currentColor" d="M14 8.5V6.8c0-.8.5-1 .9-1h2.4V2.1L14 2c-3.6 0-4.4 2.7-4.4 4.4v2.1H7.5v3.8h2.1V22h4.4v-9.7h3l.4-3.8H14z"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor"/>',
    "linkedin": '<path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.9-1.8-2.9s-2 1.4-2 2.8V21h-4z"/>',
    "youtube": '<path fill="currentColor" d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.75 15.02V8.98L15.5 12l-5.75 3.02z"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
            + ICONS[name] + "</svg>")


ROUTE_SVG = """<div class="hero-route route-draw" aria-hidden="true"><svg viewBox="0 0 1440 640" preserveAspectRatio="xMidYMid slice" fill="none">
<g stroke="rgba(157,188,198,.16)" stroke-width="1.2">
<ellipse cx="1210" cy="540" rx="330" ry="190" transform="rotate(-12 1210 540)"/>
<ellipse cx="1210" cy="540" rx="250" ry="138" transform="rotate(-12 1210 540)"/>
<ellipse cx="1210" cy="540" rx="170" ry="90" transform="rotate(-12 1210 540)"/>
<ellipse cx="1210" cy="540" rx="92" ry="46" transform="rotate(-12 1210 540)"/>
<ellipse cx="160" cy="70" rx="260" ry="120" transform="rotate(8 160 70)"/>
<ellipse cx="160" cy="70" rx="180" ry="78" transform="rotate(8 160 70)"/>
<ellipse cx="160" cy="70" rx="100" ry="40" transform="rotate(8 160 70)"/>
</g>
<path d="M-40 590 C 200 560 250 430 460 440 S 760 590 960 450 S 1200 170 1490 130" stroke="rgba(246,163,94,.75)" stroke-width="2.4" stroke-linecap="round"/>
<g fill="#F6A35E"><circle cx="960" cy="450" r="5"/><circle cx="1262" cy="226" r="5"/></g>
<g fill="none" stroke="rgba(246,163,94,.5)" stroke-width="1.5"><circle cx="960" cy="450" r="12"/><circle cx="1262" cy="226" r="12"/></g>
</svg></div>"""

# --------------------------------------------------------------------------- data
GOOGLE_REVIEWS = [
    ("Stephanie Mckinnon", "Aaron was very helpful as we navigated high school in preparation for college applications for our oldest son. He assisted with class schedule recommendations (such as foreign language planning), he provided specific guidance around building his college “resume,” and he also spent a significant amount of time between 9th and 11th grades helping my son identify his career path in advance of college applications. As we approached senior year he managed our timeline and kept us ahead of application deadlines. He provided guidance, review and feedback of my son’s college essay. He provided recommendations on when to set up campus tours. He talked with us about ensuring our college debt was in alignment with future career income expectations. At the end, I’m thrilled to share that my son was accepted to every university that he applied to, and I do believe we have Aaron to thank for much of this success!"),
    ("Alyssa Reddy", "Aaron and his team were super helpful with helping me prepare for college! They were awesome to work with and helped get me into my dream school."),
    ("Megan Hauck", "Our daughter, who is currently in her junior year of high school, has been working with Aaron to prepare for college. Aaron has been so knowledgeable throughout this whole process, from prepping for college applications to narrowing her search for a college that fits all her (and our family’s) needs. Throughout this process we have been comfortable and confident that we will find the perfect fit! I would highly recommend Pathfinders!"),
    ("Becky J", "Our family started working with Aaron Green at Pathfinders in my son's sophomore year and it has been a valuable experience. He worked closely with our son to help him identify the career path for him and then went through a very thorough process of researching schools and setting him up for success with applications. Aaron's guidance through the entire process has made it much less stressful for us as parents and for my son as the student. My son has committed to his college of choice and feels confident about that. I highly recommend Aaron and the Pathfinder team!!"),
    ("Mitch Artist", "Fantastic service! They helped my son save thousands on college, and fully understand his future."),
    ("Shannon Hutson", "The Pathfinders Team made a big difference for our daughter, and for our whole family. They helped us think clearly about her future wants and guided us through the steps she needed to get there. Their career readiness process was incredibly valuable and gave us real confidence in the decisions she was making along the way. I highly recommend for any high schooler!"),
    ("Kaleigh Eckler", "Aaron really helped us think about degrees differently and consider what our son really wants to do. He showed us how that relates to the right college. I recommend having a family call!"),
    ("Amy Wisdom", "Such knowledgeable experts leading the way on the important and sometimes complicated journey of figuring out which college will be a good fit - highly recommended!!"),
]

QUOTES = {
    "doug": dict(name="Doug Stevens", meta="Parent, daughter accepted to The Ohio State University",
                 text="Working with Pathfinders was a game-changer for our family, turning what could’ve been a very intimidating, time-consuming and stressful experience into an enlightening, empowering and uplifting one. Thanks to Aaron’s expertise and personalized approach, we confidently navigated the entire college admissions journey. The investment in Pathfinder’s services was absolutely worth every penny."),
    "devita": dict(name="Devita Strand", meta="Parent of Carl, Class of 2019",
                   text="I knew this would be the best fit for Carl and our family after a lot of research, and then meeting in person. The advisors were amazingly patient and encouraging with Carl. He’s on the autism spectrum, which posed some unique challenges in the process, but they were able to provide the individualized career planning and college admissions support he needed."),
    "kathy": dict(name="Kathy Abbott", meta="Parent of Trixie, Class of 2019",
                  text="Thank you! This is perhaps the best business I’ve come across in a long time... I had interviewed other “college counselling” companies but they didn’t offer the professionalism and decision making structure you offer. As soon as our daughter started the program, my anxiety went down by about 80 percent and I know she felt better. She also made her final decision based on the value framework you laid out for us."),
    "miranda": dict(name="Miranda Barrett", meta="Parent, Arlington, VA",
                    text="Working with Pathfinders Advisors has been an absolute game-changer for our family during the college planning process. Their advisor, Aaron, brings a steady hand to what can often feel like an overwhelming and emotional journey, providing calm and organization every step of the way. I can’t recommend them enough to any family navigating this challenging milestone of preparing to launch a kid!"),
}

# (title, ISO start with US Eastern offset, display time)
WORKSHOPS = [
    ("College Financial Aid", "2026-08-20T19:30:00-04:00", "7:30 PM ET"),
    ("College Planning Strategy", "2026-09-17T19:00:00-04:00", "7:00 PM ET"),
    ("Education Investment Planning", "2026-10-13T11:30:00-04:00", "11:30 AM ET"),
    ("College Admissions", "2026-11-19T19:00:00-05:00", "7:00 PM ET"),
    ("Career & College Planning", "2026-12-13T18:00:00-05:00", "6:00 PM ET"),
]

ARTICLES = [
    ("The Hidden Cost of College: New Federal Rules Put College Value Under the Microscope", "the-hidden-cost-of-college-new-federal-rules-put-college-value-under-the-microscope", "2026-11-07", "2026/08/merit-aid-vs-need-based-aid-college-financial-planning-768x577.png", "Parent reviewing merit aid and need-based aid options for college financial planning", ["Current Events", "Financial"], "When families calculate the cost of college, they typically focus on three numbers: tuition, scholarships and the amount they expect to pay out of pocket. But what if some of the biggest college expenses aren’t included in those calculations?"),
    ("Private Student Lending Nearly Doubles at SoFi. What Does That Mean for Families Paying for College?", "private-student-lending-nearly-doubles-at-sofi-what-does-that-mean-for-families-paying-for-college", "2026-11-03", "2026/08/college-funding-rules-changed-768x512.jpg", "College funding and student loan planning", ["Current Events", "Financial"], "When families think about paying for college, the conversation usually starts with savings, scholarships, and federal student loans. Private student loans tend to come later in the process, often treated as a last resort."),
    ("Does the PSAT Still Matter in 2026?", "does-the-psat-still-matter-in-2026", "2026-10-13", "2026/09/sat-act-college-planning-768x512.jpg", "Student preparing for the PSAT, SAT and ACT", ["Current Events", "ACT/SAT"], "Every fall, parents of high school students hear some version of the same announcement: “Your student will be taking the PSAT.” Does the PSAT actually matter? Should my freshman take it?"),
    ("Trump Accounts vs. 529 Plans: What Families Saving for College Need to Know", "trump-accounts-vs-529-plans-what-families-saving-for-college-need-to-know", "2026-10-07", "2026/07/business-team-financial-planning-768x512.jpg", "Financial planning meeting about college savings accounts", ["Financial"], "Families have a new financial planning tool to consider. On October 1, the U.S. Treasury announced that automatic enrollment for Trump Accounts had been completed."),
    ("Why Your Client’s “Affordable College List” May Be Completely Wrong", "why-your-clients-affordable-college-list-may-be-completely-wrong", "2026-10-01", "2026/08/affordable-college-list-net-price-768x473.jpg", "College cost and net price comparison", ["Financial", "For Planners"], "When families begin building a college list, one of the first questions is often: “How much does it cost?” It sounds like a straightforward question. Unfortunately, the answer usually isn’t."),
    ("Colleges Want Your Student: Why States and Universities Are Competing for Families", "colleges-want-your-student-why-states-and-universities-are-competing-for-families", "2026-09-28", "2026/09/colleges-competing-for-students-768x512.jpg", "Universities competing for prospective students", ["Current Events"], "For years, the college admissions conversation has made families feel as though they are competing for colleges. But there is another side to the story."),
    ("Where Is Your Student Wanted? Why Future Lawyers and Graduate Students Should Think Differently About the Undergraduate Decision", "where-is-your-student-wanted-why-future-lawyers-and-graduate-students-should-think-differently-about-the-undergraduate-decision", "2026-09-25", "2026/09/undergraduate-law-school-strategy-768x435.jpg", "Planning an undergraduate path toward law or graduate school", ["Careers"], "When families tell us their student wants to become a lawyer, physician, psychologist or physical therapist, they often begin looking for the university with the strongest undergraduate program connected to that profession."),
    ("Can a Higher SAT or ACT Score Actually Save Your Family Money?", "can-a-higher-sat-or-act-score-actually-save-your-family-money", "2026-09-24", "2026/09/sat-act-scholarship-savings-768x519.jpg", "SAT and ACT scores and merit scholarship savings", ["ACT/SAT", "Financial"], "Many families think about SAT and ACT scores primarily in terms of college admission. That framing makes sense as far as it goes, but scores can also change what college costs."),
    ("The Biggest Financial Decision Most Advisors Aren’t Leading", "the-biggest-financial-decision-most-advisors-arent-leading", "2026-07-09", "2026/07/financial-advisor-client-meeting-768x768.jpg", "Financial advisor meeting with client about college planning decisions", ["Financial", "For Planners"], "For decades, financial advisors have guided families through life’s biggest financial milestones. Yet there is one major financial decision that often receives far less strategic guidance than it deserves."),
    ("Why Financial Aid Appeals Are the Most Overlooked Opportunity in College Planning", "why-financial-aid-appeals-are-the-most-overlooked-opportunity-in-college-planning", "2026-04-09", "2026/04/Financial-Aid-in-College-Planning-768x512.webp", "Financial aid in college planning", ["Financial", "For Planners"], "Financial advisors pride themselves on optimizing outcomes and aligning financial decisions with long-term goals. Yet the financial aid appeal is often overlooked."),
    ("AI in College Admissions: What Families Need to Know (Beyond the Headlines)", "ai-in-college-admissions-what-families-need-to-know-beyond-the-headlines", "2026-04-01", "2026/04/AI-in-College-Admissions-768x512.jpg", "AI in college admissions", ["Careers"], "Headlines about colleges like Virginia Tech using AI to review college essays have sparked curiosity, concern, and confusion. This is not just a technology story. It’s a strategy shift."),
    ("AI Careers for 9th and 10th Graders: Reverse Engineering Education for Future Industry Demand", "ai-careers-for-9th-and-10th-graders", "2026-02-27", "2026/03/AI-Careers-768x419.webp", "AI careers for high school students", ["Careers"], "AI is not just creating “AI jobs.” It’s reshaping every sector. Families who understand where demand is heading can plan an education around it."),
    ("Understanding the CSS Profile: What It Is and Why It Matters for College Aid", "understanding-the-css-profile-what-it-is-and-why-it-matters-for-college-aid", "2025-10-16", "2025/10/iStock-1220289026.jpg", "Financial aid process paperwork", ["Financial", "For Planners"], "Unlike the FAFSA, the CSS Profile helps private and selective colleges award their own scholarship and grant money. Knowing when to file and how it works can unlock thousands of dollars in aid."),
    ("FAFSA Opens 10/1: Avoid Mistakes That Cost You Money", "fafsa-opens-oct-1-2025", "2025-09-30", "2025/05/Your-turn-768x768.png", "FAFSA filing reminder", ["Financial"], "FAFSA opens October 1, and families who delay risk losing thousands in aid. Here’s what every parent of a college-bound student must know before filing."),
]
CATEGORIES = ["Current Events", "Financial", "Careers", "ACT/SAT"]
_KW = ROOT_DIR / "src" / "data" / "article_keywords.json"
ARTICLE_KEYWORDS = json.loads(_KW.read_text()) if _KW.exists() else {}

GUIDES = [
    ("College Application Timeline & Checklist", WP + "2026/06/College-Application-Timeline-Checklist-600x347.png", "Every deadline from junior spring to decision day, in one printable checklist."),
    ("A Parent’s Cheat Sheet to Standardized Tests for College Admission", WP + "2026/06/A-Parents-Cheat-Sheet-to-Standardized-Tests-for-College-Admission-600x333.png", "SAT, ACT and PSAT explained in plain language, including when each one matters."),
]

FAQS = [
    ("Can't we figure this out ourselves?",
     ["You can, but families don't know what they don't know, and mistakes in college and career planning can be expensive and difficult to reverse.",
      "Just as you work with a financial advisor for major financial decisions, Pathfinders helps you avoid costly education mistakes before they happen."]),
    ("Isn't this what the school counselor does?",
     ["School counselors are valuable, but they often support hundreds of students. Pathfinders provides personalized, career-first planning that brings together career exploration, educational fit, financial strategy and ongoing guidance throughout the process."]),
    ("Our child will figure it out once they're in college. Why plan now?",
     ["That may have been true 20 years ago. Today, changing majors, transferring schools or extending graduation can significantly increase costs and delay financial independence.",
      "Starting with career clarity helps students make more informed decisions from the beginning."]),
    ("Is this only for students applying to elite colleges?",
     ["No. The process begins with career discovery and then identifies the best educational pathway, which may be a four-year university, community college, trade school, apprenticeship, military service or another option."]),
    ("Will my teenager actually engage?",
     ["Yes. Students work directly with experienced advisors who help them take ownership of the process, which often reduces parent-child tension."]),
    ("Is it worth the investment?",
     ["The cost of expert guidance is small compared with the financial impact of choosing the wrong educational path or taking on unnecessary student debt.",
      "Families who work with us save about $56,000 on average through scholarship strategies, four-year graduation planning, internships and co-op opportunities."]),
    ("When should our family start?",
     ["Many families begin in 9th or 10th grade, so there is time for career discovery before applications. Most reach out when sophomore or junior year begins and the timeline suddenly feels real, and that is still a great time to start.",
      "Seniors can still get help with the college list, essays, applications, financial aid and choosing between offers."]),
    ("What happens on the complimentary family strategy call?",
     ["We meet your family where you are in the college and career journey. We learn about your student's interests, strengths and goals, point out common blind spots that derail many students, and answer the big question: what should we do next?"]),
    ("Do you work with families outside your area?",
     ["Yes. Coaching, the online College & Career Planning Course and our workshops are all virtual, so we work with families across the United States."]),
]

FP_FAQS = [
    ("Will Pathfinders compete with my services?",
     ["No. Pathfinders complements financial planning by focusing on career discovery and education strategy, so you remain the family's primary financial strategist."]),
    ("Will my clients value this?",
     ["Yes. Education planning is one of the most emotionally and financially significant decisions a family faces, and clients appreciate proactive guidance on it."]),
    ("Will this create more work for me?",
     ["No. Pathfinders handles the specialized planning while keeping you informed, which strengthens your role without adding to your workload."]),
    ("My clients have already saved for college. Do they still need this?",
     ["Saving is only half the equation; strategic spending matters just as much. Academic success doesn't automatically translate into career clarity or the best educational investment."]),
    ("Isn't education funding already part of my role?",
     ["You manage the wealth plan. Pathfinders adds specialized expertise in career exploration, educational fit and Return on Education (ROE), so together your clients get a more complete strategy."]),
]

# --------------------------------------------------------------------------- page config
PAGES = [
    dict(src="index.html", out="index.html", path="/", nav="home",
         title="Education Investment Advisors | Career First. College Second. | Pathfinders",
         desc="Best college admissions consultants guiding high school students and parents in career fit, college choice, and financial strategy. Get started today!",
         og=LOGO_STACK, name="Home"),
    dict(src="educators.html", out="educators/index.html", path="/educators/", nav="educators",
         title="College Planning Support for School Counselors | Pathfinders",
         desc="Refer families to an expert college advisor and free yourself to focus where you're needed most. See how Pathfinders supports school counselors.",
         og=WP + "2025/01/iStock-488580160-modified-392d6dff-f811-4327-91dc-fea3f0286496.jpg", name="Educators"),
    dict(src="financial-planners.html", out="financial-planners/index.html", path="/financial-planners/", nav="planners",
         title="College Financial Aid Guidance for Families - Pathfinders",
         desc="Help clients optimize college portfolios with expert financial aid planning. Free up 10-30% of funds through strategic college selection. Get started now.",
         og=WP + "2025/01/iStock-488580160-modified-392d6dff-f811-4327-91dc-fea3f0286496.jpg", name="Financial Planners"),
    dict(src="workshops.html", out="workshops/index.html", path="/workshops/", nav="workshops",
         title="Workshops - Pathfinders Advisors",
         desc="Most families begin by asking: \"What college should my student attend?\" At Pathfinders, we ask a better question: \"What career will help your student thrive?\"",
         og=WP + "2026/07/Webinars-image.jpg-1024x683.jpeg", name="Workshops"),
    dict(src="resources.html", out="resources/index.html", path="/resources/", nav="resources",
         title="Resources & Insights for College Planning - Pathfinders Advisors",
         desc="Navigate the complex world of college admissions with Pathfinders. Discover expert guidance and strategic insights to maximize your education investment. Explore now!",
         og=LOGO_STACK, name="Knowledge Base"),
    dict(src="about.html", out="about/index.html", path="/about/", nav="about",
         title="About Susan Cornish — College Planning Expert | Pathfinders",
         desc="Meet Susan Cornish — college planning expert with 19+ yrs experience. We've helped 1,500+ students find their best-fit school & career path.",
         og=WP + "2025/01/iStock-488580160-modified-392d6dff-f811-4327-91dc-fea3f0286496.jpg", name="About Us"),
    dict(src="contact-us.html", out="contact-us/index.html", path="/contact-us/", nav="contact",
         title="Contact Pathfinders Advisors: Start Your College Planning Journey",
         desc="Get in touch with Pathfinders Advisors for expert guidance. Visit our contact page to connect with our team today and start your journey to success.",
         og=LOGO_STACK, name="Contact"),
    dict(src="404.html", out="404.html", path="/404/", nav="", title="Page not found | Pathfinders Advisors",
         desc="This page could not be found.", og=LOGO_STACK, name="Not found", noindex=True),
]

NAV = [
    ("home", "Families", ""),
    ("educators", "Educators", "educators/"),
    ("planners", "Financial Planners", "financial-planners/"),
    ("workshops", "Workshops", "workshops/"),
    ("resources", "Knowledge Base", "resources/"),
    ("about", "About", "about/"),
]

# --------------------------------------------------------------------------- helpers


def upcoming_workshops():
    out = []
    for title, iso, shown in WORKSHOPS:
        start = dt.datetime.fromisoformat(iso)
        if start > NOW:
            out.append((title, iso, shown, start))
    return out


def fmt_date(d):
    return d.strftime("%B %-d, %Y")


def article_url(slug):
    return f"{SITE}/{slug}/"


def initials(name):
    parts = [p for p in re.split(r"\s+", name) if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


# --------------------------------------------------------------------------- renderers


def r_reviews(_arg, ctx):
    cards = []
    for name, text in GOOGLE_REVIEWS:
        cards.append(
            f'<article class="review reveal"><div class="review-head"><span class="avatar" aria-hidden="true">{e(initials(name))}</span>'
            f'<div><div class="review-name">{e(name)}</div><div class="review-source">Posted on Google</div></div></div>'
            f'<p class="clamp">{e(text)}</p></article>')
    return '<div class="reviews">' + "".join(cards) + "</div>"


def r_quote(arg, ctx):
    q = QUOTES[arg]
    return (f'<figure class="featured-quote reveal"><div class="qmark" aria-hidden="true">“</div><div>'
            f'<blockquote><p>{e(q["text"])}</p></blockquote>'
            f'<figcaption class="who">{e(q["name"])}<span>{e(q["meta"])}</span></figcaption></div></figure>')


def r_quotecards(arg, ctx):
    keys = arg.split(",")
    cards = []
    for k in keys:
        q = QUOTES[k]
        cards.append(f'<figure class="review reveal" style="margin:0"><blockquote style="margin:0"><p>{e(q["text"])}</p></blockquote>'
                     f'<figcaption class="review-head" style="margin:16px 0 0"><span class="avatar" aria-hidden="true">{e(initials(q["name"]))}</span>'
                     f'<div><div class="review-name">{e(q["name"])}</div><div class="review-source">{e(q["meta"])}</div></div></figcaption></figure>')
    return '<div class="grid-3 cards-wrap">' + "".join(cards) + "</div>"


def post_card(a, root):
    title, slug, date, img, alt, cats, excerpt = a
    d = dt.date.fromisoformat(date)
    cats_attr = "|".join(cats)
    tag = cats[0]
    hay = " ".join([title, excerpt, " ".join(cats), " ".join(ARTICLE_KEYWORDS.get(slug, []))]).lower()
    return (f'<a class="post-card reveal" href="{article_url(slug)}" data-cats="{e(cats_attr)}" data-search="{e(hay)}">'
            f'<div class="thumb"><img src="{WP}{img}" alt="{e(alt)}" loading="lazy" width="768" height="480"></div>'
            f'<div class="body"><div class="post-meta"><span class="tag">{e(tag)}</span><time datetime="{date}">{fmt_date(d)}</time></div>'
            f'<h3>{e(title)}</h3><p>{e(excerpt)}</p><span class="text-link">Read article</span></div></a>')


def r_articles(arg, ctx):
    root = ctx["root"]
    if arg == "latest3":
        items = ARTICLES[:3]
    elif arg == "planners3":
        items = [a for a in ARTICLES if "For Planners" in a[5]][:3]
    else:
        items = ARTICLES
    return '<div class="grid-3 cards-wrap">' + "".join(post_card(a, root) for a in items) + "</div>"


def r_filters(_arg, ctx):
    chips = ['<button class="chip" type="button" data-filter="all" aria-pressed="true">All articles</button>']
    for c in CATEGORIES:
        chips.append(f'<button class="chip" type="button" data-filter="{e(c)}" aria-pressed="false">{e(c)}</button>')
    return '<div class="filter-bar" role="group" aria-label="Filter articles by topic">' + "".join(chips) + "</div>"


def r_faq(arg, ctx):
    items = []
    for i, (q, answer) in enumerate(FP_FAQS if arg == "planners" else FAQS):
        body = "".join(f"<p>{e(p)}</p>" for p in answer)
        items.append(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><div class="answer">{body}</div></details>')
    return '<div class="faq">' + "".join(items) + "</div>"


def r_workshops(arg, ctx):
    rows = []
    for title, iso, shown, start in upcoming_workshops():
        rows.append(
            f'<article class="event reveal" data-event-start="{iso}">'
            f'<div class="event-date" aria-hidden="true"><span class="m">{start.strftime("%b")}</span><span class="d">{start.day}</span></div>'
            f'<div><h3>{e(title)}<span class="tag next-label" hidden>Next up</span></h3>'
            f'<p><time datetime="{iso}">{start.strftime("%A, %B")} {start.day}, {start.year} · {shown}</time> · Free virtual workshop</p></div>'
            f'<a class="btn btn-sm" href="{WORKSHOP_URL}" target="_blank" rel="noopener">Reserve a seat<span class="sr-only"> for {e(title)}</span></a></article>')
    empty = ('<div class="events-empty card"><h3>New dates are on the way</h3>'
             f'<p class="muted">Our next round of free workshops is being scheduled. <a href="{WORKSHOP_URL}" target="_blank" rel="noopener">Check the workshop page</a> or <a href="{ctx["root"]}contact-us/#book">book a family strategy call</a> in the meantime.</p></div>')
    return '<div><div class="event-list">' + "".join(rows) + "</div>" + empty + "</div>"


def r_guides(_arg, ctx):
    cards = []
    for title, img, blurb in GUIDES:
        cards.append(f'<article class="guide-card reveal"><img src="{img}" alt="{e(title)} preview" loading="lazy" width="600" height="340">'
                     f'<div class="body"><span class="tag">Free download</span><h3>{e(title)}</h3><p class="muted" style="margin:8px 0 0;font-size:.98rem">{e(blurb)}</p></div></article>')
    return '<div class="grid-2">' + "".join(cards) + "</div>"


CONSENT = "By submitting this form, I agree to receive email communications from Pathfinders College &amp; Career Advisors related to my inquiry."


def field(name, label, typ="text", required=False, full=False, auto=None, options=None, rows=None):
    req = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    r = " required" if required else ""
    a = f' autocomplete="{auto}"' if auto else ""
    fid = f"f-{name}-{{FORMID}}"
    cls = "field full" if full else "field"
    if options is not None:
        opts = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in options)
        ctrl = f'<select id="{fid}" name="{name}"{r}><option value="">Select one</option>{opts}</select>'
    elif rows:
        ctrl = f'<textarea id="{fid}" name="{name}" rows="{rows}"{r}></textarea>'
    else:
        ctrl = f'<input id="{fid}" name="{name}" type="{typ}"{a}{r}>'
    return f'<div class="{cls}"><label for="{fid}">{label}{req}</label>{ctrl}</div>'


GRAD_YEARS = [str(y) for y in range(NOW.year, NOW.year + 6)] + ["Other / not sure"]


def r_form(kind, ctx):
    if kind in ("educator", "planner"):
        fields = [field("full_name", "Full name", required=True, full=True, auto="name"),
                  field("email", "Email", "email", True, auto="email"),
                  field("phone", "Phone number", "tel", auto="tel"),
                  field("organization", "Organization" if kind == "educator" else "Firm / organization", auto="organization"),
                  field("zip", "ZIP code", auto="postal-code")]
        title = "Give every student your guidance and support." if kind == "educator" else "Provide your clients with something they can’t get anywhere else."
        sub = "Tell us a little about your school or district and we’ll be in touch." if kind == "educator" else "Tell us about your practice and we’ll show you how a partnership works."
        btn, success = "Get in touch", "Thank you. Our team will contact you shortly."
    elif kind == "resource":
        fields = [field("first_name", "First name", required=True, auto="given-name"),
                  field("last_name", "Last name", required=True, auto="family-name"),
                  field("email", "Email", "email", True, full=True, auto="email"),
                  field("grad_year", "Student graduation year", options=GRAD_YEARS),
                  field("resource", "Which resource would you like?", required=True, options=[g[0] for g in GUIDES])]
        title, sub = "Send me the free guide", "We’ll email the PDF to you right away."
        btn, success = "Send me the resource", "Thank you. Check your inbox for your guide."
    else:  # contact
        fields = [field("first_name", "First name", required=True, auto="given-name"),
                  field("last_name", "Last name", required=True, auto="family-name"),
                  field("email", "Email", "email", True, auto="email"),
                  field("phone", "Phone", "tel", auto="tel"),
                  field("student_names", "Student first name(s)"),
                  field("grad_year", "Student graduation year", options=GRAD_YEARS),
                  field("message", "How can we help?", full=True, rows=5)]
        title, sub = "Send us a message", "Questions about coaching, the course or workshops? We’ll reply by email."
        btn, success = "Send message", "Thank you. A member of our team will reply soon."
    sms = ""
    if kind == "contact":
        sms = ('<div class="full consent"><label><input type="checkbox" name="sms_service" value="yes"> I agree to receive non-marketing text messages from Pathfinders College &amp; Career Advisors LLC regarding appointments, scheduling, advising services and other communications related to services I have requested. Message frequency may vary. Message and data rates may apply. Reply HELP for help or STOP to opt out.</label></div>'
               '<div class="full consent"><label><input type="checkbox" name="sms_marketing" value="yes"> I agree to receive marketing text messages from Pathfinders College &amp; Career Advisors LLC regarding educational resources, events, programs, services and promotions. Message frequency may vary. Message and data rates may apply. Reply HELP for help or STOP to opt out.</label></div>'
               f'<p class="full consent" style="margin:0">SMS consent is optional and is not a condition of purchasing or receiving services. See our <a href="{SITE}/privacy-policy/">Privacy Policy</a> and <a href="{SITE}/terms-of-service/">Terms of Service</a>.</p>')
    body = "".join(fields)
    html_out = (f'<form class="form-panel" data-pf-form="{kind}" data-success="{e(success)}" novalidate>'
                f'<h3>{title}</h3><p>{sub}</p><div class="form-grid">{body}'
                f'<div class="hp" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>'
                f'{sms}<p class="full consent" style="margin:0">{CONSENT}</p>'
                f'<div class="full"><button class="btn btn-block" type="submit">{btn}</button></div></div>'
                f'<div class="form-status" role="status" aria-live="polite"></div></form>')
    return html_out.replace("{FORMID}", kind)


CTA_COPY = {
    "home": ("Build a plan first", "Don’t spend $400,000 hoping it works out.",
             "Pathfinders isn’t traditional college counseling. We help students discover who they want to become, identify the educational pathway that supports those goals, and build a financial strategy that maximizes Return on Education (ROE)."),
    "planners": ("For advisors who lead with advice", "Make education one of your clients’ smartest investments.",
                 "You’ve helped your clients accumulate wealth. We help ensure one of their largest planned expenditures is aligned with career outcomes, family values and long-term financial goals."),
    "": ("Ready? We are too.", "Put your student in the driver’s seat.",
         "We get it. Choosing the right college with your student can be daunting. Let us help you put them in the driver’s seat and take the stress off of you."),
}


def r_cta(arg, ctx):
    root = ctx["root"]
    eyebrow, head, para = CTA_COPY.get(arg or "", CTA_COPY[""])
    return (f'<section class="section-tight"><div class="container"><div class="cta-band reveal">{ROUTE_SVG}'
            f'<div><span class="eyebrow">{eyebrow}</span><h2>{head}</h2>'
            f'<p>{para}</p></div>'
            f'<div class="btn-row"><a class="btn" href="{root}contact-us/#book">Book a free strategy call {icon("arrow")}</a></div></div></div></section>')


def r_video(arg, ctx):
    caption = {"home": "See how our Career-First approach works for families like yours.",
               "about": "Meet the Pathfinders team and hear from families who found their path.",
               "workshop": "Watch this 2-minute overview before you reserve your seat."}.get(arg, "")
    return (f'<figure class="video-card"><video controls preload="metadata" playsinline src="{VIDEO_URL}#t=0.8" '
            f'aria-label="See how Pathfinders has helped families like yours"></video>'
            f'<figcaption><span class="video-badge" aria-hidden="true">{icon("play")}</span><span><strong>See how Pathfinders has helped families like yours</strong>{e(caption)}</span></figcaption></figure>')


RENDERERS = {
    "REVIEWS": r_reviews, "QUOTE": r_quote, "QUOTECARDS": r_quotecards, "ARTICLES": r_articles,
    "FILTERS": r_filters, "FAQ": r_faq, "WORKSHOPS": r_workshops, "GUIDES": r_guides, "FORM": r_form,
    "CTA": r_cta, "VIDEO": r_video,
}

# --------------------------------------------------------------------------- schema


def org_node():
    return {
        "@type": "Organization", "@id": SITE + "/#organization", "name": ORG_NAME,
        "alternateName": ["Pathfinders Advisors", "Pathfinders", "College Liftoff"],
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "@id": SITE + "/#logo", "url": LOGO, "width": 1522, "height": 320, "caption": "Pathfinders Advisors"},
        "image": {"@id": SITE + "/#logo"},
        "description": "Education Investment Advisors. We help planning-oriented families make smarter education investments by discovering the right career before choosing the right educational pathway.",
        "slogan": "Career First. College Second.",
        "foundingDate": "2009",
        "founder": {"@type": "Person", "@id": SITE + "/about/#aaron-greene", "name": "Aaron Greene"},
        "areaServed": {"@type": "Country", "name": "United States"},
        "knowsAbout": ["Return on Education (ROE)", "Education investment planning", "College admissions", "Career exploration for high school students", "College planning", "Financial aid", "FAFSA", "CSS Profile", "Merit scholarships", "College application essays", "SAT", "ACT", "Education return on investment"],
        "sameAs": list(SOCIAL.values()),
    }


def website_node():
    return {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Pathfinders Advisors",
            "alternateName": ORG_NAME, "publisher": {"@id": SITE + "/#organization"}, "inLanguage": "en-US"}


def webpage_node(p, typ="WebPage"):
    url = SITE + p["path"]
    node = {"@type": typ, "@id": url + "#webpage", "url": url, "name": p["title"], "description": p["desc"],
            "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": SITE + "/#organization"}, "inLanguage": "en-US",
            "primaryImageOfPage": {"@type": "ImageObject", "url": p["og"]}}
    if p["path"] != "/":
        node["breadcrumb"] = {"@id": url + "#breadcrumb"}
    return node


def breadcrumb_node(p):
    url = SITE + p["path"]
    return {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": p["name"], "item": url}]}


def faq_node(p, faqs=None):
    return {"@type": "FAQPage", "@id": SITE + p["path"] + "#faq", "isPartOf": {"@id": SITE + p["path"] + "#webpage"},
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": " ".join(a)}} for q, a in (faqs or FAQS)]}


def person(pid, name, job, desc, img, extra=None):
    n = {"@type": "Person", "@id": SITE + "/about/#" + pid, "name": name, "jobTitle": job, "description": desc,
         "image": img, "worksFor": {"@id": SITE + "/#organization"}, "url": SITE + "/about/"}
    if not job:
        n.pop("jobTitle")
    if extra:
        n.update(extra)
    return n


def event_nodes():
    out = []
    for title, iso, shown, start in upcoming_workshops():
        end = start + dt.timedelta(hours=1)
        out.append({
            "@type": "EducationEvent", "@id": SITE + "/workshops/#" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") + "-" + start.strftime("%Y%m%d"),
            "name": f"{title} | Free Virtual Workshop for Families",
            "description": "A free virtual workshop for parents of high school students on career-first college planning: choosing a career direction, the right educational pathway and a strategy to fund it.",
            "startDate": iso, "endDate": end.isoformat(),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
            "location": {"@type": "VirtualLocation", "url": WORKSHOP_URL},
            "image": [WP + "2026/07/Webinars-image.jpg-1024x683.jpeg"],
            "organizer": {"@id": SITE + "/#organization"},
            "performer": {"@id": SITE + "/about/#aaron-greene"},
            "isAccessibleForFree": True,
            "audience": {"@type": "Audience", "audienceType": "Parents of high school students"},
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": WORKSHOP_URL, "validFrom": "2026-07-01T00:00:00-04:00"},
        })
    return out


def service_node(sid, name, desc, audience, stype):
    return {"@type": "Service", "@id": SITE + sid, "name": name, "serviceType": stype, "description": desc,
            "provider": {"@id": SITE + "/#organization"}, "areaServed": {"@type": "Country", "name": "United States"},
            "audience": {"@type": "Audience", "audienceType": audience}}


def schema_for(p):
    g = [org_node(), website_node()]
    key = p["src"]
    if key == "index.html":
        g.append(webpage_node(p))
        svc = service_node("/#college-career-advising", "College & Career Advising",
                           "1:1 virtual coaching for high school students and parents: career discovery, college selection, essays and applications, timeline management and financial aid strategy.",
                           "Parents of high school students and students in grades 9 to 12", "College admissions and career planning consulting")
        svc["hasOfferCatalog"] = {"@type": "OfferCatalog", "name": "Pathfinders services", "itemListElement": [
            {"@type": "Offer", "price": "0", "priceCurrency": "USD", "itemOffered": {"@type": "Service", "name": "Complimentary Family Strategy Call"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "1:1 Virtual College & Career Coaching"}},
            {"@type": "Offer", "itemOffered": {"@type": "Course", "name": "The Pathfinders College & Career Planning Course", "provider": {"@id": SITE + "/#organization"}}},
            {"@type": "Offer", "price": "0", "priceCurrency": "USD", "itemOffered": {"@type": "Service", "name": "Free Virtual College & Career Planning Workshops"}},
        ]}
        g += [svc, faq_node(p)]
    elif key == "educators.html":
        g += [webpage_node(p), breadcrumb_node(p),
              service_node("/educators/#service", "College & Career Planning Support for School Counselors",
                           "Personalized career discovery and college planning for high school students, so counselors with large caseloads can focus where they make the most impact.",
                           "High school counselors and educators", "College and career readiness support")]
    elif key == "financial-planners.html":
        g += [webpage_node(p), breadcrumb_node(p),
              service_node("/financial-planners/#service", "College Planning Partnership for Financial Planners",
                           "A wealth-protection and education planning partner for financial advisors: career-first college selection and financial aid strategy that helps client families invest education dollars with discipline, reduce unnecessary student debt and maximize Return on Education (ROE).",
                           "Financial planners and wealth advisors", "College financial aid planning"),
              faq_node(p, FP_FAQS)]
    elif key == "workshops.html":
        g += [webpage_node(p), breadcrumb_node(p)] + event_nodes()
    elif key == "resources.html":
        page = webpage_node(p, "CollectionPage")
        page["mainEntity"] = {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": article_url(a[1]), "name": a[0]} for i, a in enumerate(ARTICLES)]}
        g += [page, breadcrumb_node(p)]
    elif key == "about.html":
        page = webpage_node(p, "AboutPage")
        g += [page, breadcrumb_node(p),
              person("aaron-greene", "Aaron Greene", "Founder & Lead Advisor",
                     "College planning advisor with 16 years of experience and a degree in mechanical engineering. Creator of the Pathfinders Career-First methodology.",
                     WP + "2025/04/image3.png", {"knowsAbout": ["College planning", "Career exploration", "Financial aid strategy"]}),
              person("susan-cornish", "Susan Cornish", None,
                     "19 years in corporate America, a degree in economics and more than 15 years as an entrepreneur. Helps families tackle college and career planning with no regrets.",
                     WP + "2025/04/image2.png"),
              person("aly-foster", "Aly Foster", None,
                     "Degree in business administration and more than a decade of experience guiding families to personalized decisions.",
                     WP + "2025/04/image4.png"),
              {"@type": "Course", "@id": SITE + "/about/#course", "name": "The Pathfinders College & Career Planning Course",
               "description": "A self-paced, online course that supports college applicants through every phase of finding a career and applying to the most suitable college.",
               "provider": {"@id": SITE + "/#organization"}, "inLanguage": "en-US"}]
    elif key == "contact-us.html":
        g += [webpage_node(p, "ContactPage"), breadcrumb_node(p)]
    else:
        g.append(webpage_node(p))
    data = {"@context": "https://schema.org", "@graph": g}
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


# --------------------------------------------------------------------------- layout


def announce_bar(root):
    items = []
    for title, iso, shown, start in upcoming_workshops():
        items.append(f'<template data-announce-item="{iso}">Free virtual workshop: <strong>{e(title)}</strong>, {start.strftime("%a %b")} {start.day} at {shown}. '
                     f'<a href="{root}workshops/">Reserve a seat</a></template>')
    first = upcoming_workshops()
    if first:
        t, iso, shown, start = first[0]
        text = f'Free virtual workshop: <strong>{e(t)}</strong>, {start.strftime("%a %b")} {start.day} at {shown}. <a href="{root}workshops/">Reserve a seat</a>'
    else:
        text = f'Free virtual workshops for families. <a href="{root}workshops/">See upcoming dates</a>'
    return (f'<div class="utility-bar"><div class="container"><p class="utility-announce" style="margin:0"><span class="dot" aria-hidden="true"></span>'
            f'<span data-announce data-fallback="{root}workshops/">{text}</span></p>{"".join(items)}'
            f'<nav class="utility-links" aria-label="Course account"><a href="{SITE}/log-in/">Course login</a><a href="{SITE}/register/">Register</a></nav></div></div>')


def header(p, root):
    links = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == p["nav"] else ""
        links.append(f'<li><a href="{root}{href}"{cur}>{label}</a></li>')
    cur_c = ' aria-current="page"' if p["nav"] == "contact" else ""
    links.append(f'<li class="desktop-hide"><a href="{root}contact-us/"{cur_c}>Contact</a></li>')
    mobile = (f'<li class="mobile-only"><a class="btn" href="{root}contact-us/#book">Book a free strategy call</a></li>'
              f'<li class="mobile-only nav-sub"><a href="{SITE}/log-in/">Course login</a></li>'
              f'<li class="mobile-only"><a href="{SITE}/register/" style="font-size:.95rem;color:var(--muted)">Register for the course</a></li>')
    return (announce_bar(root) +
            f'<header class="site-header"><div class="container header-inner">'
            f'<a class="brand" href="{root}" aria-label="Pathfinders Advisors home"><img src="{LOGO_300}" srcset="{LOGO_300} 300w, {LOGO_600} 600w" sizes="200px" width="300" height="63" alt="Pathfinders College &amp; Career Advisors"></a>'
            f'<nav class="main-nav" id="main-nav" aria-label="Main"><button class="nav-close" type="button" aria-label="Close menu">{icon("close")}</button><ul>{"".join(links)}{mobile}</ul></nav>'
            f'<div class="header-cta"><a class="btn btn-sm" href="{root}contact-us/#book">Book a free call</a>'
            f'<button class="nav-toggle" type="button" aria-controls="main-nav" aria-expanded="false" aria-label="Open menu">{icon("menu")}</button></div>'
            f'</div></header><div class="nav-backdrop" aria-hidden="true"></div>')


def footer(root):
    soc = "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="Pathfinders on {k.capitalize() if k != "youtube" else "YouTube"}"><svg viewBox="0 0 24 24" aria-hidden="true">{SOCIAL_ICONS[k]}</svg></a>' for k, u in SOCIAL.items())
    return (f'<footer class="site-footer"><div class="container"><div class="footer-grid">'
            f'<div class="footer-brand"><img src="{LOGO_600}" width="600" height="126" alt="Pathfinders College &amp; Career Advisors" loading="lazy">'
            f'<p class="tagline">Career First. College Second.</p><p>Education investment advisors helping families across the United States plan the right career, college and funding path since 2009.</p>'
            f'<div class="socials">{soc}</div></div>'
            f'<div><h2>Who we help</h2><ul><li><a href="{root}">Families &amp; students</a></li><li><a href="{root}educators/">School counselors &amp; educators</a></li><li><a href="{root}financial-planners/">Financial planners</a></li></ul></div>'
            f'<div><h2>Learn</h2><ul><li><a href="{root}workshops/">Free workshops</a></li><li><a href="{root}resources/">Knowledge base</a></li><li><a href="{root}#free-guides">Free guides</a></li><li><a href="{SITE}/log-in/">Course login</a></li></ul></div>'
            f'<div><h2>Company</h2><ul><li><a href="{root}about/">About us</a></li><li><a href="{root}contact-us/">Contact</a></li><li><a href="{root}contact-us/#book">Book a strategy call</a></li></ul></div>'
            f'</div><div class="footer-bottom"><p style="margin:0">&copy; <span data-year>{NOW.year}</span> Pathfinders College &amp; Career Advisors LLC. All rights reserved.</p>'
            f'<nav aria-label="Legal"><a href="{SITE}/privacy-policy/">Privacy Policy</a><a href="{SITE}/terms-of-service/">Terms of Service</a></nav></div></div></footer>'
            f'<div class="mobile-cta"><a class="btn" href="{root}contact-us/#book">Book a free strategy call</a></div>')


def layout(p, body, root):
    canonical = SITE + p["path"] if p["src"] != "404.html" else SITE + "/"
    robots = "noindex, nofollow" if (not LIVE or p.get("noindex")) else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    return f"""<!doctype html>
<html lang="en-US" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p["title"])}</title>
<meta name="description" content="{e(p["desc"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Pathfinders Advisors">
<meta property="og:title" content="{e(p["title"])}">
<meta property="og:description" content="{e(p["desc"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{p["og"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#003D51">
<link rel="icon" href="{WP}2025/01/cropped-Pathfinders_hor_RGB-32x32.png" sizes="32x32">
<link rel="icon" href="{WP}2025/01/cropped-Pathfinders_hor_RGB-192x192.png" sizes="192x192">
<link rel="apple-touch-icon" href="{WP}2025/01/cropped-Pathfinders_hor_RGB-180x180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@1,8..60,400;1,8..60,500&display=swap">
<link rel="stylesheet" href="{root}assets/css/style.css?v={VERSION}">
<script type="application/ld+json">
{schema_for(p)}
</script>
</head>
<body class="page-{p["nav"] or "404"}">
<a class="skip-link" href="#main">Skip to content</a>
{header(p, root)}
<main id="main">
{body}
</main>
{footer(root)}
<script src="{root}assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


TOKEN = re.compile(r"\{\{([A-Z_]+)(?::([^}]*))?\}\}")


def render_body(text, ctx):
    def rep(m):
        name, arg = m.group(1), m.group(2)
        if name == "ROOT":
            return ctx["root"]
        if name == "ICON":
            return icon(arg)
        if name == "ROUTE":
            return ROUTE_SVG
        if name == "SITE":
            return SITE
        if name == "WP":
            return WP
        if name == "BOOK_URL":
            return BOOK_URL
        if name == "WORKSHOP_URL":
            return WORKSHOP_URL
        if name == "ARTICLE_COUNT":
            return str(len(ARTICLES))
        if name in RENDERERS:
            return RENDERERS[name](arg, ctx)
        raise KeyError(f"Unknown token {name}")
    out = TOKEN.sub(rep, text)
    return TOKEN.sub(rep, out)  # second pass for tokens produced by renderers


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT_DIR / "assets", OUT / "assets")
    for p in PAGES:
        depth = p["out"].count("/")
        root = "../" * depth if depth else "./"
        if p["src"] == "404.html":
            root = "/pathfindersadvisors-redesign/" if not LIVE else "/"
        body = render_body((SRC / p["src"]).read_text(encoding="utf-8"), {"root": root, "page": p})
        dest = OUT / p["out"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(layout(p, body, root), encoding="utf-8")
        print("built", p["out"])
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if not LIVE else f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    if LIVE:
        urls = "".join(f"<url><loc>{SITE}{p['path']}</loc></url>" for p in PAGES if not p.get("noindex"))
        (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    print("done:", "LIVE build" if LIVE else "review build (noindex)")


if __name__ == "__main__":
    build()
