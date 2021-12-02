# bsc-etherscan-crawler
It's the simplest tool in the world that helps you collect data of the holder from BSCscan or Etherscan.
# Follow the below steps to dig the gold.
## List all the smart contracts that you want to collect the top holders on the token_list.csv file. (Symbol and the smart contract address)
## Run python "python bsc_crawler.py --from <from page> --to <to page>" (the tool will collect top holder of the smart contracts to separate files)
## After you have the list of holders, then use file bsc_holder_info_crawler.py to collect data about the token from holders. It will list all tokens held by the holders with a total value in USDT. And based on that, you will see what tokens that held by most of the holders. (Noted: customize the value of MIN_TOTAL_VALUE, HOLDER_LIST_FILE, TOKEN_NAME for yourself  )