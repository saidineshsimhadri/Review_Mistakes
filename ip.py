import os
import time
import platform
import subprocess
import streamlit as st

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_chrome_driver_setup():
    """
    Automatically detect environment and configure Chrome/ChromeDriver.
    Returns (service, options) or raises an error.
    """
    options = webdriver.ChromeOptions()

    # Essential options for all environments
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36"
    )

    # Memory optimizations
    options.add_argument("--disable-dev-tools")
    options.add_argument("--disable-background-timer-throttling")

    system_os = platform.system()

    # Detect Streamlit Cloud environment
    if os.path.exists("/usr/bin/chromedriver"):
        st.info("✅ Detected Cloud Environment (Streamlit Cloud)")

        if os.path.exists("/usr/bin/chromium"):
            options.binary_location = "/usr/bin/chromium"
        elif os.path.exists("/usr/bin/google-chrome"):
            options.binary_location = "/usr/bin/google-chrome"
        elif os.path.exists("/usr/bin/chromium-browser"):
            options.binary_location = "/usr/bin/chromium-browser"

        service = Service("/usr/bin/chromedriver")
        return service, options

    # Local System (Windows/Mac)
    st.info(f"🖥️ Detected Local Environment: {system_os}")

    try:
        from webdriver_manager.chrome import ChromeDriverManager

        if system_os == "Windows":
            options.add_argument("--disable-features=RendererCodeIntegrity")
            options.add_argument("--remote-debugging-port=9222")

            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(
                    r"~\AppData\Local\Google\Chrome\Application\chrome.exe"
                ),
            ]

            for path in chrome_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    st.info(f"Found Chrome at: {path}")
                    break

        elif system_os == "Darwin":
            chrome_path = (
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            )
            if os.path.exists(chrome_path):
                options.binary_location = chrome_path
                st.info(f"Found Chrome at: {chrome_path}")

        service = Service(ChromeDriverManager().install())
        return service, options

    except ImportError:
        st.error("❌ webdriver-manager not installed!")
        st.code("pip install webdriver-manager", language="bash")
        raise Exception(
            "Please install webdriver-manager: pip install webdriver-manager"
        )

    except Exception as e:
        st.error(f"❌ ChromeDriver setup failed: {e}")
        raise


