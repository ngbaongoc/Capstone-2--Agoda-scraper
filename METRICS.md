# 📊 Dashboard Metrics & Calculations

This document explains the key metrics used in the dashboard, how they are calculated, and the logic behind AI-driven insights.

## 1. Core Metrics

### ⭐ Agoda Score
- **Definition**: The average rating given by reviewers on Agoda.
- **Source**: Directly scraped from Agoda (`reviewer_score`).
- **Scale**: 0.0 - 10.0

### ❤️ Sentiment Score (AI)
- **Definition**: An AI-adjusted score that reflects the *actual* sentiment of the review text, penalized by negative keywords.
- **Calculation**:
  ```python
  Base Score = Reviewer Score / 10.0
  Negative Count = Number of negative keywords found in text
  Penalty = Negative Count * 0.15
  
  Sentiment Score = max(0.1, Base Score - Penalty)
  ```
- **Negative Keywords**: `ồn` (noisy), `bẩn` (dirty), `tệ` (bad), `hôi` (smell), `chán`, `thất vọng` (disappointed), `rude`, `uncomfortable`, `musty`, etc.
- **Purpose**: To detect when a high numerical rating hides a negative textual experience.

### 🏷️ AI Label
- **Definition**: Categorization of the sentiment score into human-readable labels.
- **Logic**:
  - **Tích cực (Positive)**: Sentiment Score ≥ 0.7
  - **Tiêu cực (Negative)**: Sentiment Score ≤ 0.45
  - **Trung lập (Neutral)**: Otherwise

## 2. Risk Detection

### ⚠️ Hidden Risk (Review Ảo / Conflict)
- **Definition**: Reviews that have a high numerical score but contain negative sentiment (potentially fake reviews or "passive aggressive" guests).
- **Condition**:
  - `Reviewer Score` ≥ 8.0  **AND**
  - `Sentiment Score` < 0.5

## 3. Action Center Priority

The dashboard assigns a **Priority Score** (0-100+) to each review to help staff prioritize responses. Higher score = More urgent.

### 🔢 Priority Calculation
1.  **Base Priority**: Derived from the inverse of the sentiment score.
    ```python
    Base = (1.0 - Sentiment Score) * 100
    ```
    *(Lower sentiment = Higher base priority)*

2.  **Modifiers**:
    - **+50 points**: If it is a **Conflict/Hidden Risk** review.
    - **+30 points**: If the label is **Tiêu cực (Negative)**.

### 🚦 Priority Tiers
- **🔥 Khẩn cấp (Urgent)**: Priority Score ≥ 80
- **⚠️ Cần chú ý (Warning)**: Priority Score between 50 and 79
- **📌 Theo dõi (Pending)**: Priority Score < 50

## 4. Overall Statistics

- **Data Coverage**:
  ```
  (Total Reviews Scraped / Total Reviews on Agoda) * 100
  ```
- **Category Scores**:
  - Currently simulated based on the hotel's average reviewer score with slight variations for categories like Location, Service, Cleanliness to demonstrate the UI (as these specific sub-scores aren't always available in the list view scrape).
