from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from typing import Any, Dict, List, Optional, Type, Union
import time
import csv
import argparse
import sys

options = Options()
options.headless = True

driver = webdriver.Firefox(options=options,executable_path = './geckodriver/geckodriver')
# driver = webdriver.Firefox(executable_path = '/Users/macpro/Downloads/geckodriver')
driver.implicitly_wait(0)
token_list_file_path = './token_list.csv'

class BSCCrawler:

  def __init__(self, from_page, to_page) -> None:
    MAX_PAGE_NUM = 10
    
    smart_contract_list = self.get_token_address_list(token_list_file_path)
    if smart_contract_list is not None:
      for addr in smart_contract_list.keys():
        self.get_holder_information(from_page, to_page, smart_contract_list[addr], addr)

  def get_holder_information(self, from_page: int, to_page: int, smart_contract_address_url: str, holder_list_file_path) -> None:
    
    # driver.get("https://etherscan.io/token/0xc4c7ea4fab34bd9fb9a5e1b1a98df76e26e6407c")
    driver.get(smart_contract_address_url)
    print('start to load holder list and insert to the file {} from page {} to page {}'.format(holder_list_file_path, from_page, to_page))
    element = WebDriverWait(driver,10).until(EC.presence_of_element_located(
      (By.XPATH, '//*[@id="ContentPlaceHolder1_tabHolders"]')))

    driver.execute_script("arguments[0].click();", element)

    holder_list_table_frame = WebDriverWait(driver,10).until(EC.presence_of_element_located(
      (By.XPATH, '//*[@id="tokeholdersiframe"]')))

    driver.switch_to.frame(holder_list_table_frame)
    # self.create_holder_list_header()
    index = 0
    for x in range(0, to_page):
      if index < from_page -1:
        print("start to load holder list page ", index)
        next_anchor = WebDriverWait(driver,10).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/div[2]/div[2]/nav/ul/li[4]/a')))
        driver.execute_script(next_anchor.get_attribute('href'))
        # ActionChains(driver).move_to_element(next_anchor).click().perform()
        time.sleep(3)
        index+=1
        continue

      time.sleep(3)
      self.crawl_holder_information(holder_list_file_path)
      next_anchor = WebDriverWait(driver,10).until(EC.presence_of_element_located(
      (By.XPATH, '/html/body/div[2]/div[2]/nav/ul/li[4]/a')))
      if next_anchor is not None:
        driver.execute_script(next_anchor.get_attribute('href'))
        index+=1

      # ActionChains didn't work in the headless mode
      # ActionChains(driver).move_to_element(next_anchor).click().perform()
    driver.switch_to_default_content

  # Collect holder address from the token
  def crawl_holder_information(self, holder_file_name: str) -> None:
      holder_list_table = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "maintable")))
      rows = holder_list_table.find_elements(By.TAG_NAME, "tr")
      with open(holder_file_name, 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            col_list = []
            for col in cols:
              anchor_tag = col.find_elements(By.TAG_NAME, "a")
              if len(anchor_tag) > 0:
                print(anchor_tag[0].get_attribute("href"))
                col_list.append(anchor_tag[0].get_attribute("href"))
              else:
                col_list.append(col.text)
            writer.writerow(col_list)
        f.close

  # Get token address list from file
  def get_token_address_list(self, file_path: str) -> any:
    token_address_dict = {}
    list_token = []
    with open('./token_list.csv', mode='r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      line_count = 0
      for row in csv_reader:
          token_file_name = self.create_symbol_csv(row["Symbol"])
          
          if line_count == 0:
              line_count += 1
          list_token.append(row["Smart Contract"])
          token_address_dict[token_file_name] = row["Smart Contract"]
          line_count += 1
    
    print('There are {} tokens in the list'.format(len(list_token)))
    return token_address_dict

  # Create file output csv file for each symbol
  def create_symbol_csv(self, symbol: str) -> str:
    if symbol is None:
      return None
    token_holder_filename = symbol + "_token_holder.csv"

    print('create file {}'.format(token_holder_filename))
    with open(token_holder_filename, mode='w', encoding='UTF8') as f:
      writer = csv.writer(f)
      holder_address_header = ['Rank', 'Address',
                               'Quantity', 'Percentage', 'Value', 'Analytics']
      writer.writerow(holder_address_header)
      f.close
    return token_holder_filename
  
# Craw token holder list
parser = argparse.ArgumentParser(description='Crawl token holder information')
parser.add_argument('-from','--from', help='From holder page index', required=True)
parser.add_argument('-to','--to', help='To holder page index', required=True)
args = vars(parser.parse_args())

from_page = args['from']
to_page = args['to']

BSCCrawler(int(from_page),int(to_page))
# BSCCrawler(5,10)

driver.close()
