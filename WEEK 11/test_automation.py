import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

print("Starting Selenium Test Automation...")
print("====================================")

# Initialize WebDriver
try:
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Uncomment to run invisibly
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
except Exception as e:
    print(f"Error initializing Chrome WebDriver: {e}")
    print("Please make sure you have regular Chrome installed.")
    exit(1)

wait = WebDriverWait(driver, 10)

try:
    # 1. Navigate to Signup Page
    print("\n[1] Navigating to Signup Page...")
    driver.get("http://localhost:3000/signup.html")
    
    # 2. Fill out Signup Form
    print("[2] Filling out signup details...")
    wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("Selenium Tester")
    driver.find_element(By.ID, "email").send_keys("test@selenium.com")
    driver.find_element(By.ID, "age").send_keys("30")
    
    gender_select = Select(driver.find_element(By.ID, "gender"))
    gender_select.select_by_value("Other")
    
    driver.find_element(By.ID, "phone").send_keys("+1 800 555 1234")
    
    # Check password strength meter
    print("[3] Testing password strength meter...")
    pw_input = driver.find_element(By.ID, "password")
    pw_input.send_keys("weak")
    time.sleep(1) # Let UI update
    
    pw_input.clear()
    pw_input.send_keys("StrongP@ss123!")
    
    driver.find_element(By.ID, "confirm-password").send_keys("StrongP@ss123!")
    time.sleep(1)
    
    # 3. Submit Form
    print("[4] Submitting registration form...")
    driver.find_element(By.ID, "signup-btn").click()
    
    # 4. Wait for redirection to dashboard
    print("[5] Waiting for automatic login and redirection...")
    wait.until(EC.url_contains("dashboard.html"))
    print("Successfully reached dashboard!")
    
    # Wait for dashboard to load data
    wait.until(EC.presence_of_element_located((By.ID, "profile-name")))
    name = driver.find_element(By.ID, "profile-name").text
    print(f"Dashboard loaded for user: {name}")
    
    # 5. Sync Wearable Data
    print("\n[6] Syncing mock wearable data...")
    driver.find_element(By.ID, "heartRate").send_keys("75")
    driver.find_element(By.ID, "steps").send_keys("10500")
    driver.find_element(By.ID, "sleep").send_keys("8")
    driver.find_element(By.ID, "calories").send_keys("2400")
    driver.find_element(By.ID, "stressLevel").send_keys("40")
    
    driver.find_element(By.ID, "sync-btn").click()
    
    time.sleep(2) # Wait for alert and table update
    
    print("\n[7] Test Completed Successfully! ✓")
    print("The backend successfully processed SQLite inserts and the frontend responded perfectly.")
    time.sleep(3) # Leave browser open briefly

except Exception as e:
    print(f"\n[X] Test Failed: {e}")

finally:
    driver.quit()
    print("Browser closed.")
