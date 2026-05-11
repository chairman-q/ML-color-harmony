# 🎨 ML Color Harmony Scoring System (DEPRECATED)

![Version](https://img.shields.io/badge/Version-0.4-blue.svg) ![ReleaseType](https://img.shields.io/badge/Alpha-orange.svg) ![Status](https://img.shields.io/badge/Status-Deprecated-red.svg)

A student project as an assignment for "Machine Learning for Design" module that analyzes how harmonious a color palette is using **XGBoost expert models**.

The app supports common harmony rules:
- Analogous
- Monochromatic
- Complementary
- Split Complementary
- Triad

---

## 🌐 Deployment
This application is being deployed at [mlcolorharmony.streamlit.app](https://mlcolorharmony.streamlit.app).

---

## 📌 Overview

- Uses **5 specialist models** (`expert_*.json`), one model per harmony rule.
- Uses **XGBoost Regressor** for training and inference.
- Includes **data augmentation** to support multiple palette sizes (2-5 colors).
- Streamlit app loads the matching expert model dynamically based on selected harmony rule.

---

## Workflow

1. **Collect data** from ColorHunt and auto-label palettes by harmony type.
2. **Train expert models** for each harmony category.
3. **Run app** to score user-selected palettes.

---

## Structure

- `app.py` - Streamlit UI for interactive palette scoring.
- `colorhunt_scraper.py` - Selenium scraper + auto-labeler, writes `data_*.csv`.
- `model_trainer.py` - trains 5 XGBoost experts and saves them to `models/`.
- `evaluator.py` - CLI-style test script for quick scoring checks.
- `models/` - trained model files:
  - `expert_analogous.json`
  - `expert_monochromatic.json`
  - `expert_complementary.json`
  - `expert_split_complementary.json`
  - `expert_triad.json`

---

## 📦 Setup

Clone this repository:

```bash
git clone https://github.com/chairman-q/ML-color-harmony.git
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate virtual environment:

- **Windows (PowerShell)**
```bash
.venv\Scripts\Activate.ps1
```
- **macOS/Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the app

```bash
streamlit run app.py
```

If model files are missing, train them first:

```bash
python model_trainer.py
```

---

## Data collection and training (optional)

### 1) Scrape and auto-label training data

```bash
python colorhunt_scraper.py
```

This creates category datasets like:
- `data_analogous.csv`
- `data_monochromatic.csv`
- `data_complementary.csv`
- `data_split_complementary.csv`
- `data_triad.csv`

### 2) Train expert models

```bash
python model_trainer.py
```

Models are saved into `models/`.

---

## Quick local evaluation

Run:

```bash
python evaluator.py
```

This script runs sample palettes and prints predicted harmony score output in terminal.

---

## Notes

- Main app scoring is normalized to a **1-10 scale**.
- Ensure the `models/` folder contains all required expert JSON files before deployment.
- This project currently uses mixed English/Vietnamese text in code and UI.