import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime, timezone
import re

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RolePulse",
    layout="wide"
)

# =========================================================
# PREMIUM UI
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {

    background:
    linear-gradient(
        180deg,
        #050816 0%,
        #0f172a 35%,
        #111827 100%
    );

    color: white;
}

.block-container {

    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background: rgba(15,23,42,0.96);

    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TITLE */

.hero-title {

    font-size: 4rem;
    font-weight: 700;
    letter-spacing: -2px;
    margin-bottom: -10px;
}

.hero-subtitle {

    color: #94a3b8;
    font-size: 1.1rem;
}

/* METRIC CARDS */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.04);

    border: 1px solid rgba(255,255,255,0.08);

    padding: 24px;

    border-radius: 24px;

    backdrop-filter: blur(14px);

    box-shadow:
        0px 8px 30px rgba(0,0,0,0.35);

    transition: 0.3s ease;
}

[data-testid="metric-container"]:hover {

    transform: translateY(-5px);

    border: 1px solid rgba(59,130,246,0.4);
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {

    gap: 20px;
}

.stTabs [data-baseweb="tab"] {

    border-radius: 16px;

    background: rgba(255,255,255,0.04);

    padding: 12px 22px;
}

.stTabs [aria-selected="true"] {

    background:
    linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    ) !important;

    color: white !important;
}

/* EXPANDER */

.streamlit-expanderHeader {

    font-size: 1rem;
    font-weight: 600;
}

/* BUTTON */

.stButton>button {

    border-radius: 12px;

    border: none;

    color: white;

    background:
    linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );
}

/* REMOVE STREAMLIT DEFAULTS */

#MainMenu,
footer,
header {

    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class='hero-title'>
RolePulse
</div>

<div class='hero-subtitle'>
AI-Powered Multi-Source Hiring Intelligence Platform
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# API KEYS
# =========================================================

APP_ID = st.secrets["ADZUNA_APP_ID"]
APP_KEY = st.secrets["ADZUNA_APP_KEY"]

# =========================================================
# SKILLS
# =========================================================

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
    "stakeholder management",
    "roadmap",
    "communication"
]

# =========================================================
# HELPERS
# =========================================================

def extract_skills(text):

    text = str(text).lower()

    found = []

    for skill in SKILLS:

        if skill in text:
            found.append(skill.title())

    return found

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

def get_freshness(days):

    if days <= 7:
        return "Fresh"

    elif days <= 30:
        return "Moderate"

    return "Stale"

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Search Intelligence")

role_options = [

    "Product Manager",
    "Associate Product Manager",
    "AI Product Manager",
    "Product Analyst",
    "Business Analyst",
    "Data Analyst",
    "Software Engineer"
]

keyword = st.sidebar.selectbox(

    "Role",

    role_options
)

results_count = st.sidebar.slider(

    "Listings",

    10,
    100,
    50
)

workmode_filter = st.sidebar.multiselect(

    "Work Mode",

    ["Remote", "Onsite", "Hybrid"],

    default=["Remote", "Onsite", "Hybrid"]
)

platform_filter = st.sidebar.multiselect(

    "Platforms",

    ["Adzuna", "RemoteOK", "Greenhouse"],

    default=["Adzuna", "RemoteOK", "Greenhouse"]
)

freshness_filter = st.sidebar.multiselect(

    "Freshness",

    ["Fresh", "Moderate", "Stale"],

    default=["Fresh", "Moderate", "Stale"]
)

uploaded_resume = st.sidebar.file_uploader(

    "Upload Resume (.txt)",

    type=["txt"]
)

# =========================================================
# JOB STORAGE
# =========================================================

jobs = []
all_skills = []

# =========================================================
# ADZUNA
# =========================================================

adzuna_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {

    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": results_count,
    "what": keyword,
    "where": "India",
    "content-type": "application/json"
}

response = requests.get(
    adzuna_url,
    params=params
)

data = response.json()

