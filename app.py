import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
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
# APPLE-LIKE UI
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(
        180deg,
        #0a0a0a 0%,
        #111827 35%,
        #0f172a 100%
    );
    color: white;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* HEADER */

.main-title {
    font-size: 4rem;
    font-weight: 700;
    letter-spacing: -2px;
    margin-bottom: 0px;
}

.subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-top: -10px;
}

/* METRIC CARDS */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.04);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 24px;

    padding: 24px;

    backdrop-filter: blur(18px);

    box-shadow:
        0px 8px 30px rgba(0,0,0,0.35);

    transition: 0.3s ease;
}

[data-testid="metric-container"]:hover {

    transform: translateY(-6px);

    border: 1px solid rgba(59,130,246,0.5);
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background: rgba(15,23,42,0.95);

    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 18px;
}

.stTabs [data-baseweb="tab"] {

    border-radius: 16px;

    padding: 12px 22px;

    background: rgba(255,255,255,0.04);
}

.stTabs [aria-selected="true"] {

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    ) !important;

    color: white !important;
}

/* TABLE */

[data-testid="stDataFrame"] {

    border-radius: 20px;

    overflow: hidden;

    border: 1px solid rgba(255,255,255,0.06);
}

/* BUTTONS */

.stButton>button {

    border-radius: 14px;

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    color: white;

    border: none;
}

/* REMOVE DEFAULTS */

#MainMenu,
footer,
header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class='main-title'>
RolePulse
</div>

<div class='subtitle'>
Multi-Source Hiring Intelligence Platform
</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# API KEYS
# =====================================================

APP_ID = st.secrets["ADZUNA_APP_ID"]
APP_KEY = st.secrets["ADZUNA_APP_KEY"]

# =====================================================
# SKILL ENGINE
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
    "agile",
    "scrum",
    "ai",
    "machine learning",
    "communication",
    "roadmap",
    "stakeholder management"
]

def extract_skills(text):

    text = str(text).lower()

    found = []

    for skill in SKILLS:

        if skill in text:
            found.append(skill.title())

    return found

# =====================================================
# EXPERIENCE ENGINE
# =====================================================

def extract_experience(text):

    patterns = [

        r'(\\d+)\\+?\\s*years',
        r'(\\d+)\\s*-\\s*(\\d+)\\s*years',
        r'(\\d+)\\+?\\s*yrs'
    ]

    text = str(text).lower()

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)} Years"

            return f"{match.group(1)}+ Years"

    return "Not Specified"

# =====================================================
# FRESHNESS ENGINE
# =====================================================

def freshness_logic(created):

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
            freshness = "Stale"

        return freshness, days_old

    except:

        return "Unknown", None

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Search Intelligence")

keyword = st.sidebar.text_input(
    "Role",
    value="Product Manager"
)

results_count = st.sidebar.slider(
    "Listings",
    10,
    100,
    50
)

platform_filter = st.sidebar.multiselect(

    "Platforms",

    [
        "Adzuna",
        "RemoteOK",
        "Greenhouse"
    ],

    default=[
        "Adzuna",
        "RemoteOK",
        "Greenhouse"
    ]
)

workmode_filter = st.sidebar.multiselect(

    "Work Mode",

    [
        "Remote",
        "Onsite",
        "Hybrid"
    ],

    default=[
        "Remote",
        "Onsite",
        "Hybrid"
    ]
)

freshness_filter = st.sidebar.multiselect(

    "Listing Freshness",

    [
        "Fresh",
        "Moderate",
        "Stale"
    ],

    default=[
        "Fresh",
        "Moderate",
        "Stale"
    ]
)

uploaded_resume = st.sidebar.file_uploader(
    "Upload Resume (.txt)",
    type=["txt"]
)

# =====================================================
# MASTER DATA
# =====================================================

jobs = []

all_skills = []

# =====================================================
# ADZUNA API
# =====================================================

adzuna_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

adzuna_params = {

    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": results_count,
    "what": keyword,
    "where": "India",
    "content-type": "application/json"
}

response = requests.get(
    adzuna_url,
    params=adzuna_params
)

adzuna_data = response.json()

for job in adzuna_data.get("results", []):

    description = str(
        job.get("description", "")
    )

    skills = extract_skills(description)

    all_skills.extend(skills)

    freshness, days_old = freshness_logic(
        job.get("created", "")
    )

    title = job.get("title", "")

    company = job.get(
        "company",
        {}
    ).get(
        "display_name",
        "Unknown"
    )

    work_mode = "Onsite"

    if "remote" in description.lower():
        work_mode = "Remote"

    elif "hybrid" in description.lower():
        work_mode = "Hybrid"

    jobs.append({

        "Title": title,

        "Company": company,

        "Location": job.get(
            "location",
            {}
        ).get(
            "display_name",
            "India"
        ),

        "Platform": "Adzuna",

        "Work Mode": work_mode,

        "Experience": extract_experience(
            description
        ),

        "Freshness": freshness,

        "Days Old": days_old,

        "Skills": ", ".join(skills),

        "URL": job.get("redirect_url")
    })

# =====================================================
# REMOTEOK API
# =====================================================

try:

    remote_response = requests.get(
        "https://remoteok.com/api"
    )

    remote_jobs = remote_response.json()[1:]

    for job in remote_jobs[:25]:

        description = str(
            job.get("description", "")
        )

        skills = extract_skills(description)

        all_skills.extend(skills)

        jobs.append({

            "Title": job.get("position"),

            "Company": job.get(
                "company",
                "Unknown"
            ),

            "Location": "Remote",

            "Platform": "RemoteOK",

            "Work Mode": "Remote",

            "Experience": extract_experience(
                description
            ),

            "Freshness": "Fresh",

            "Days Old": 1,

            "Skills": ", ".join(skills),

            "URL": f"https://remoteok.com{job.get('url','')}"
        })

