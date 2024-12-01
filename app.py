from playwright.sync_api import sync_playwright
import time
import random
from flask import Flask, request, jsonify, render_template
import os
import csv
app = Flask(__name__)

class InstagramBot:
    def __init__(self, username, password, account_list):
        self.sp = None
        self.browser = None
        self.cursor = None
        self.username = username
        self.password = password
        self.account_list = account_list

    def input_csv(self, x, data):
        csv_file_path = f'{x}.csv'

        if not os.path.exists(csv_file_path):
            with open(csv_file_path, mode='w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(data)

        with open(csv_file_path, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(data)

    def login(self):
        try:
            self.cursor.wait_for_selector('//*[@id="loginForm"]/div/div[1]/div/label/input', timeout=50000)
            self.cursor.query_selector('//*[@id="loginForm"]/div/div[1]/div/label/input').fill(self.username)
            self.cursor.query_selector('//*[@id="loginForm"]/div/div[2]/div/label/input').fill(self.password)
            self.cursor.query_selector('//*[@id="loginForm"]/div/div[2]/div/label/input').press("Enter")

            try:
                # Wait for login error or check if login was successful
                self.cursor.wait_for_selector('//*[@id="loginForm"]/span/div', timeout=5000)
                print("Login failed.")
                return False
            except:
                try:
                    # Click "Not Now" if prompted to save login info
                    self.cursor.wait_for_selector('//div[@class="_a9-v"]', timeout=2000)
                    self.cursor.click('//div[@class="_a9-v"]/div[last()]/*[contains(text(), "Not Now")]')
                    self.cursor.wait_for_selector('//main[@class="x78zum5 xdt5ytf x1iyjqo2 x182iqb8 xvbhtw8"]')
                    print("Logged in successfully.")
                    return True
                except:
                    print("Logged in without saving credentials.")
                    return True
        except Exception as e:
            print(f"Login failed due to error: {e}")
            return False

    def search_account(self, account_to_search):
        time.sleep(random.randint(2, 4))
        try:
            self.cursor.wait_for_selector('//div[@class="x1iyjqo2 xh8yej3"]', timeout=10000)
            self.cursor.click('//div[@class="x1iyjqo2 xh8yej3"]/div[2]/span')
            self.cursor.wait_for_selector('//div[@class="x78zum5 xdt5ytf x5yr21d"]', timeout=10000)
            time.sleep(random.randint(2, 4))
            self.cursor.query_selector('//div[@class="x78zum5 xdt5ytf x5yr21d"]/div/div/div/input').fill("@" + account_to_search)
            self.cursor.query_selector('//div[@class="x78zum5 xdt5ytf x5yr21d"]/div/div/div/input').press("Enter")
            self.cursor.wait_for_selector('//div[@class="x6s0dn4 x78zum5 xdt5ytf x5yr21d x1odjw0f x1n2onr6 xh8yej3"]/div/a[1]', timeout=10000)
            self.cursor.click('//div[@class="x6s0dn4 x78zum5 xdt5ytf x5yr21d x1odjw0f x1n2onr6 xh8yej3"]/div/a[1]')
            print(f"Account '{account_to_search}' found successfully.")
            return True
        except Exception as e:
            print(f"Error searching for account {account_to_search}: {e}")
            return False

    def follower_status(self):
        try:
            self.cursor.wait_for_selector("//main/div/header", timeout=5000)
            self.cursor.wait_for_selector('//main/div/header/section/ul/li[2]//a', timeout=5000)
            self.cursor.click('//main/div/header/section/ul/li[2]//a', timeout=5000)
            print("Follower section is clickable.")
            return True
        except Exception as e:
            print(f"Error accessing follower section: {e}")
            return False

    def follower_scraping(self, x):
        time.sleep(3)
        count = 1
        count_status = True

        try:
            self.cursor.wait_for_selector(
                '//div[@class="xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6"]',
                timeout=10000)

            while count_status:
                last_node = self.cursor.query_selector(
                    '//div[@class="x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe"]/div/div/div[last()]/div/div/div[last()]/div/div/div/div[2]/div/div/div[1]').inner_text()

                try:
                    self.cursor.wait_for_selector(
                        f'//div[@class="x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe"]/div/div/div[last()]/div/div/div[{count}]',
                        timeout=10000)
                    current_node = self.cursor.query_selector(
                        f'//div[@class="x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe"]/div/div/div[last()]/div/div/div[{count}]/div/div/div/div[2]/div/div/div[1]').inner_text()

                    if current_node == last_node:
                        last_element = self.cursor.wait_for_selector(
                            '//div[@class="x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe"]/div/div/div[last()]/div/div/div[last()]')
                        self.cursor.evaluate('(element) => { element.scrollIntoView(); }', last_element)
                        self.input_csv(x, [current_node])
                    else:
                        self.input_csv(x, [current_node])
                    count = count + 1
                except Exception as e:
                    print(f"Error while scraping followers: {e}")
                    count_status = False

            if count_status:
                return False
            else:
                return True
        except Exception as e:
            print(f"Error in follower scraping: {e}")
            return False

    def start_bot(self):
        with sync_playwright() as self.sp:
            self.browser = self.sp.chromium.launch(headless=True)
            self.cursor = self.browser.new_page()
            self.cursor.goto("https://www.instagram.com/accounts/login/")
            login_status = self.login()

            if login_status:
                print("Logged In")
                account_to_search = self.account_list

                for x in account_to_search:
                    search_status = self.search_account(x)

                    if search_status:
                        print(f"Successfully searched for account: {x}")
                        follower_click_status = self.follower_status()

                        if follower_click_status:
                            print("Follower section accessible.")
                            scraping_status = self.follower_scraping(x)

                            if scraping_status:
                                print(f"Follower scraping completed for {x}.")
                            else:
                                print(f"Follower scraping incomplete for {x}.")
                                time.sleep(3)
                        else:
                            print(f"Follower section not accessible for {x}.")
                    else:
                        print(f"Failed to search for account: {x}")
            else:
                print("Login failed.")



from flask import Flask, request, jsonify, send_file



class FollowerBot:
    def __init__(self, username, password, account_list):
        self.sp = None
        self.browser = None
        self.cursor = None
        self.username = username
        self.password = password
        self.account_list = account_list
        print(account_list)

    def safe_wait_for_selector(self, selector, timeout=5000):
        """
        Wait for a selector to appear with error handling.
        Returns True if the selector is found, otherwise False.
        """
        try:
            self.cursor.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            print(f"Selector '{selector}' not found: {e}")
            return False

    def bot_login(self):
        if self.safe_wait_for_selector('//*[@id="loginForm"]/div/div[1]/div/label/input', timeout=5000):
            self.cursor.query_selector('//*[@id="loginForm"]/div/div[1]/div/label/input').fill(self.username)
            self.cursor.query_selector('//*[@id="loginForm"]/div/div[2]/div/label/input').fill(self.password)
            self.cursor.query_selector('//*[@id="loginForm"]/div/div[2]/div/label/input').press("Enter")
        else:
            print("Login form not found.")
            return False

        # Check if login succeeded
        if self.safe_wait_for_selector('//*[@id="loginForm"]/span/div', timeout=5000):
            return False
        return True

    def post_follow(self, name):
        time.sleep(random.randint(2, 4))
        self.cursor.goto(f'https://www.instagram.com/{name}')
        
        if not self.safe_wait_for_selector('//main/div/header', timeout=5000):
            print(f"Header not found for account: {name}")
            return False

        follow_button_selector = '//main/div/header/section/div[1]/div//*[contains(text(), "Follow") and not (contains(text(), "Following"))]'
        if self.safe_wait_for_selector(follow_button_selector, timeout=2000):
            self.cursor.click(follow_button_selector)
            return True
        else:
            print(f"Follow button not found for account: {name}")
            return False

    def bot_start(self):
        with sync_playwright() as self.sp:
            self.browser = self.sp.chromium.launch(headless=True)
            self.cursor = self.browser.new_page()
            self.cursor.goto("https://www.instagram.com/accounts/login/")
            login_status = self.bot_login()

            if login_status:
                print("Logged In")
                account_to_follow = self.account_list
                print(account_to_follow)

                for account in account_to_follow:
                    following_status = self.post_follow(account)
                    if following_status:
                        print(f"Account {account} followed successfully.")
                    else:
                        print(f"Account {account} already followed or an error occurred.")
            else:
                print("Login failed. Please check your credentials.")
            self.cursor.close()
            self.browser.close()


@app.route('/api/follow', methods=['POST'])
def follow_accounts():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    account_list = data.get('account_list')

    if not username or not password or not account_list:
        return jsonify({'success': False, 'message': 'username, password, and account_list are required.'}), 400

    bot = FollowerBot(username, password, account_list)
    bot.bot_start()

    return jsonify({'success': True, 'message': 'Process completed. Check logs for details.'})



@app.route('/api/fatch-followers', methods=['POST'])
def fetch_followers():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    account_list = data.get('account_list')

    if not username or not password or not account_list:
        return jsonify({"error": "username, password, and account_list are required."}), 400

    bot = InstagramBot(username, password, account_list=account_list)
    bot.start_bot()

    csv_file = f"{account_list[0]}.csv"

    if os.path.exists(csv_file):
        return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=csv_file  
        )
    else:
        return jsonify({"error": "CSV file not generated or found"}), 500

    

@app.route('/')
def InstaBOt():
    return render_template('main.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5000)