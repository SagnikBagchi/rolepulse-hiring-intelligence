import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timezone

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RolePulse",
    layout="wide"
)

# =====================================================
# MODERN UI STYLING
# =====================================================

st.markdown("""
<style>

/* GLOBAL */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* MAIN CONTAINER */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* HEADINGS */

h1 {
    font-size: 3rem !important;
    font-weight: 700 !important;
    letter-spacing: -1px;
}

h2, h3 {
    font-weight: 600 !important;
}

/* KPI CARDS */

[data-testid="metric-container"] {
    background: #ffffff10;
    border: 1px solid #ffffff15;
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    border-right: 1px solid #ffffff10;
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}

.stTabs [data-baseweb="tab"] {
    padding: 12px 20px;
    border-radius: 12px;
    background-color: transparent;
}

.stTabs [aria-selected="true"] {
    background-color: #262730 !important;
}

/* DATAFRAME */

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #ffffff10;
}

/* INFO BOX */

[data-testid="stAlert"] {
    border-radius: 16px;
}

/* REMOVE STREAMLIT MENU */

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
<p style='font-size:18px; color:gray; margin-top:-10px;'>
Hiring Intent Intelligence for the Indian Job Market
</p>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# API CREDENTIALS
# =====================================================

APP_ID = st.secrets["ADZUNA_APP_ID"]
APP_KEY = st.secrets["ADZUNA_APP_KEY"]

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

for job in data.get("results", []):

    title = job.get(
        "title",
        "N/A"
    )

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

    # =====================================================
    # FRESHNESS
    # =====================================================

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

    # =====================================================
    # COMPETITION
    # =====================================================

    competition = "Medium"

    if "manager" in title.lower():
        competition = "High"

    if "director" in title.lower():
        competition = "Low"

    # =====================================================
    # DESCRIPTION QUALITY
    # =====================================================

    description_quality = "Low"

    if len(description) > 400:
        description_quality = "Moderate"

    if len(description) > 800:
        description_quality = "High"

    # =====================================================
    # SCORING
    # =====================================================

    score = 50

    if freshness == "Fresh":
        score += 20

    if description_quality == "High":
        score += 15

    if "senior" in title.lower():
        score += 5

    if "urgent" in description.lower():
        score += 10

    if "remote" in description.lower():
        score += 5

    score = min(score, 100)

    # =====================================================
    # RECOMMENDATION
    # =====================================================

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
        "Hiring Score": score,
        "Freshness": freshness,
        "Competition": competition,
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

# =====================================================
# EMPTY CHECK
# =====================================================

if df.empty:

    st.warning(
        "No listings matched the selected filters."
    )

    st.stop()

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================

avg_score = round(
    df["Hiring Score"].mean(),
    1
)

top_company = (
    df["Company"]
    .value_counts()
    .idxmax()
)

fresh_jobs = len(
    df[
        df["Freshness"]
        ==
        "Fresh"
    ]
)

# =====================================================
# HERO INSIGHTS
# =====================================================

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
    "Active Companies",
    df["Company"].nunique()
)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# INSIGHT BOX
# =====================================================

st.info(
    f"""
    Current hiring activity for **{keyword}** roles in India indicates strong recruiter participation from **{top_company}**.
    
    Recently posted opportunities continue to dominate the market, while detailed job descriptions appear strongly correlated with higher hiring intent scores.
    """
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

        st.subheader("Hiring Score Distribution")

        fig1 = px.histogram(
            df,
            x="Hiring Score",
            nbins=10
        )

        fig1.update_layout(
            height=400,
            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            )
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with right:

        st.subheader("Freshness Breakdown")

        fig2 = px.pie(
            df,
            names="Freshness",
            hole=0.55
        )

        fig2.update_layout(
            height=400,
            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            )
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

        st.subheader("Top Hiring Companies")

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
            orientation="h"
        )

        fig3.update_layout(
            height=500,
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    with right:

        st.subheader("Hiring Locations")

        top_locations = (
            df["Location"]
            .value_counts()
            .head(12)
            .reset_index()
        )

        top_locations.columns = [
            "Location",
            "Listings"
        ]

        fig4 = px.treemap(
            top_locations,
            path=["Location"],
            values="Listings"
        )

        fig4.update_layout(
            height=500
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

# =====================================================
# APPLICATION INSIGHTS
# =====================================================

with insights_tab:

    st.subheader("Top Recommended Opportunities")

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
                "Hiring Score",
                "Freshness",
                "Competition",
                "Recommendation"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Competition Landscape")

    fig5 = px.scatter(
        df,
        x="Hiring Score",
        y="Days Old",
        color="Competition",
        hover_data=[
            "Company",
            "Title"
        ]
    )

    fig5.update_layout(
        height=500
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "RolePulse analyzes live hiring signals from public job market data to identify recruiter intent, freshness, and market activity trends."
)
