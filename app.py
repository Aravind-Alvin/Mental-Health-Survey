"""
Mental Health in Tech — Interactive Streamlit Dashboard
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from data_utils import load_and_clean, get_yes_no_columns, EMPLOYEE_ORDER, WORK_INTERFERE_ORDER, LEAVE_ORDER

# --------------------------------------------------------------------------------------
# Page config & styling
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Mental Health in Tech — Dashboard",
    page_icon="🧠",
    layout="wide",
)

sns.set_theme(style="whitegrid", palette="Set2")
PALETTE_2 = ["#e07a5f", "#3d5a80"]

st.title("🧠 Mental Health in Tech Survey — Dashboard")
st.caption(
    "Explore the OSMI 2014 Mental Health in Tech Survey: demographics, treatment-seeking "
    "behavior, and workplace attitudes. Use the sidebar to filter the data."
)


# --------------------------------------------------------------------------------------
# Data loading (cached)
# --------------------------------------------------------------------------------------
@st.cache_data
def get_data(file):
    return load_and_clean(file)


with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload survey.csv (optional)", type="csv")
    st.caption("If no file is uploaded, the bundled `survey.csv` is used.")

data_source = uploaded if uploaded is not None else "survey.csv"

try:
    df = get_data(data_source)
except FileNotFoundError:
    st.error(
        "Couldn't find `survey.csv` next to this app. Upload the file using the sidebar, "
        "or place `survey.csv` in the same folder as `app.py`."
    )
    st.stop()


# --------------------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")

    age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
    age_range = st.slider("Age range", age_min, age_max, (age_min, age_max))

    genders = sorted(df["Gender_clean"].unique())
    selected_genders = st.multiselect("Gender", genders, default=genders)

    countries = sorted(df["Country_grouped"].unique())
    selected_countries = st.multiselect("Country", countries, default=countries)

    sizes = [s for s in EMPLOYEE_ORDER if s in df["company_size"].unique()]
    selected_sizes = st.multiselect("Company size", sizes, default=sizes)

    remote_options = sorted(df["remote_work"].dropna().unique())
    selected_remote = st.multiselect("Remote work?", remote_options, default=remote_options)

    st.divider()
    st.caption(f"Showing filtered subset of **{len(df)}** total cleaned responses.")

mask = (
    df["Age"].between(age_range[0], age_range[1])
    & df["Gender_clean"].isin(selected_genders)
    & df["Country_grouped"].isin(selected_countries)
    & df["company_size"].isin(selected_sizes)
    & df["remote_work"].isin(selected_remote)
)
fdf = df[mask].copy()

if fdf.empty:
    st.warning("No responses match the current filters. Try widening your selection.")
    st.stop()


# --------------------------------------------------------------------------------------
# KPI row
# --------------------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Respondents (filtered)", f"{len(fdf):,}")
k2.metric("Median age", f"{fdf['Age'].median():.0f}")
treat_rate = (fdf["treatment"] == "Yes").mean() * 100
k2.metric("Sought treatment", f"{treat_rate:.1f}%")
fam_rate = (fdf["family_history"] == "Yes").mean() * 100
k3.metric("Family history of MH illness", f"{fam_rate:.1f}%")
benefits_rate = (fdf["benefits"] == "Yes").mean() * 100
k4.metric("Has employer MH benefits", f"{benefits_rate:.1f}%")

st.divider()


# --------------------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------------------
tab_demo, tab_treat, tab_workplace, tab_corr, tab_data = st.tabs(
    ["📊 Demographics", "🩺 Treatment", "🏢 Workplace", "🔗 Correlations", "🗂️ Raw Data"]
)

# ---- Demographics tab ----
with tab_demo:
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(fdf["Age"], bins=20, kde=True, ax=ax, color="#3d5a80")
        ax.set_title("Age Distribution")
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(6, 4))
        order = fdf["Gender_clean"].value_counts().index
        sns.countplot(y="Gender_clean", data=fdf, order=order, ax=ax, hue="Gender_clean",
                      palette="Set2", legend=False)
        ax.set_title("Gender")
        ax.set_ylabel("")
        st.pyplot(fig)
        plt.close(fig)

    c3, c4 = st.columns(2)

    with c3:
        top_countries = fdf["Country_grouped"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.barplot(x=top_countries.values, y=top_countries.index, ax=ax,
                    hue=top_countries.index, palette="crest", legend=False)
        ax.set_title("Top Countries")
        ax.set_xlabel("Count")
        st.pyplot(fig)
        plt.close(fig)

    with c4:
        fig, ax = plt.subplots(figsize=(6, 5))
        sizes_present = [s for s in EMPLOYEE_ORDER if s in fdf["company_size"].unique()]
        sns.countplot(x="company_size", data=fdf, order=sizes_present, ax=ax,
                      hue="company_size", palette="flare", legend=False)
        ax.set_title("Company Size")
        ax.set_xlabel("")
        plt.xticks(rotation=20)
        st.pyplot(fig)
        plt.close(fig)

# ---- Treatment tab ----
with tab_treat:
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 5))
        fdf["treatment"].value_counts().plot.pie(
            autopct="%1.1f%%", ax=ax, colors=PALETTE_2, ylabel=""
        )
        ax.set_title("Sought Treatment?")
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.countplot(x="family_history", hue="treatment", data=fdf, ax=ax, palette=PALETTE_2)
        ax.set_title("Treatment by Family History")
        ax.set_xlabel("Family history of mental illness")
        st.pyplot(fig)
        plt.close(fig)

    c3, c4 = st.columns(2)

    with c3:
        fig, ax = plt.subplots(figsize=(6, 5))
        order = [o for o in (WORK_INTERFERE_ORDER + ["Not applicable"]) if o in fdf["work_interfere"].unique()]
        sns.countplot(x="work_interfere", hue="treatment", data=fdf, order=order, ax=ax, palette=PALETTE_2)
        ax.set_title("Work Interference vs. Treatment")
        ax.set_xlabel("")
        plt.xticks(rotation=15)
        st.pyplot(fig)
        plt.close(fig)

    with c4:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.boxplot(x="treatment", y="Age", data=fdf, ax=ax, hue="treatment",
                    palette=PALETTE_2, legend=False)
        ax.set_title("Age by Treatment-Seeking")
        st.pyplot(fig)
        plt.close(fig)

# ---- Workplace tab ----
with tab_workplace:
    st.subheader("Benefits & support programs")
    support_cols = ["benefits", "care_options", "wellness_program", "seek_help", "anonymity"]
    cols = st.columns(len(support_cols))
    for col_widget, col_name in zip(cols, support_cols):
        with col_widget:
            fig, ax = plt.subplots(figsize=(3.2, 3.5))
            sns.countplot(x=col_name, data=fdf, ax=ax, order=fdf[col_name].value_counts().index,
                          hue=col_name, palette="Set2", legend=False)
            ax.set_title(col_name.replace("_", " ").title(), fontsize=10)
            ax.set_xlabel("")
            ax.tick_params(axis="x", labelrotation=30, labelsize=8)
            st.pyplot(fig)
            plt.close(fig)

    st.subheader("Comfort discussing mental health")
    consequence_cols = ["mental_health_consequence", "coworkers", "supervisor", "obs_consequence"]
    cols2 = st.columns(len(consequence_cols))
    for col_widget, col_name in zip(cols2, consequence_cols):
        with col_widget:
            fig, ax = plt.subplots(figsize=(3.2, 3.5))
            sns.countplot(x=col_name, data=fdf, ax=ax, order=fdf[col_name].value_counts().index,
                          hue=col_name, palette="Set2", legend=False)
            ax.set_title(col_name.replace("_", " ").title(), fontsize=10)
            ax.set_xlabel("")
            ax.tick_params(axis="x", labelrotation=30, labelsize=8)
            st.pyplot(fig)
            plt.close(fig)

    st.subheader("Ease of taking medical leave")
    fig, ax = plt.subplots(figsize=(8, 4))
    order = [o for o in LEAVE_ORDER if o in fdf["leave"].unique()]
    sns.countplot(y="leave", data=fdf, order=order, ax=ax, hue="leave", palette="flare", legend=False)
    ax.set_xlabel("Count")
    ax.set_ylabel("")
    st.pyplot(fig)
    plt.close(fig)

# ---- Correlations tab ----
with tab_corr:
    st.subheader("Correlation heatmap — encoded categorical responses")
    yn_cols = get_yes_no_columns()
    encoded = fdf[yn_cols + ["treatment"]].copy()
    for c in encoded.columns:
        encoded[c] = encoded[c].astype("category").cat.codes

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(encoded.corr(), cmap="coolwarm", center=0, ax=ax)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Treatment-seeking rate by employer benefits")
    benefits_treatment = pd.crosstab(fdf["benefits"], fdf["treatment"], normalize="index") * 100
    fig, ax = plt.subplots(figsize=(7, 4))
    benefits_treatment.plot(kind="bar", ax=ax, color=PALETTE_2)
    ax.set_ylabel("% sought treatment")
    ax.set_xlabel("Employer offers mental health benefits?")
    plt.xticks(rotation=0)
    st.pyplot(fig)
    plt.close(fig)

# ---- Raw data tab ----
with tab_data:
    st.subheader("Filtered data")
    st.dataframe(fdf, use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        fdf.to_csv(index=False).encode("utf-8"),
        file_name="filtered_survey.csv",
        mime="text/csv",
    )
