
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
import datetime
import os
import dmu_helper_functions as dmu
import shutil


print('hi_1')

# Global variables:
cwd = os.getcwd()
now = datetime.datetime.now()
dtime_string = now.strftime("%Y-%m-%d-%H-%M-%S")

# Load ticker set 1 from yahoo:
print('ticker_set_1')
ticker_set_01 = ['SPY', 'ACWX', 'VWO', \
                 'EDV', 'TLT', 'TLH', 'IEI', 'SHY', 'LTPZ', 'TIP', 'STPZ', \
                 'EWA', 'EWC', 'EWG', 'EWJ', 'EWU', 'RSX', 'MCHI']
yahoo_01 = dmu.YahooObject(ticker_set_01, 'etf_set01')
html_dir_1 = yahoo_01.html_dir_all_freq

# Save only the 1st DFs as a local CSV:
csv_dir = cwd + str('\\CSVs\\df_yahoo1') + dtime_string + str('.csv')
yahoo_01.df_daily_adj_prices.to_csv(csv_dir)

# Load ticker set 2 from yahoo:
print('ticker_set_2')
ticker_set_02 = ['XLB','XLC','XLE','XLF','XLI',\
                 'XLK','XLP','XLRE','XLU','XLV','XLY','EQL',\
                 'QQQ','VNQ','VHT','XBI','IBB']
yahoo_02 = dmu.YahooObject(ticker_set_02, 'etf_set02')
html_dir_2 = yahoo_02.html_dir_all_freq

# Load ticker set 3 from yahoo:
print('ticker_set_3')
ticker_set_03 = ['GLD','DBC','GCC','SLV','USO']
yahoo_03 = dmu.YahooObject(ticker_set_03, 'etf_set03')
html_dir_3 = yahoo_03.html_dir_all_freq

# Load ticker set 4 from yahoo:
print('ticker_set_4')
ticker_set_04 = ['FXA','FXB','FXC','FXE','FXF','FXS','FXY','UUP','UDN','CYB','CNY','DBV']
yahoo_04 = dmu.YahooObject(ticker_set_04, 'etf_set04')
html_dir_4 = yahoo_04.html_dir_all_freq

# Load ticker set 5 from yahoo:
print('ticker_set_5')
ticker_set_05 = ['TSLA', 'KODK', 'AAPL', 'MSFT', 'GS', \
                'BRK-B', 'XOM', 'JPM', 'JNJ', 'KR', 'AMZN', 'GOOG', 'LULU', 'FB', 'NFLX']
yahoo_05 = dmu.YahooObject(ticker_set_05, 'STOCK_set01')
html_dir_5 = yahoo_05.html_dir_all_freq

# Load ticker set 6 from yahoo:
print('ticker_set_6')
ticker_set_06 = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD', 'ADA-USD']
yahoo_06 = dmu.YahooObject(ticker_set_06, 'CRYPTO_set01')
html_dir_6 = yahoo_06.html_dir_all_freq

# Concatenate HTMLs into single HTML:
html_concat1 = cwd + str('\\HTMLs\\html_concat1_') + dtime_string + str('.html')
dmu.concat_html(html_dir_1, html_dir_2, html_concat1)
html_concat2 = cwd + str('\\HTMLs\\html_concat2_') + dtime_string + str('.html')
dmu.concat_html(html_concat1, html_dir_3, html_concat2)
html_concat3 = cwd + str('\\HTMLs\\html_concat3_') + dtime_string + str('.html')
dmu.concat_html(html_concat2, html_dir_4, html_concat3)
html_concat4 = cwd + str('\\HTMLs\\html_concat4_') + dtime_string + str('.html')
dmu.concat_html(html_concat3, html_dir_5, html_concat4)
html_concat5 = cwd + str('\\HTMLs\\html_concat5_') + dtime_string + str('.html')
dmu.concat_html(html_concat4, html_dir_6, html_concat5)

# The email function requires a DIRECTORY, not a single HTML file, so let's
# put our newly concatenated HTML into a date-stamped subdirectory:
html_dir_to_send = cwd + str('\\HTMLs\\_TO_SEND_\\') + dtime_string
os.mkdir(html_dir_to_send)

# Now put the HTML into the subdirectory we just created:
shutil.copyfile(html_concat5, \
     html_dir_to_send + str('\\') + str('Report_' + dtime_string + '.html') )

print('hi_3')

# Load email credentials from separate directory:
cred_dir = cwd + str('\\Credentials\\gmail_credentials.csv')
csv_credentials = pd.read_csv(cred_dir, header=None)
gmail_username = csv_credentials.iloc[0, 0]
gmail_pw = csv_credentials.iloc[1, 0]

# Load email recipients from separate directory:
recipient_dir = cwd + str('\\Recipient_List\\email_addresses_to_spam.csv')
csv_recipients = pd.read_csv(recipient_dir, header=None)
recipient_address_list = csv_recipients.iloc[:, 0]  # fill this in from txt/csv to be loaded

# Send HTML as email:
subj_string = str('Daily Market Update: [') + str(dtime_string) + str(']')
msg_text_01 = str('Daily Market Update:')
dmu.send_html_via_gmail(username=gmail_username, password=gmail_pw,\
                toaddrs_list=recipient_address_list,\
                msg_text=msg_text_01, fromaddr='Bob R. Tumbloni', \
                subject=subj_string,
                attachment_path_list=html_dir_to_send)

print('hi_4')