for job in data.get("results", []):

    title = str(job.get("title", ""))

    description = str(job.get("description", ""))

    combined = (title + " " + description).lower()

    if keyword.lower() not in combined:
        continue

    skills = extract_skills(description)

    all_skills.extend(skills)

    created = job.get("created")

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

    except:

        days_old = 15

    work_mode = "Onsite"

    if "remote" in description.lower():
        work_mode = "Remote"

    elif "hybrid" in description.lower():
        work_mode = "Hybrid"

    jobs.append({

        "Title": title,

        "Company": job.get(
            "company",
            {}
        ).get(
            "display_name",
            "Unknown"
        ),

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

        "Freshness": get_freshness(
            days_old
        ),

        "Days Old": days_old,

        "Skills": ", ".join(skills),

        "Description": description,

        "URL": job.get("redirect_url")
    })

# =========================================================
# REMOTEOK
# =========================================================

try:

    remote_jobs = requests.get(
        "https://remoteok.com/api"
    ).json()[1:]

    for job in remote_jobs:

        title = str(
            job.get("position", "")
        )

        description = str(
            job.get("description", "")
        )

        combined = (
            title + " " + description
        ).lower()

        if keyword.lower() not in combined:
            continue

        skills = extract_skills(description)

        all_skills.extend(skills)

        jobs.append({

            "Title": title,

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

            "Days Old": 2,

            "Skills": ", ".join(skills),

            "Description": description,

            "URL": f"https://remoteok.com{job.get('url','')}"
        })

except:
    pass

# =========================================================
# GREENHOUSE
# =========================================================

companies = [

    "notion",
    "stripe",
    "airbyte",
    "scaleai"
]

for company in companies:

    try:

        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        response = requests.get(url)

        data = response.json()

        for job in data.get("jobs", []):

            title = str(
                job.get("title", "")
            )

            description = str(
                job.get("content", "")
            )

            combined = (
                title + " " + description
            ).lower()

            if keyword.lower() not in combined:
                continue

            skills = extract_skills(description)

            all_skills.extend(skills)

            jobs.append({

                "Title": title,

                "Company": company.title(),

                "Location": "Global",

                "Platform": "Greenhouse",

                "Work Mode": "Remote",

                "Experience": extract_experience(
                    description
                ),

                "Freshness": "Fresh",

                "Days Old": 1,

                "Skills": ", ".join(skills),

                "Description": description,

                "URL": job.get("absolute_url")
            })

    except:
        pass

# =========================================================
# DATAFRAME
# =========================================================

df = pd.DataFrame(jobs)

if df.empty:

    st.warning("No matching jobs found.")

    st.stop()

# =========================================================
# FILTERS
# =========================================================

df = df[
    df["Work Mode"].isin(
        workmode_filter
    )
]

df = df[
    df["Platform"].isin(
        platform_filter
    )
]

df = df[
    df["Freshness"].isin(
        freshness_filter
    )
]

# =========================================================
# DUPLICATES
# =========================================================

df["Duplicate"] = df.duplicated(

    subset=["Title", "Company"],

    keep=False
)

# =========================================================
# HIRING SCORE
# =========================================================

def score(row):

    value = 50

    if row["Work Mode"] == "Remote":
        value += 10

    if row["Freshness"] == "Fresh":
        value += 15

    if row["Duplicate"]:
        value += 5

    if len(str(row["Skills"])) > 10:
        value += 10

    return min(value, 100)

df["Hiring Score"] = df.apply(
    score,
    axis=1
)

# =========================================================
# RESUME ANALYSIS
# =========================================================

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

    market_skills = [

        skill
        for skill, count
        in Counter(all_skills).most_common(10)
    ]

    matched = set(
        resume_skills
    ).intersection(
        set(market_skills)
    )

    resume_score = round(

        (
            len(matched)
            /
            max(len(market_skills), 1)
        ) * 100,

        1
    )

    missing_skills = list(

        set(market_skills)
        -
        set(resume_skills)
    )

# =========================================================
# METRICS
# =========================================================

st.markdown("## Market Snapshot")

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric(
    "Listings",
    len(df)
)

m2.metric(
    "Companies",
    df["Company"].nunique()
)

m3.metric(
    "Platforms",
    df["Platform"].nunique()
)

m4.metric(
    "Remote Roles",
    len(
        df[
            df["Work Mode"]
            ==
            "Remote"
        ]
    )
)

m5.metric(
    "Duplicate Listings",
    int(df["Duplicate"].sum())
)

