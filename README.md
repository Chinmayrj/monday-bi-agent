# Monday.com AI BI Agent

## Overview

This project implements a live AI-powered Business Intelligence (BI) agent built on top of Monday.com.

The agent connects to two boards:
- Deals
- Work Orders

It supports founder-level business queries such as:
- Pipeline performance
- Closed revenue
- Sector analysis
- Quarter-based performance
- Work order fulfillment

The system executes entirely on live data (no caching or preloading) and provides visible tool execution trace for transparency.

---

## Live Demo

Hosted Prototype:

> https://monday-bi-agent-1.streamlit.app/

---

## Architecture Summary

The system follows a hybrid architecture:

- Deterministic BI Engine (Python)
- Rule-based Intent Parsing
- Cross-board join logic
- Live Monday.com API execution
- Executive summary generation
- Clarification logic
- Follow-up conversational context support

All metrics are computed deterministically to prevent hallucination in financial calculations.

---

## Features

- Live API integration with Monday.com
- Cursor-based pagination
- Data normalization layer
- Safe type conversions (numeric, date)
- Cross-board analytics (Deals ↔ Work Orders)
- Sector aggregation layer
- Clarifying questions when intent is ambiguous
- Follow-up conversational context
- Visible tool execution trace

---

## How to Run Locally

### 1. Install Dependencies
pip install -r requirements.txt

### 2. Set Environment Variable

If running locally, create a `.streamlit/secrets.toml` file:

MONDAY_API_KEY = "your_api_key_here"

### 3. Run the App
streamlit run app.py

---

## Example Queries

- How is mining performing this quarter?
- What is total pipeline value?
- Show work order performance.
- How is energy sector performing this quarter?
- What about revenue?

---

## Notes

- No caching or preloading is used.
- Data is fetched live for every valid query.
- Clarification is performed before API execution.
- Only parsed conversational metadata is stored in session state.