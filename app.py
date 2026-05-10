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
# MODERN UI
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
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
    max-width: 1450px;
    padding-top: 2rem;
}

[data-testid="metric-container"] {

    background: linear-gradient(
        135deg,
        rgba(37,99,235,0.25),
        rgba(124,58,237,0.25)
    );

    border-radius: 20px;

    padding: 20px;

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
}

[data-testid="metric-container"]:hover {

    transform: translateY(-5px);

    transition: 0.3s ease;
}

.stTabs [aria-selected="true"] {

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed,
        #06b6d4
    ) !important;

    color: white !important;

    border-radius: 14px;
}

#MainMenu, footer, header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("RolePulse")

st.caption(
    "Multi-Source Hiring Intelligence Platform"
)

st.divider()

# =====================================================
# API CREDENTIALS
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
    "roadmap"
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

# =====================================================
# MASTER JOB LIST
# =====================================================

jobs = []

all_skills = []

# =====================================================
# 1. ADZUNA API
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

adzuna_response = requests.get(
    adzuna_url,
    params=adzuna_params
)

adzuna_data = adzuna_response.json()

for job in adzuna_data.get("results", []):

    description = job.get(
        "description",
        ""
    )

    skills = extract_skills(description)

    all_skills.extend(skills)

    jobs.append({

        "Title": job.get("title"),

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

        "Work Mode": "Remote"
        if "remote" in description.lower()
        else "Onsite",

        "Experience": extract_experience(
            description
        ),

        "Skills": ", ".join(skills),

        "Description": description,

        "URL": job.get("redirect_url")
    })

# =====================================================
# 2. REMOTEOK API
# =====================================================

try:

    remote_response = requests.get(
        "https://remoteok.com/api"
    )

    remote_jobs = remote_response.json()[1:]

    for job in remote_jobs[:20]:

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

            "Skills": ", ".join(skills),

            "Description": description,

            "URL": job.get("url")
        })

except:
    pass

# =====================================================
# 3. GREENHOUSE API
# =====================================================

greenhouse_companies = [

    "airbyte",
    "notion",
    "stripe",
    "scaleai"
]

for company in greenhouse_companies:

    try:

        greenhouse_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        response = requests.get(
            greenhouse_url
        )

        data = response.json()

        for job in data.get("jobs", [])[:10]:

            description = str(
                job.get(
                    "content",
                    ""
                )
            )

            skills = extract_skills(description)

            all_skills.extend(skills)

            jobs.append({

                "Title": job.get(
                    "title"
                ),

                "Company": company.title(),

                "Location": "Global",

                "Platform": "Greenhouse",

                "Work Mode": "Remote",

                "Experience": extract_experience(
                    description
                ),

                "Skills": ", ".join(skills),

                "Description": description,

                "URL": job.get(
                    "absolute_url"
                )
            })

    except:
        pass

# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(jobs)

# =====================================================
# EMPTY CHECK
# =====================================================

if df.empty:

    st.warning(
        "No jobs retrieved."
    )

    st.stop()

# =====================================================
# HIRING SCORE
# =====================================================

def calculate_score(row):

    score = 50

    if row["Work Mode"] == "Remote":
        score += 10

    if len(str(row["Skills"])) > 10:
        score += 15

    if row["Platform"] == "Greenhouse":
        score += 10

    return min(score, 100)

df["Hiring Score"] = df.apply(
    calculate_score,
    axis=1
)

# =====================================================
# METRICS
# =====================================================

st.markdown("## Market Snapshot")

c1, c2, c3, c4 = st.columns(4)

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

# =====================================================
# TABS
# =====================================================

overview_tab, market_tab, jobs_tab = st.tabs([

    "Overview",
    "Market Intelligence",
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

            hole=0.55,

            color_discrete_sequence=[

                "#2563eb",
                "#7c3aed",
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

        fig2 = px.bar(

            df["Work Mode"]
            .value_counts()
            .reset_index(),

            x="count",

            y="Work Mode",

            orientation="h",

            color="count",

            color_continuous_scale="Turbo"
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

            color_continuous_scale="Viridis"
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

    recommended_df = (

        df.sort_values(

            by="Hiring Score",

            ascending=False
        )

        .head(20)

        .reset_index(drop=True)
    )

    st.dataframe(

        recommended_df[

            [
                "Title",
                "Company",
                "Platform",
                "Location",
                "Experience",
                "Work Mode",
                "Skills",
                "Hiring Score"
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

    "RolePulse aggregates hiring signals from multiple live job platforms to analyze recruiter intent, remote trends, skill demand, and market hiring intelligence."
)
