import time
import os
import re
import json
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramLikeChecker:
    def __init__(self, culprit_username, victim_username):
        self.culprit_username = culprit_username
        self.victim_username = victim_username
        self.driver = None
        self.wait = None
        self.like_count = 0

        # Load credentials from config.json, or fall back to environment variables
        self.config = None
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            env_username = os.getenv("IG_USERNAME")
            env_password = os.getenv("IG_PASSWORD")
            if env_username and env_password:
                self.config = {"username": env_username, "password": env_password}
                logging.info("🔐 Using Instagram credentials from environment variables IG_USERNAME/IG_PASSWORD.")
            else:
                logging.error("❌ Missing credentials. Provide config.json or set IG_USERNAME and IG_PASSWORD env vars.")
                exit(1)

    def setup_driver(self):
        """Setup Chrome driver"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 15)
            logging.info("✅ Chrome driver setup successful!")
        except Exception as e:
            logging.error(f"❌ Failed to setup Chrome driver: {e}")
            exit(1)

    def login(self):
        """Login to Instagram"""
        self.driver.get("https://www.instagram.com/accounts/login/")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.config["username"])
        self.wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(self.config["password"])
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        time.sleep(5)
        logging.info("✅ Logged in successfully!")

    def open_friend_profile(self):
        """Open the culprit's Instagram profile"""
        self.driver.get(f"https://www.instagram.com/{self.culprit_username}/")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//header")))
        logging.info(f"📂 Opened profile: {self.culprit_username}")

    def collect_post_links(self, max_posts=None):
        """Scroll profile and collect all post URLs"""
        logging.info("🔍 Collecting post links...")
        collected = []
        seen = set()
        last_height = -1
        while True:
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
            for post in posts:
                link = post.get_attribute("href")
                if link and link not in seen:
                    seen.add(link)
                    collected.append(link)
                    if max_posts and len(collected) >= max_posts:
                        return collected
            # Scroll to load more posts
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        logging.info(f"📌 Collected {len(collected)} posts")
        return collected

    def open_likes_dialog(self):
        """Open the likes dialog"""
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/liked_by/')]")))
            button.click()
            time.sleep(2)
            return True
        except:
            return False

    def scroll_likes_and_check(self):
        """Scroll likes dialog and check for victim"""
        target = self.victim_username.lower()
        try:
            popup = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        except:
            return False
        
        seen = set()
        last_height = 0
        while True:
            users = self.driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")
            for u in users:
                try:
                    username = u.get_attribute("href").split("instagram.com/")[-1].strip("/")
                    if username not in seen:
                        seen.add(username)
                        if username.lower() == target:
                            return True
                except:
                    continue
            # Scroll
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 400;", popup)
            time.sleep(1.5)
            new_height = self.driver.execute_script("return arguments[0].scrollHeight;", popup)
            if new_height == last_height:
                break
            last_height = new_height
        return False

    def close_likes_dialog(self):
        """Close likes dialog"""
        try:
            close_btn = self.driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
            close_btn.click()
        except:
            self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        time.sleep(1)

    def check_post_likes(self, link, idx):
        """Check if victim liked a post"""
        self.driver.get(link)
        time.sleep(3)
        if not self.open_likes_dialog():
            logging.warning(f"⚠️ Could not open likes for post #{idx}")
            return
        liked = self.scroll_likes_and_check()
        if liked:
            self.like_count += 1
            logging.info(f"❤️ {self.victim_username} liked post #{idx}")
        else:
            logging.info(f"💔 {self.victim_username} did NOT like post #{idx}")
        self.close_likes_dialog()

    def run(self, max_posts=None):
        self.setup_driver()
        self.login()
        self.open_friend_profile()
        links = self.collect_post_links(max_posts)
        for idx, link in enumerate(links, 1):
            self.check_post_likes(link, idx)
        logging.info(f"🎯 RESULT: {self.victim_username} liked {self.like_count}/{len(links)} posts by {self.culprit_username}")

if __name__ == "__main__":
    tool = InstagramLikeChecker(
        culprit_username="culprit_username",
        victim_username="victim_username"
    )
    tool.run(max_posts=None)  # Set max_posts=20 to limit, or None for all
