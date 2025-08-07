# Assessment 'Review Mistakes' Automation Tool

## Prerequisites

- Python 3.7+
- Google Chrome browser installed

## Setup

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```
   streamlit run app.py/automation_app.py
   ```

3. The app will open in your browser. Fill in your credentials and assessment data as instructed.

## Notes

- The app uses Selenium and will launch a Chrome window for automation.
- If you encounter issues with ChromeDriver, ensure your Chrome browser is up to date.
- If you want to run in headless mode (no visible Chrome window), uncomment the `options.add_argument("--headless")` line in the code. 