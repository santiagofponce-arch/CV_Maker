# 💼 AI Job Hunting Assistant

A powerful, Streamlit-based web application that automates the tedious process of tailoring your CV and drafting highly personalized cover letters for every unique job application. 

By taking your comprehensive "Base CV" and comparing it to any job posting description, this application uses **Google's Gemini 2.5 Flash AI** to build you perfectly matching application materials in seconds.

---

## ✨ Features

- **Genuine Human-Sounding Cover Letters:** The AI is strictly prompted to avoid cliches and buzzwords (like "delve", "tapestry", "in today's fast-paced world"), outputting an email draft that sounds exactly like an experienced professional wrote it.
- **Native LaTeX Resume Compilation:** We ripped out standard raw text PDF builders and integrated true native LaTeX `pdflatex` compilation. The App generates your tailored CV in a gorgeous, ATS-optimized, flawlessly formatted professional document.
- **100% Safe:** The application does *not* hardcode your personal API keys! It securely requests users to input their own Gemini API key in a masked password box.
- **Auto Web-Scraping:** You can just paste a URL to a job posting, and the app will automatically scrape the job description.

---

## ☁️ Deploying on Streamlit Community Cloud

This repository is pre-configured to be deployed for free on [Streamlit Community Cloud](https://share.streamlit.io/). 

