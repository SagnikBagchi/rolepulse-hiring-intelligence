import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="RolePulse",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    font-weight: 700;
}

.metric-card {
    background-color: #111827;
    padding: 1rem;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("RolePulse")
st.caption("Hiring Intent & Job Intelligence Platform")

st.divider()

# ---------------------------------------------------
# API CREDENTIALS
# ---------------------------------------------------

APP_ID = st.secrets["ADZUNA_APP_ID"]
APP_KEY = st.secrets["ADZUNA_APP_KEY"]

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("Search Parameters")

keyword = st.sidebar.text_input(
    "Job Role",
    value="Product Manager"
)

location = st.sidebar.text_input(
    "Location",
    value="India"
)

results_count = st.sidebar.slider(
    "Number of Listings",
    10,
    50,
    25
)

salary_filter = st.sidebar.slider(
    "Minimum Salary",
    0,
    5000000,
    0,
    step=50000
)

# ---------------------------------------------------
# API REQUEST
# ---------------------------------------------------

url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": results_count,
    "what": keyword,
    "where": location,
    "content-type": "application/json"
}

response = requests.get(url, params=params)
data = response.json()

# ---------------------------------------------------
# DATA PROCESSING
# ---------------------------------------------------

jobs = []

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

    salary_min = job.get(
        "salary_min",
        0
    )

    salary_max = job.get(
        "salary_max",
        0
    )

    created = job.get("created", "")

    redirect_url = job.get(
        "redirect_url",
        ""
    )

    # ---------------------------------------------------
    # FRESHNESS LOGIC
    # ---------------------------------------------------

    freshness = "Unknown"
    freshness_score = 50

    try:
        created_date = datetime.strptime(
            created,
            "%Y-%m-%dT%H:%M:%SZ"
        )

        days_old = (
            datetime.now(timezone.utc) -
            created_date.replace(tzinfo=timezone.utc)
        ).days

        if days_old <= 7:
            freshness = "Fresh"
            freshness_score = 100

        elif days_old <= 30:
            freshness = "Moderate"
            freshness_score = 70

        else:
            freshness = "Possibly Stale"
            freshness_score = 40

    except:
        days_old = None

    # ---------------------------------------------------
    # COMPETITION LOGIC
    # ---------------------------------------------------

    competition = "Medium"

    if "manager" in title.lower():
        competition = "High"

    if "director" in title.lower():
        competition = "Low"

    # ---------------------------------------------------
    # HIRING INTENT SCORE
    # ---------------------------------------------------

    score = 50

    if salary_min > 0:
        score += 15

    if len(description) > 800:
        score += 10

    if freshness == "Fresh":
        score += 15

    if "senior" in title.lower():
        score += 5

    if "urgent" in description.lower():
        score += 10

    score = min(score, 100)

    # ---------------------------------------------------
    # APPLICATION RECOMMENDATION
    # ---------------------------------------------------

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
        "Salary Min": salary_min,
        "Salary Max": salary_max,
        "Hiring Intent Score": score,
        "Freshness": freshness,
        "Competition": competition,
        "Recommendation": recommendation,
        "Days Old": days_old,
        "Job Link": redirect_url
    })

df = pd.DataFrame(jobs)

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

if salary_filter > 0:
    df = df[df["Salary Max"] >= salary_filter]

# ---------------------------------------------------
# EXECUTIVE INSIGHTS
# ---------------------------------------------------

st.subheader("Executive Market Insights")

avg_score = round(df["Hiring Intent Score"].mean(), 1)

top_company = (
    df["Company"]
    .value_counts()
    .idxmax()
)

fresh_jobs = len(
    df[df["Freshness"] == "Fresh"]
)

st.info(
    f"""
    Current market analysis indicates an average hiring intent score of {avg_score}.
    {top_company} appears among the most active recruiters in the selected search.
    {fresh_jobs} recently posted opportunities were identified with strong freshness signals.
    """
)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Jobs Retrieved",
    len(df)
)

col2.metric(
    "Average Hiring Score",
    avg_score
)

col3.metric(
    "Fresh Listings",
    fresh_jobs
)

col4.metric(
    "Companies Hiring",
    df["Company"].nunique()
)

st.divider()

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Market Intelligence",
    "Application Insights",
    "Job Listings"
])

# ---------------------------------------------------
# TAB 1
# ---------------------------------------------------

with tab1:

    st.subheader("Hiring Intent Distribution")

    fig1 = px.histogram(
        df,
        x="Hiring Intent Score",
        nbins=10
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.subheader("Freshness Distribution")

    fig2 = px.pie(
        df,
        names="Freshness"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------------------------------------------
# TAB 2
# ---------------------------------------------------

with tab2:

    st.subheader("Top Hiring Companies")

    top_companies = (
        df["Company"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_companies.columns = [
        "Company",
        "Jobs"
    ]

    fig3 = px.bar(
        top_companies,
        x="Company",
        y="Jobs"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.subheader("Location Hiring Heatmap")

    top_locations = (
        df["Location"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_locations.columns = [
        "Location",
        "Jobs"
    ]

    fig4 = px.treemap(
        top_locations,
        path=["Location"],
        values="Jobs"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# ---------------------------------------------------
# TAB 3
# ---------------------------------------------------

with tab3:

    st.subheader("Top Recommended Opportunities")

    recommended_df = df.sort_values(
        by="Hiring Intent Score",
        ascending=False
    ).head(10)

    st.dataframe(
        recommended_df[
            [
                "Title",
                "Company",
                "Location",
                "Hiring Intent Score",
                "Freshness",
                "Competition",
                "Recommendation"
            ]
        ]
    )

    st.subheader("Competition Analysis")

    fig5 = px.scatter(
        df,
        x="Hiring Intent Score",
        y="Salary Max",
        color="Competition",
        hover_data=["Company", "Title"]
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

# ---------------------------------------------------
# TAB 4
# ---------------------------------------------------

with tab4:

    st.subheader("Complete Job Listings")

    st.dataframe(df)

# ---------------------------------------------------
# FOOTER INSIGHTS
# ---------------------------------------------------

st.divider()

st.subheader("Platform Recommendations")

high_priority = len(
    df[
        df["Recommendation"] ==
        "Apply Immediately"
    ]
)

st.success(
    f"{high_priority} opportunities currently show strong hiring and freshness signals."
)

st.write(
    "Listings with salary transparency and detailed descriptions tend to correlate with stronger hiring intent indicators."
)

st.write(
    "Freshly posted roles generally demonstrate higher recruiter engagement probability."
)
