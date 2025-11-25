import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- This is the updated automation function for IP Restrictions ---
# It now accepts cidr_ranges_input as a parameter
def perform_ip_restriction_automation(username, password, assessment_data, cidr_ranges_input):
    
    # Setup Selenium WebDriver
    try:
        st.info("🚀 Launching the automation robot...")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
        st.success("✅ Robot launched successfully.")
    except Exception as e:
        st.error(f"Failed to start Chrome. Please ensure Chrome is installed. Error: {e}")
        return

    # 1. Login Process
    try:
        st.info("Navigating to the login page...")
        base_url = "https://nxtwave-assessments-backend-topin-prod-apis.ccbp.in/admin/"
        driver.get(base_url)
        st.info("Entering credentials...")
        wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(username)
        driver.find_element(By.ID, "id_password").send_keys(password)
        st.info("Clicking 'Log In' button...")
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        wait.until(EC.presence_of_element_located((By.ID, "user-tools")))
        st.success("✅ Login Successful! Preparing to process data.")
    except Exception as e:
        st.error(f"Login failed. Please double-check credentials. Error: {e}")
        driver.quit()
        return

    # Process each Assessment ID
    id_list = [id.strip() for id in assessment_data.strip().split('\n') if id.strip()]
    total_ids = len(id_list)
    
    st.info(f"Found {total_ids} assessments to process.")
    if total_ids == 0:
        st.warning("No data found to process.")
        driver.quit()
        return
        
    progress_bar = st.progress(0)
    
    # ==================================================================
    # CHANGE: The static CIDR ranges variable has been REMOVED from here.
    # The 'cidr_ranges_input' parameter passed to the function will be used directly.
    # ==================================================================
    
    # Main loop for each assessment
    for i, assess_id in enumerate(id_list):
        st.markdown(f"<hr>", unsafe_allow_html=True)
        try:
            st.write(f"▶️ **Processing ({i+1}/{total_ids}): {assess_id}**")

            # ==================================================================
            #                          STEP 1: Navigate and Add
            # ==================================================================
            st.subheader("Step 1: Creating Network Config")
            add_url = "https://nxtwave-assessments-backend-topin-prod-apis.ccbp.in/admin/nw_assessments_core/orgassessmentnetworkconfig/add/"
            driver.get(add_url)
            
            # ==================================================================
            #                          STEP 2: Search and Select Assessment
            # ==================================================================
            st.info("Searching for the Organisation Assessment ID...")
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-labelledby='select2-id_org_assessment-container']"))).click()
            search_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select2-search__field")))
            search_box.send_keys(assess_id[:8])
            
            suggestion_locator = (By.XPATH, f"//li[contains(@class, 'select2-results__option') and contains(text(), '{assess_id}')]")
            wait.until(EC.element_to_be_clickable(suggestion_locator)).click()
            st.success("✅ Assessment selected.")

            # ==================================================================
            #                          STEP 3: Enter CIDR Ranges and Save
            # ==================================================================
            st.info("Entering CIDR ranges...")
            cidr_box = wait.until(EC.presence_of_element_located((By.ID, "id_cidr_ranges")))
            
            # This line now uses the value passed into the function from the Streamlit UI
            cidr_box.send_keys(cidr_ranges_input)
            
            st.info("Saving the configuration...")
            driver.find_element(By.NAME, "_continue").click()
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.success")))
            st.success(f"✅ Successfully saved IP Restriction for {assess_id}.")

        except Exception as e:
            st.error(f"❌ Failed while processing ID: **{assess_id}**. See error below.")
            st.exception(e)
            continue
        finally:
            progress_bar.progress((i + 1) / total_ids)

    driver.quit()
    st.success("🎉🎉🎉 All tasks complete! The robot has finished its work.")
    st.balloons()


# --- Streamlit User Interface for the NEW Tool ---
st.set_page_config(page_title="IP Restriction Tool", layout="wide")
st.title("🔐 Turn on IP Restriction")
st.markdown("This tool enables a predefined set of IP restrictions for a list of Organisation Assessment IDs.")
st.warning("**IMPORTANT:** Please use your secure, updated password.", icon="🔒")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Login Credentials")
    username = st.text_input("Django Admin Username")
    password = st.text_input("Django Admin Password", type="password")

with col2:
    st.header("2. Input Data")
    st.markdown("Paste one or more **Organisation Assessment IDs** below, each on a new line.")
    assessment_data_input = st.text_area(
        "Paste Organisation Assessment IDs here:", 
        height=200
    )
    # ==================================================================
    # CHANGE: Added a new text area for the user to input CIDR ranges.
    # ==================================================================
    st.markdown("Enter the **CIDR Ranges** in the exact JSON array format below.")
    cidr_ranges_ui_input = st.text_area(
        "Paste CIDR Ranges here:",
        height=100,
        placeholder='[ "49.249.8.90/30", "136.232.227.202/30" ]'
    )

st.divider()

if st.button("▶️ Turn on IP Restrictions", type="primary", use_container_width=True):
    # ==================================================================
    # CHANGE: Updated validation to include the new CIDR ranges field.
    # ==================================================================
    if not username or not password or not assessment_data_input or not cidr_ranges_ui_input:
        st.error("Please fill in all fields: Username, Password, Assessment ID(s), and CIDR Ranges.")
    else:
        with st.spinner("Automation in progress..."):
            # ==================================================================
            # CHANGE: Pass the new CIDR ranges input to the automation function.
            # ==================================================================
            perform_ip_restriction_automation(username, password, assessment_data_input, cidr_ranges_ui_input)