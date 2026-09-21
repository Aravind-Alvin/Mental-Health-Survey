"""
Shared cleaning utilities for the OSMI Mental Health in Tech Survey dataset.
Used by both the EDA notebook and the Streamlit app so cleaning logic stays consistent.
"""

import pandas as pd
import numpy as np

GENDER_MAP = {
    # Male
    "male": "Male", "m": "Male", "man": "Male", "male-ish": "Male", "maile": "Male",
    "cis male": "Male", "mal": "Male", "male (cis)": "Male", "make": "Male",
    "male ": "Male", "msle": "Male", "mail": "Male", "malr": "Male", "cis man": "Male",
    # Female
    "female": "Female", "f": "Female", "woman": "Female", "femake": "Female",
    "cis female": "Female", "cis-female/femme": "Female", "female (cis)": "Female",
    "femail": "Female", "female ": "Female",
    # Non-binary / other / trans / genderqueer -> grouped as "Other/Non-binary"
    "trans-female": "Other/Non-binary", "something kinda male?": "Other/Non-binary",
    "queer/she/they": "Other/Non-binary", "non-binary": "Other/Non-binary",
    "nah": "Other/Non-binary", "all": "Other/Non-binary", "enby": "Other/Non-binary",
    "fluid": "Other/Non-binary", "genderqueer": "Other/Non-binary",
    "androgyne": "Other/Non-binary", "agender": "Other/Non-binary",
    "trans woman": "Other/Non-binary", "male leaning androgynous": "Other/Non-binary",
    "guy (-ish) ^_^": "Other/Non-binary", "trans-female ": "Other/Non-binary",
    "female (trans)": "Other/Non-binary", "queer": "Other/Non-binary",
    "ostensibly male, unsure what that really means": "Other/Non-binary",
    "a little about you": "Other/Non-binary", "p": "Other/Non-binary",
    "neuter": "Other/Non-binary",
}

# Excel silently auto-corrected some "N-M employees" ranges into dates on entry.
# We restore the intended human-readable order here.
EMPLOYEE_ORDER_MAP = {
    "01-May": "1-5",
    "Jun-25": "6-25",
    "26-100": "26-100",
    "100-500": "100-500",
    "500-1000": "500-1000",
    "More than 1000": "1000+",
}
EMPLOYEE_ORDER = ["1-5", "6-25", "26-100", "100-500", "500-1000", "1000+"]

WORK_INTERFERE_ORDER = ["Never", "Rarely", "Sometimes", "Often"]
LEAVE_ORDER = ["Very easy", "Somewhat easy", "Don't know", "Somewhat difficult", "Very difficult"]


def load_and_clean(path_or_buffer) -> pd.DataFrame:
    """Load the raw survey CSV and return a cleaned DataFrame ready for analysis."""
    df = pd.read_csv(path_or_buffer)

    # --- Timestamp ---
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)

    # --- Age: keep only plausible working-age respondents (18-75) ---
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df.loc[(df["Age"] < 15) | (df["Age"] > 80), "Age"] = np.nan

    # --- Gender: normalize free text into 3 buckets ---
    df["Gender_clean"] = (
        df["Gender"].astype(str).str.strip().str.lower().map(GENDER_MAP).fillna("Other/Non-binary")
    )

    # --- no_employees: fix Excel date auto-correction & order categories ---
    df["company_size"] = df["no_employees"].map(EMPLOYEE_ORDER_MAP).fillna(df["no_employees"])
    df["company_size"] = pd.Categorical(df["company_size"], categories=EMPLOYEE_ORDER, ordered=True)

    # --- work_interfere: ordered categorical, keep NaN as "Not applicable / No answer" ---
    df["work_interfere"] = df["work_interfere"].fillna("Not applicable")
    wi_order = WORK_INTERFERE_ORDER + ["Not applicable"]
    df["work_interfere"] = pd.Categorical(df["work_interfere"], categories=wi_order, ordered=True)

    # --- leave: ordered categorical ---
    df["leave"] = pd.Categorical(df["leave"], categories=LEAVE_ORDER, ordered=True)

    # --- self_employed: fill missing with "No" (majority class / survey default) ---
    df["self_employed"] = df["self_employed"].fillna("No")

    # --- state: only meaningful for US respondents; keep NaN as "N/A (non-US)" ---
    df["state"] = df["state"].fillna("N/A (non-US)")

    # --- comments: binary flag is often more useful than the free text itself ---
    df["has_comment"] = df["comments"].notna()

    # --- Country: collapse rare countries (<5 respondents) into "Other" for cleaner charts ---
    country_counts = df["Country"].value_counts()
    common_countries = country_counts[country_counts >= 5].index
    df["Country_grouped"] = df["Country"].where(df["Country"].isin(common_countries), "Other")

    # --- Drop exact duplicate rows ---
    df = df.drop_duplicates()

    return df


def get_yes_no_columns():
    """Columns that are simple Yes/No/Don't know style responses, useful for grouped analysis."""
    return [
        "family_history", "remote_work", "tech_company", "benefits",
        "care_options", "wellness_program", "seek_help", "anonymity",
        "mental_health_consequence", "phys_health_consequence", "coworkers",
        "supervisor", "mental_health_interview", "phys_health_interview",
        "mental_vs_physical", "obs_consequence",
    ]
