Instagram Like Checker Bot

This project automates checking whether a specific Instagram user (“victim”) has liked posts by another Instagram user (“culprit”) using Python and Selenium.

Features

Automated Login: Logs into Instagram using credentials from a configuration file or environment variables.

Like Checking: Navigates through a target profile and checks which posts are liked by a specified user.

Post Scrolling: Automatically scrolls and collects all posts from the target account.

Configurable Settings: Easily switch target usernames and control the number of posts to check.

Requirements

To use this script, ensure you have the following installed:

Python 3.8 or later

Google Chrome browser

ChromeDriver (handled automatically by webdriver-manager)

Installation
1. Clone or Download the Repository
git clone https://github.com/your-username/instagram-like-checker.git
cd instagram-like-checker

2. Install Dependencies

Install all required Python packages:

pip install -r requirements.txt


Your requirements.txt should include:

selenium
webdriver-manager

3. Configuration

Create a config.json file in the project directory with your Instagram credentials:

{
  "username": "your_instagram_username",
  "password": "your_instagram_password"
}


Alternatively, you can set environment variables instead of using a config.json file:

export IG_USERNAME=your_instagram_username
export IG_PASSWORD=your_instagram_password

Usage

Run the script with:

python like_checker.py


You can change the usernames or limit the number of posts to check by editing:

tool = InstagramLikeChecker(
    culprit_username="target_account_username",
    victim_username="username_to_check"
)
tool.run(max_posts=None)  # Set a number instead of None to limit posts

How It Works

Launch Chrome: The script initializes a Chrome browser instance via Selenium.

Login: Logs in using credentials from config.json or environment variables.

Profile Scraping: Opens the culprit’s profile and collects all post URLs.

Like Checking: Opens each post, checks if the victim has liked it, and logs results.

Summary: Displays how many posts the victim liked out of the total scanned.

Warnings

Ethical Use: This script is for personal/educational use only. Automating Instagram actions may violate Instagram’s terms of service.

Liability: The author is not responsible for misuse or any resulting consequences.

Troubleshooting
Common Issues

Instagram Layout Changes: If Instagram updates its UI, some XPaths may need updating.

WebDriver Errors: Make sure your Google Chrome browser is up to date.

Login Failures: Double-check credentials or try using environment variables instead of config.json.

Contributing

Contributions are welcome! Feel free to fork this repo, open an issue, or submit a pull request with improvements.

Disclaimer

This project is not affiliated with or endorsed by Instagram. Use responsibly and respect Instagram’s terms and conditions.