def perform_ip_restriction_automation(
    username, password, assessment_data, cidr_ranges_input
):
    """Main automation function to configure IP restrictions."""
    st.info("🚀 Launching the automation robot...")

    try:
        service, options = get_chrome_driver_setup()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        wait = WebDriverWait(driver, 60)
        st.success("✅ Chrome WebDriver initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to start Chrome WebDriver: {e}")
        st.info("💡 Troubleshooting tips:")
        st.markdown(
            """
            - **Windows**: Make sure Chrome is installed in default location  
            - **Mac**: Keep Chrome inside /Applications  
            - **Cloud**: Ensure packages.txt contains chromium & chromium-driver  
            - Install requirements: `pip install selenium webdriver-manager`
            """
        )
        return

    # LOGIN
    try:
        st.info("Navigating to login page...")
        base_url = (
            "https://nxtwave-assessments-backend-topin-prod-apis.ccbp.in/admin/"
        )
        driver.get(base_url)
        time.sleep(2)

        st.info("Entering credentials...")
        wait.until(
            EC.presence_of_element_located((By.ID, "id_username"))
        ).send_keys(username)

        driver.find_element(By.ID, "id_password").send_keys(password)

        st.info("Clicking 'Log in'...")
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        wait.until(EC.presence_of_element_located((By.ID, "user-tools")))
        st.success("✅ Login Successful!")

    except Exception as e:
        st.error(f"Login failed. Check credentials. Error: {e}")
        driver.quit()
        return

    # PROCESS INPUT
    id_list = [
        line.strip()
        for line in assessment_data.strip().split("\n")
        if line.strip()
    ]

    if not id_list:
        st.warning("No Assessment IDs found.")
        driver.quit()
        return

    total_ids = len(id_list)
    st.info(f"Found {total_ids} assessments to process.")
    progress_bar = st.progress(0)

    # MAIN LOOP
    for index, assess_id in enumerate(id_list):
        try:
            st.write(f"▶️ Processing {index + 1}/{total_ids}: **{assess_id}**")
            st.markdown("<hr>", unsafe_allow_html=True)

            driver.get(
                "https://nxtwave-assessments-backend-topin-prod-apis.ccbp.in/"
                "admin/nw_assessments_core/orgassessmentnetworkconfig/add"
            )
            time.sleep(1)

            st.info("Selecting Assessment...")
            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "span[aria-labelledby='select2-id_org_assessment-container']",
                    )
                )
            ).click()

            search_box = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "select2-search__field")
                )
            )
            search_box.send_keys(assess_id[:8])
            time.sleep(0.5)

            suggestion = (
                By.XPATH,
                f"//li[contains(@class,'select2-results__option') "
                f"and contains(text(), '{assess_id}')]",
            )
            wait.until(EC.element_to_be_clickable(suggestion)).click()
            st.success("Assessment selected.")

            st.info("Entering CIDR ranges...")
            cidr_box = wait.until(
                EC.presence_of_element_located((By.ID, "id_cidr_ranges"))
            )
            cidr_box.clear()
            cidr_box.send_keys(cidr_ranges_input)

            st.info("Saving...")
            driver.find_element(By.NAME, "_continue").click()

            try:
                wait.until(
                    EC.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "li.success, div.success, ul.success",
                        )
                    )
                )
                st.success(f"✅ Successfully saved for {assess_id}")
            except TimeoutException:
                st.warning(
                    f"⚠️ Could not confirm save for {assess_id}. "
                    "It may have succeeded anyway."
                )

        except Exception as e:
            st.error(f"❌ Failed for Assessment: {assess_id}")
            st.exception(e)

        finally:
            progress_bar.progress((index + 1) / total_ids)
            time.sleep(0.5)

    driver.quit()
    st.success("🎉 All tasks completed!")
    st.snow()


# ---------------- UI ----------------

st.set_page_config(page_title="IP Restriction Tool", layout="wide")
st.title("🔐 Turn on IP Restriction Automatically")
st.warning("Use your secure Django Admin password.", icon="🔒")

with st.expander("ℹ️ System Information"):
    st.write(f"**Operating System:** {platform.system()} {platform.release()}")
    st.write(f"**Python Version:** {platform.python_version()}")
    st.write(f"**Architecture:** {platform.machine()}")

with st.expander("📋 Setup Instructions"):
    st.markdown(
        """
        ### Local Setup (Windows/Mac)
        ```
        pip install streamlit selenium webdriver-manager
        ```
        Run:
        ```
        streamlit run app.py
        ```

        ### Cloud Deployment (Streamlit Cloud)

        **packages.txt**
        ```
        chromium
        chromium-driver
        ```

        **requirements.txt**
        ```
        streamlit
        selenium==4.15.2
        webdriver-manager
        ```
        """
    )

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Login Credentials")
    username = st.text_input("Django Admin Username")
    password = st.text_input("Django Admin Password", type="password")

with col2:
    st.header("2. Input Data")
    assessment_data_input = st.text_area(
        "Paste Organisation Assessment IDs:", height=200
    )
    cidr_ranges_ui_input = st.text_area(
        "CIDR Ranges (JSON array):",
        height=120,
        placeholder='[ "49.249.8.90/30", "136.232.227.202/30" ]',
    )

st.divider()

if st.button("▶️ Run Automation", use_container_width=True):
    if not all(
        [username, password, assessment_data_input, cidr_ranges_ui_input]
    ):
        st.error("Please fill all fields.")
    else:
        perform_ip_restriction_automation(
            username,
            password,
            assessment_data_input,
            cidr_ranges_ui_input,
        )
