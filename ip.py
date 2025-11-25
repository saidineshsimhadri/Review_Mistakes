import streamlit as st
import pandas as pd
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


# --------------------------------------------------------------------
# IP Restriction Automation Function
# --------------------------------------------------------------------
def perform_ip_restriction_automation(username, password, assessment_data, cidr_ranges_input):

    st.info("🚀 Launching the automation robot...")

    # ---------- Setup WebDriver ----------
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-features=NetworkService')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--disable-features=VizDisplayCompositor')

        if os.path.exists('/usr/bin/chromium'):
            options.binary_location = '/usr/bin/chromium'
            service = Service(executable_path='/usr/bin/chromedriver')
        else:
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)

    except Exception as e:
        st.error(f"❌ Failed to start Chrome WebDriver: {e}")
        return

    # ---------- LOGIN ----------
    try:
        st.info("Navigating to the login page...")
        base_url = "https://nxtwave-assessments-backend-topin-prod-apis.ccbp.in/admin/"
        driver.get(base_url)

        st.info("Entering credentials...")
        wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(username)
        driver.find_element(By.ID, "id_password").send_keys(password)

        st.info("Clicking 'Log in'...")
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        wait.until(EC.presence_of_element_located((By.ID, "user-tools")))
        st.success("✅ Login Successful!")

    except Exception as e:
        st.error(f"Login failed. Please check credentials. Error: {e}")
        driver.quit()
        return

    # ---------- Process Assessment IDs ----------
    id_list = [id.strip() for id in assessment_data.strip().split("\n") if id.strip()]
    total_ids = len(id_list)

    if total_ids == 0:
        st.warning("No Assessment IDs found.")
        driver.quit()
        return

    st.info(f"Found {total_ids} assessments to process.")
    progress_bar = st.progress(0)

    # ---------- MAIN LOOP ----------
    for i, assess_id in enumerate(id_list):
        try:
            st.write(f"▶️ Processing {i+1}/{total_ids}: **{assess_id}**")
            st.markdown("<hr>", unsafe_allow_html=True)

            # Step 1: Navigate
            add_url = "https://nxtwave-assessments-backend-topin-prod-apis.ccbp.in/admin/nw_assessments_core/orgassessmentnetworkconfig/add/"
            driver.get(add_url)

            # Step 2: Select Assessment
            st.info("Selecting Assessment...")
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-labelledby='select2-id_org_assessment-container']"))).click()

            search_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select2-search__field")))
            search_box.send_keys(assess_id[:8])

            suggestion = (By.XPATH, f"//li[contains(@class,'select2-results__option') and contains(text(), '{assess_id}')]")
            wait.until(EC.element_to_be_clickable(suggestion)).click()
            st.success("Assessment selected.")

            # Step 3: Enter CIDR Ranges
            st.info("Entering CIDR ranges...")
            cidr_box = wait.until(EC.presence_of_element_located((By.ID, "id_cidr_ranges")))
            cidr_box.clear()
            cidr_box.send_keys(cidr_ranges_input)

            # Save
            st.info("Saving...")
            driver.find_element(By.NAME, "_continue").click()

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.success")))
            st.success(f"✅ Successfully saved for {assess_id}")

        except Exception as e:
            st.error(f"❌ Failed for Assessment: {assess_id}")
            st.exception(e)

        finally:
            progress_bar.progress((i + 1) / total_ids)

    driver.quit()
    st.success("🎉 All tasks completed!")
    st.balloons()


# --------------------------------------------------------------------
# Streamlit UI
# --------------------------------------------------------------------

st.set_page_config(page_title="IP Restriction Tool", layout="wide")
st.title("🔐 Turn on IP Restriction Automatically")
st.warning("Use your secure Django Admin password.", icon="🔒")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Login Credentials")
    username = st.text_input("Django Admin Username")
    password = st.text_input("Django Admin Password", type="password")

with col2:
    st.header("2. Input Data")
    assessment_data_input = st.text_area("Paste Organisation Assessment IDs:", height=200)
    cidr_ranges_ui_input = st.text_area(
        "CIDR Ranges (JSON array):",
        height=120,
        placeholder='[ "49.249.8.90/30", "136.232.227.202/30" ]'
    )

st.divider()

if st.button("▶️ Run Automation", use_container_width=True):
    if not username or not password or not assessment_data_input or not cidr_ranges_ui_input:
        st.error("Please fill all fields.")
    else:
        perform_ip_restriction_automation(username, password, assessment_data_input, cidr_ranges_ui_input)