except:
    pass

# =====================================================
# GREENHOUSE API
# =====================================================

greenhouse_companies = [

    "notion",
    "stripe",
    "airbyte",
    "scaleai"
]

for company in greenhouse_companies:

    try:

        greenhouse_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        response = requests.get(
            greenhouse_url
        )

        data = response.json()

        for job in data.get("jobs", [])[:15]:

            description = str(
                job.get("content", "")
            )

            skills = extract_skills(description)

            all_skills.extend(skills)

            jobs.append({

                "Title": job.get("title"),

                "Company": company.title(),

                "Location": "Global",

                "Platform": "Greenhouse",

                "Work Mode": "Remote",

                "Experience": extract_experience(
                    description
                ),

                "Freshness": "Fresh",

                "Days Old": 2,

                "Skills": ", ".join(skills),

                "URL": job.get("absolute_url")
            })

    except:
        pass

# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(jobs)

# =====================================================
# DUPLICATE DETECTION
# =====================================================

df["Duplicate"] = df.duplicated(
    subset=["Title", "Company"],
    keep=False
)

# =====================================================
# HIRING SCORE
# =====================================================

def calculate_score(row):

    score = 50

    if row["Work Mode"] == "Remote":
        score += 10

    if row["Freshness"] == "Fresh":
        score += 15

    if row["Platform"] == "Greenhouse":
        score += 10

    if row["Duplicate"]:
        score += 5

    if len(str(row["Skills"])) > 10:
        score += 10

    return min(score, 100)

df["Hiring Score"] = df.apply(
    calculate_score,
    axis=1
)

# =====================================================
# FILTERS
# =====================================================

df = df[
    df["Platform"].isin(platform_filter)
]

df = df[
    df["Work Mode"].isin(workmode_filter)
]

df = df[
    df["Freshness"].isin(freshness_filter)
]

# =====================================================
# RESUME ANALYSIS
# =====================================================

resume_score = None

resume_skills = []

missing_skills = []

if uploaded_resume:

    resume_text = uploaded_resume.read().decode(
        "utf-8"
    )

    resume_skills = extract_skills(
        resume_text
    )

    top_market_skills = [

        skill
        for skill, count
        in Counter(all_skills).most_common(10)
    ]

    matched = set(resume_skills).intersection(
        set(top_market_skills)
    )

    resume_score = round(

        (
            len(matched)
            /
            max(len(top_market_skills), 1)
        ) * 100,

        1
    )

    missing_skills = list(

        set(top_market_skills)
        -
        set(resume_skills)
    )

# =====================================================
# HERO METRICS
# =====================================================

st.markdown("## Market Snapshot")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Listings",
    len(df)
)

c2.metric(
    "Companies",
    df["Company"].nunique()
)

c3.metric(
    "Platforms",
    df["Platform"].nunique()
)

c4.metric(
    "Remote Roles",
    len(
        df[
            df["Work Mode"]
            ==
            "Remote"
        ]
    )
)

c5.metric(
    "Duplicates",
    int(df["Duplicate"].sum())
)

# =====================================================
# RESUME SECTION
# =====================================================

if uploaded_resume:

    st.divider()

    st.markdown("## Resume Match Intelligence")

    r1, r2 = st.columns(2)

    with r1:

        st.metric(
            "Resume Match Score",
            f"{resume_score}%"
        )

        st.write(
            "### Detected Skills"
        )

        st.write(
            ", ".join(resume_skills)
        )

    with r2:

        st.write(
            "### Missing Market Skills"
        )

        for skill in missing_skills:

            st.write(f"• {skill}")

# =====================================================
# TABS
# =====================================================

overview_tab, trends_tab, jobs_tab = st.tabs([

    "Overview",
    "Hiring Trends",
    "Job Listings"
])

# =====================================================
# OVERVIEW
# =====================================================

with overview_tab:

    left, right = st.columns(2)

    with left:

        st.subheader(
            "Hiring Source Distribution"
        )

        fig1 = px.pie(

            df,

            names="Platform",

            hole=0.6,

            color_discrete_sequence=[

                "#3b82f6",
                "#8b5cf6",
                "#06b6d4"
            ]
        )

        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with right:

        st.subheader(
            "Work Mode Distribution"
        )

        mode_df = (

            df["Work Mode"]
            .value_counts()
            .reset_index()
        )

        fig2 = px.bar(

            mode_df,

            x="count",

            y="Work Mode",

            orientation="h",

            color="count",

            color_continuous_scale="Turbo"
        )

        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# =====================================================
# HIRING TRENDS
# =====================================================

with trends_tab:

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

            color_continuous_scale="Viridis"
        )

        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
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
            all_skills
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

        fig4 = px.treemap(

            skill_df,

            path=["Skill"],

            values="Count",

            color="Count",

            color_continuous_scale="Turbo"
        )

        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

# =====================================================
# JOB LISTINGS
# =====================================================

with jobs_tab:

    st.subheader(
        "Top Opportunities"
    )

    display_df = (

        df.sort_values(

            by="Hiring Score",

            ascending=False
        )

        .reset_index(drop=True)
    )

    st.dataframe(

        display_df[

            [
                "Title",
                "Company",
                "Platform",
                "Location",
                "Work Mode",
                "Experience",
                "Freshness",
                "Hiring Score",
                "Duplicate",
                "URL"
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

    "RolePulse aggregates live hiring intelligence from Adzuna, RemoteOK, and Greenhouse APIs to analyze market demand, hiring trends, recruiter activity, resume alignment, and opportunity quality."
)
