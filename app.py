import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import re
from datetime import datetime, timezone
from collections import Counter

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RolePulse",
    layout="wide"
)

# =====================================================
# ADVANCED UI STYLING
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #111827 25%,
        #1e1b4b 50%,
        #111827 75%,
        #0f172a 100%
    );
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* HEADER */

h1 {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

/* KPI CARDS */

[data-testid="metric-container"] {

    background: linear-gradient(
        135deg,
        rgba(37,99,235,0.25),
        rgba(124,58,237,0.25)
    );

    border: 1px solid rgba(255,255,255,0.08);

    padding: 22px;

    border-radius: 20px;

    backdrop-filter: blur(12px);

    box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
}

[data-testid="metric-container"]:hover {

    transform: translateY(-4px);

    transition: 0.3s ease;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background-color: #0f172a;

    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}

.stTabs [data-baseweb="tab"] {

    padding: 12px 22px;

    border-radius: 14px;
}

.stTabs [aria-selected="true"] {

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed,
        #06b6d4
    ) !important;

    color: white !important;

    box-shadow: 0px 4px 12px rgba(37,99,235,0.4);
}

/* DATAFRAME */

[data-testid="stDataFrame"] {

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid rgba(255,255,255,0.08);
}

/* ALERTS */

[data-testid="stAlert"] {

    border-radius: 18px;
}

/* REMOVE STREAMLIT DEFAULTS */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<h1>RolePulse</h1>

<p style='font-size:18px; color:#cbd5e1; margin-top:-10px;'>

Hiring Intelligence & Resume Match Analytics
for the Indian Job Market

</p>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# API CREDENTIALS
# =====================================================

APP_ID = st.secrets["ADZUNA_APP_ID"]
APP_KEY = st.secrets["ADZUNA_APP_KEY"]

# =====================================================
# EXPERIENCE EXTRACTION
# =====================================================

