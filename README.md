# Mental Health in Tech — Streamlit Dashboard

An interactive dashboard for the OSMI 2014 Mental Health in Tech Survey.

## Files

- `app.py` — the Streamlit app
- `data_utils.py` — shared data-cleaning logic (also used by the companion Jupyter notebook)
- `survey.csv` — the bundled dataset (you can also upload your own from the sidebar)
- `requirements.txt` — Python dependencies

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Deploy

### Option A: Streamlit Community Cloud (free, easiest)
1. Push this folder to a GitHub repo (keep `app.py`, `data_utils.py`, `survey.csv`, and
   `requirements.txt` at the repo root, or note the subfolder path).
2. Go to https://share.streamlit.io, sign in with GitHub, and click "New app".
3. Point it at your repo/branch and set the main file path to `app.py`.
4. Deploy — it will install `requirements.txt` automatically.

### Option B: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Build and run:
```bash
docker build -t mental-health-dashboard .
docker run -p 8501:8501 mental-health-dashboard
```

### Option C: Any cloud VM / server
Install Python 3.10+, `pip install -r requirements.txt`, then run:
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
and open the appropriate port in your firewall/security group.

## Features

- Sidebar filters: age range, gender, country, company size, remote work
- KPI cards: respondent count, median age, treatment rate, family history rate, benefits rate
- Tabs: Demographics, Treatment, Workplace, Correlations, Raw Data
- CSV download of the currently filtered data
- Optional CSV upload to analyze a different (same-schema) dataset