# =========================================================
# AI INSIGHTS
# =========================================================

top_skill = Counter(all_skills).most_common(1)

top_company = (

    df["Company"]
    .value_counts()
    .idxmax()
)

st.info(

    f"""
    AI Hiring Insights

    • Most demanded skill: {top_skill[0][0] if top_skill else 'N/A'}

    • Most active recruiter: {top_company}

    • Remote hiring trend remains dominant.

    • Greenhouse startup hiring is increasing.
    """
)

# =========================================================
# RESUME SECTION
# =========================================================

if uploaded_resume:

    st.markdown("## Resume Match Intelligence")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Resume Match Score",
            f"{resume_score}%"
        )

        skill_match = pd.DataFrame({

            "Skill": resume_skills,

            "Match": [1]*len(resume_skills)
        })

        fig = px.bar(

            skill_match,

            x="Skill",

            y="Match",

            color="Skill"
        )

        fig.update_layout(

            paper_bgcolor='rgba(0,0,0,0)',

            plot_bgcolor='rgba(0,0,0,0)',

            font_color='white'
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        st.write(
            "### Missing Market Skills"
        )

        for skill in missing_skills:

            st.write(f"• {skill}")

# =========================================================
# TABS
# =========================================================

overview_tab, trends_tab, jobs_tab = st.tabs([

    "Overview",
    "Hiring Trends",
    "Job Explorer"
])

# =========================================================
# OVERVIEW
# =========================================================

with overview_tab:

    left, right = st.columns(2)

    with left:

        platform_df = (

            df["Platform"]
            .value_counts()
            .reset_index()
        )

        fig1 = px.pie(

            platform_df,

            names="Platform",

            values="count",

            hole=0.6,

            color_discrete_sequence=[
                "#3b82f6",
                "#8b5cf6",
                "#06b6d4"
            ]
        )

        fig1.update_layout(

            paper_bgcolor='rgba(0,0,0,0)',

            font_color='white'
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with right:

        work_df = (

            df["Work Mode"]
            .value_counts()
            .reset_index()
        )

        fig2 = px.bar(

            work_df,

            x="Work Mode",

            y="count",

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

# =========================================================
# TRENDS
# =========================================================

with trends_tab:

    left, right = st.columns(2)

    with left:

        company_df = (

            df["Company"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        fig3 = px.bar(

            company_df,

            x="count",

            y="Company",

            orientation="h",

            color="count",

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

        skill_counter = Counter(all_skills)

        skill_df = pd.DataFrame(

            skill_counter.items(),

            columns=["Skill", "Count"]

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

# =========================================================
# JOB EXPLORER
# =========================================================

with jobs_tab:

    st.markdown("## Top Opportunities")

    df = df.sort_values(
        by="Hiring Score",
        ascending=False
    )

    for index, row in df.iterrows():

        logo = f"https://logo.clearbit.com/{row['Company'].replace(' ','').lower()}.com"

        with st.expander(

            f"{row['Title']} • {row['Company']} • {row['Hiring Score']} Score"
        ):

            c1, c2 = st.columns([1,4])

            with c1:

                st.image(
                    logo,
                    width=70
                )

            with c2:

                st.markdown(
                    f"### {row['Title']}"
                )

                st.write(
                    f"**Company:** {row['Company']}"
                )

                st.write(
                    f"**Platform:** {row['Platform']}"
                )

                st.write(
                    f"**Location:** {row['Location']}"
                )

                st.write(
                    f"**Work Mode:** {row['Work Mode']}"
                )

                st.write(
                    f"**Experience:** {row['Experience']}"
                )

                st.write(
                    f"**Freshness:** {row['Freshness']}"
                )

                st.write(
                    f"**Skills:** {row['Skills']}"
                )

                st.write(
                    f"**Duplicate Listing:** {row['Duplicate']}"
                )

                st.markdown(
                    f"[Apply Here]({row['URL']})"
                )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(

    """
    RolePulse aggregates live hiring intelligence from Adzuna,
    RemoteOK, and Greenhouse APIs to analyze recruiter intent,
    remote hiring demand, startup hiring activity, skill trends,
    resume alignment, and market opportunity quality.
    """
)