def extract_experience(text):

    if not isinstance(text, str):
        return "Not Specified"

    text = text.lower()

    patterns = [

        r'(\\d+)\\+?\\s*years',
        r'(\\d+)\\s*-\\s*(\\d+)\\s*years',
        r'(\\d+)\\+?\\s*yrs',
        r'minimum\\s*(\\d+)\\s*years',
        r'(\\d+)\\s*year experience'

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            if len(match.groups()) == 2:

                return f"{match.group(1)}-{match.group(2)} Years"

            return f"{match.group(1)}+ Years"

    return "Not Specified"

# =====================================================
# SKILL EXTRACTION
# =====================================================

SKILLS = [

    "python",
    "sql",
    "tableau",
    "power bi",
    "excel",
    "jira",
    "figma",
    "analytics",
    "api",
    "product strategy",
    "agile",
    "scrum",
    "ai",
    "machine learning",
    "communication",
    "stakeholder management",
    "roadmap",
    "data analysis"
]

def extract_skills(text):

    text = str(text).lower()

    found = []

    for skill in SKILLS:

        if skill in text:
            found.append(skill.title())

    return found

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Search")

keyword = st.sidebar.text_input(
    "Role",
    value="Product Manager"
)

results_count = st.sidebar.slider(
    "Listings",
    10,
    50,
    25
)

freshness_filter = st.sidebar.selectbox(
    "Freshness",
    [
        "All",
        "Fresh",
        "Moderate",
        "Possibly Stale"
    ]
)

experience_filter = st.sidebar.selectbox(
    "Experience Level",
    [
        "All",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Resume Intelligence")

uploaded_resume = st.sidebar.file_uploader(
    "Upload Resume (.txt)",
    type=["txt"]
)

# =====================================================
# API REQUEST
# =====================================================

url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {

    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": results_count,
    "what": keyword,
    "where": "India",
    "content-type": "application/json"
}

response = requests.get(url, params=params)

data = response.json()

# =====================================================
# PROCESS JOBS
# =====================================================

jobs = []

all_market_skills = []

for job in data.get("results", []):

    title = job.get("title", "N/A")

    company = job.get(
        "company",
        {}
    ).get(
        "display_name",
        "Unknown"
    )

    location_name = job.get(
        "location",
        {}
    ).get(
        "display_name",
        "Unknown"
    )

    description = job.get(
        "description",
        ""
    )

    created = job.get(
        "created",
        ""
    )

    redirect_url = job.get(
        "redirect_url",
        ""
    )

    # EXPERIENCE

    experience_required = extract_experience(
        title + " " + description
    )

    # SKILLS

    extracted_skills = extract_skills(description)

    all_market_skills.extend(extracted_skills)

    # FRESHNESS

    freshness = "Unknown"

    days_old = None

    try:

        created_date = datetime.strptime(
            created,
            "%Y-%m-%dT%H:%M:%SZ"
        )

        days_old = (
            datetime.now(timezone.utc)
            -
            created_date.replace(
                tzinfo=timezone.utc
            )
        ).days

        if days_old <= 7:
            freshness = "Fresh"

        elif days_old <= 30:
            freshness = "Moderate"

        else:
            freshness = "Possibly Stale"

    except:
        freshness = "Unknown"

    # WORK MODE

    work_mode = "Onsite"

    if "remote" in description.lower():
        work_mode = "Remote"

    elif "hybrid" in description.lower():
        work_mode = "Hybrid"

    # URGENCY

    urgency = "Normal"

    urgent_keywords = [

        "urgent",
        "immediate joiner",
        "hiring now",
        "asap"
    ]

    for word in urgent_keywords:

        if word in description.lower():

            urgency = "Urgent"

            break

    # DESCRIPTION QUALITY

    description_quality = "Low"

    if len(description) > 400:
        description_quality = "Moderate"

    if len(description) > 800:
        description_quality = "High"

    # HIRING SCORE

    score = 50

    if freshness == "Fresh":
        score += 20

    if description_quality == "High":
        score += 15

    if urgency == "Urgent":
        score += 10

    if work_mode == "Remote":
        score += 5

    if "senior" in title.lower():
        score += 5

    score = min(score, 100)

    # RECOMMENDATION

    if score >= 85:
        recommendation = "Apply Immediately"

    elif score >= 70:
        recommendation = "Strong Opportunity"

    elif score >= 55:
        recommendation = "Moderate Priority"

    else:
        recommendation = "Low Confidence"

    jobs.append({

        "Title": title,
        "Company": company,
        "Location": location_name,
        "Experience Required": experience_required,
        "Work Mode": work_mode,
        "Urgency": urgency,
        "Skills": ", ".join(extracted_skills),
        "Hiring Score": score,
        "Freshness": freshness,
        "Description Quality": description_quality,
        "Recommendation": recommendation,
        "Days Old": days_old,
        "Job Link": redirect_url

    })

# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(jobs)

# =====================================================
# FILTERS
# =====================================================

if not df.empty:

    if freshness_filter != "All":

        df = df[
            df["Freshness"]
            ==
            freshness_filter
        ]

    if experience_filter == "0-2 Years":

        df = df[
            df["Experience Required"]
            .str.contains(
                "0|1|2",
                na=False
            )
        ]

    elif experience_filter == "2-5 Years":

        df = df[
            df["Experience Required"]
            .str.contains(
                "2|3|4|5",
                na=False
            )
        ]

    elif experience_filter == "5+ Years":

        df = df[
            df["Experience Required"]
            .str.contains(
                "5|6|7|8|9",
                na=False
            )
        ]

# =====================================================
# EMPTY CHECK
# =====================================================

if df.empty:

    st.warning(
        "No listings matched the selected filters."
    )

    st.stop()

# =====================================================
# RESUME ANALYSIS
# =====================================================

resume_skills = []

resume_match_score = None

missing_skills = []

if uploaded_resume:

    resume_text = uploaded_resume.read().decode("utf-8")

    resume_skills = extract_skills(
        resume_text
    )

    market_top_skills = [

        skill
        for skill, count
        in Counter(all_market_skills).most_common(10)
    ]

    matched = set(resume_skills).intersection(
        set(market_top_skills)
    )

    resume_match_score = round(

        (
            len(matched)
            /
            max(len(market_top_skills), 1)
        ) * 100,

        1
    )

    missing_skills = list(

        set(market_top_skills)
        -
        set(resume_skills)
    )

# =====================================================
# HERO METRICS
# =====================================================

avg_score = round(
    df["Hiring Score"].mean(),
    1
)

fresh_jobs = len(
    df[
        df["Freshness"]
        ==
        "Fresh"
    ]
)

st.markdown("## Market Snapshot")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Listings",
    len(df)
)

col2.metric(
    "Avg Hiring Score",
    avg_score
)

col3.metric(
    "Fresh Roles",
    fresh_jobs
)

col4.metric(
    "Companies",
    df["Company"].nunique()
)

# =====================================================
# RESUME INSIGHTS
# =====================================================

if uploaded_resume:

    st.divider()

    st.markdown("## Resume Intelligence")

    r1, r2 = st.columns(2)

    with r1:

        st.metric(
            "Resume Match Score",
            f"{resume_match_score}%"
        )

        st.write("### Skills Found")

        st.write(
            ", ".join(resume_skills)
        )

    with r2:

        st.write(
            "### Recommended Skills"
        )

        if missing_skills:

            for skill in missing_skills:
                st.write(f"• {skill}")

        else:

            st.success(
                "Strong market alignment detected."
            )

# =====================================================
# TABS
# =====================================================

overview_tab, market_tab, insights_tab = st.tabs([

    "Overview",
    "Market Intelligence",
    "Application Insights"
])

# =====================================================
# OVERVIEW TAB
# =====================================================

with overview_tab:

    left, right = st.columns(2)

    with left:

        st.subheader(
            "Hiring Score Distribution"
        )

        fig1 = px.histogram(

            df,

            x="Hiring Score",

            nbins=10,

            color_discrete_sequence=[
                "#06b6d4"
            ]
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with right:

        st.subheader(
            "Work Mode Distribution"
        )

        fig2 = px.pie(

            df,

            names="Work Mode",

            hole=0.55,

            color_discrete_sequence=[

                "#2563eb",
                "#7c3aed",
                "#06b6d4"
            ]
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# =====================================================
# MARKET TAB
# =====================================================

with market_tab:

    left, right = st.columns(2)

    with left:

        st.subheader(
            "Top Hiring Companies"
        )

        top_companies = (

            df["Company"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_companies.columns = [

            "Company",
            "Listings"
        ]

        fig3 = px.bar(

            top_companies,

            x="Listings",

            y="Company",

            orientation="h",

            color="Listings",

            color_continuous_scale="Turbo"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    with right:

        st.subheader(
            "Most In-Demand Skills"
        )

        skill_counts = Counter(
            all_market_skills
        )

        skill_df = pd.DataFrame(

            skill_counts.items(),

            columns=[
                "Skill",
                "Count"
            ]

        ).sort_values(

            by="Count",

            ascending=False

        ).head(10)

        fig4 = px.bar(

            skill_df,

            x="Skill",

            y="Count",

            color="Count",

            color_continuous_scale="Viridis"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

# =====================================================
# APPLICATION INSIGHTS
# =====================================================

with insights_tab:

    st.subheader(
        "Top Recommended Opportunities"
    )

    recommended_df = (

        df.sort_values(

            by="Hiring Score",

            ascending=False
        )

        .head(10)

        .reset_index(drop=True)
    )

    st.dataframe(

        recommended_df[

            [
                "Title",
                "Company",
                "Location",
                "Experience Required",
                "Work Mode",
                "Urgency",
                "Hiring Score",
                "Recommendation"
            ]
        ],

        use_container_width=True,

        hide_index=True
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(

    "RolePulse analyzes live hiring signals, recruiter urgency, market skill demand, resume alignment, and work flexibility trends using public job market data."
)
