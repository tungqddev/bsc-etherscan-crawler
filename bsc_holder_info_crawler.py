from builtins import print
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from typing import Any, Dict, List, Optional, Type, Union
import csv
import re
import time

MIN_TOTAL_VALUE = 20000
HOLDER_LIST_FILE = './holder_list.csv'
TOKEN_NAME = 'REQ'

class BSCHolderInfoCrawler:

    def __init__(self) -> None:
        
        
        holder_address = self.get_holder_address_list('')
        skip_index = 1
        index = 1
        for address in holder_address:
            try:
                if index < skip_index:
                    index = index + 1
                    continue
                print("reading line ", index)
                print("getting information from ", address)
                self.get_list_token_of_holder(address)
                index = index + 1
                
            except Exception:
                print("can't load information of holder ", address)
                continue

        # self.get_list_token_of_holder(holder_address)

    def get_list_token_of_holder(self, holder_address) -> None:

        options = Options()
        options.headless = True
        holder_info_driver = webdriver.Firefox(options=options,
            executable_path='/Users/macpro/Downloads/geckodriver')
        holder_info_driver.implicitly_wait(10)
        holder_info_driver.get(holder_address)

        # click on holder address
        xpath_navigation_anchor = re.sub(r'.+\?.=', '', holder_address)
        holder_navigation_anchor = WebDriverWait(holder_info_driver, 10).until(EC.presence_of_all_elements_located((
            By.XPATH, '//*[@id="spanTarget_' + xpath_navigation_anchor + '"]')))
        if holder_navigation_anchor is None:
            return
        # go to the details of holder
        holder_info_driver.get(
            holder_navigation_anchor[0].get_attribute('href'))

        # anchor_tag = holder_navigation_anchor[0].find_elements(By.TAG_NAME, "a")
        token_list_dropdown = WebDriverWait(holder_info_driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="availableBalanceDropdown"]')))

        time.sleep(2)
        if token_list_dropdown is None:
            return
        ActionChains(holder_info_driver).move_to_element(
            token_list_dropdown[0]).click().perform()

        holder_list_token_ul = WebDriverWait(holder_info_driver, 10).until(EC.presence_of_all_elements_located(
            (By.XPATH, '/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div[1]/div/ul')))

        holder_list_token_li_list = holder_list_token_ul[0].find_elements(
            By.TAG_NAME, "li")
        # [0].find_elements(By.TAG_NAME, "span")
        with open('holder_tokens_info.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            for li in holder_list_token_li_list[1:]:
                total_span_tag = li.find_elements(By.TAG_NAME, "span")
                if len(total_span_tag) < 3:
                    continue
                token_span_1 = li.find_elements(By.TAG_NAME, "span")[1].text
                token_span_2 = li.find_elements(By.TAG_NAME, "span")[2].text
                token_span_1_split = token_span_1.split(" ")
                if len(token_span_1_split) > 1:
                    total_in_dolars = re.sub(',', '', token_span_2[1:])
                    if isfloat(total_in_dolars):
                        if token_span_1_split[1] == TOKEN_NAME:
                            continue
                        if float(total_in_dolars) > MIN_TOTAL_VALUE:
                            csv_row = []
                            csv_row.append(xpath_navigation_anchor)
                            csv_row.append(token_span_1_split[1])
                            csv_row.append(total_in_dolars)
                            writer.writerow(csv_row)
            f.close
        holder_info_driver.close()

    def get_holder_address_list(self, file_path: str) -> List[str]:
        list_address = []
        with open(HOLDER_LIST_FILE, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                list_address.append(row["Address"])
                line_count += 1
        print("There are [{}] holder in the file", len(list_address))
        return list_address


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

BSCHolderInfoCrawler()