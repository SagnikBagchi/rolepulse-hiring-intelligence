import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(
    page_title="RolePulse",
    layout="wide"
)

st.title("RolePulse")
st.subheader("Hiring Intent & Job Intelligence Platform")

# -----------------------------
# API Credentials
# -----------------------------

APP_ID = st.secrets["ADZUNA_APP_ID"]
APP_KEY = st.secrets["ADZUNA_APP_KEY"]

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Job Search")

keyword = st.sidebar.text_input(
    "Job Role",
    value="Product Manager"
)

location = st.sidebar.text_input(
    "Location",
    value="India"
)

results_count = st.sidebar.slider(
    "Number of Jobs",
    10,
    50,
    20
)

# -----------------------------
# API Call
# -----------------------------

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

# -----------------------------
# Process Data
# -----------------------------

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

    redirect_url = job.get(
        "redirect_url",
        ""
    )

    # -----------------------------
    # Hiring Intent Score
    # -----------------------------

    score = 50

    if salary_min > 0:
        score += 15

    if len(description) > 500:
        score += 10

    if "senior" in title.lower():
        score += 5

    if "urgent" in description.lower():
        score += 10

    score = min(score, 100)

    # -----------------------------
    # Recommendation
    # -----------------------------

    if score >= 80:
        recommendation = "High Priority Apply"

    elif score >= 65:
        recommendation = "Good Opportunity"

    else:
        recommendation = "Low Confidence"

    jobs.append({
        "Title": title,
        "Company": company,
        "Location": location_name,
        "Salary Min": salary_min,
        "Salary Max": salary_max,
        "Hiring Intent Score": score,
        "Recommendation": recommendation,
        "Job Link": redirect_url
    })

df = pd.DataFrame(jobs)

# -----------------------------
# KPI Metrics
# -----------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Jobs Retrieved",
    len(df)
)

col2.metric(
    "Average Hiring Score",
    round(df["Hiring Intent Score"].mean(), 1)
)

col3.metric(
    "Companies Hiring",
    df["Company"].nunique()
)

st.divider()

# -----------------------------
# Charts
# -----------------------------

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

# -----------------------------

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

fig2 = px.bar(
    top_companies,
    x="Company",
    y="Jobs"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------

st.subheader("Job Listings")

st.dataframe(df)

# -----------------------------

st.subheader("Key Insights")

high_priority = len(
    df[
        df["Recommendation"]
        ==
        "High Priority Apply"
    ]
)

st.write(
    f"{high_priority} jobs show strong hiring signals."
)

st.write(
    "Roles with salary transparency tend to score higher."
)

st.write(
    "Detailed job descriptions correlate with stronger hiring confidence."
)
