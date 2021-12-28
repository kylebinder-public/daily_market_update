import smtplib  # for sending automatic email
from email.mime.text import MIMEText  # for sending automatic email
from email.mime.multipart import MIMEMultipart  # for sending automatic email
from email.mime.application import MIMEApplication  # for sending automatic email
import pandas_datareader as pdr
import os
import datetime

# Global variables:
cwd = os.getcwd()
now = datetime.datetime.now()
dtime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
today_str = datetime.datetime.today().strftime('%Y-%m-%d')
start_date_str = '2006-12-29'


class YahooObject:
    """A simple object for keeping track of data DL-ed from Yahoo"""
    # above docstring can be called via "__doc__"
    #
    # Has these properties, possibly NULL:
    # (1) Most recent data point (String)
    # (2) Dataframe for daily (recent 14 calendar days), monthly, quarterly, yearly
    # (3) HTML for all in (2)
    #
    # Any methods?
    # (1) Populate all of (1),(2),(3) above.
    # (2) retrieve data - will be specific for particular
    #     class - CPI we'll get from FRED; ETFs we'll get from
    #     Yahoo, VIX term structure we'll get from elsewhere.
    #
    #####################################

    def __init__(self, ticker_list, name_str):

        self.tickers = ticker_list
        raw_daily_adj_prices = pdr.get_data_yahoo(self.tickers, start=start_date_str, end=today_str)
        self.most_recent_data_point = raw_daily_adj_prices.index[-1]

        # Convert index of dataframe from timestamp to "YYYY-MM-DD"
        self.df_daily_adj_prices = raw_daily_adj_prices.iloc[:, 0:len(ticker_list)]
        self.df_daily_return = self.df_daily_adj_prices.pct_change(1)  # 1 for ONE DAY lookback

        # Put dataframes into HTML files:
        self.html_dir_daily = cwd + str('\\HTMLs\\html_dailies_') + \
                              str(name_str) + str('_') + dtime_string + str('.html')

        # The syntax "[::-1]" reverses the order
        df_previous_six_days = self.df_daily_return.iloc[-7:,:]
        df_daily_transpose = df_previous_six_days[::-1].transpose()
        df_daily_transpose.to_html(self.html_dir_daily)

        # (1A) Convert to yearly returns:
        yearlies = self.df_daily_return.groupby(self.df_daily_return.index.year).apply(total_return_from_returns)
        yearlies.columns = self.tickers
        self.df_yearly_return = yearlies

        # (1B) Create HTML for yearly returns:
        self.html_dir_yearly = cwd + str('\\HTMLs\\html_yearlies_') + \
                               str(name_str) + str('_') + dtime_string + str('.html')
        df_yearly_transpose = yearlies[::-1].transpose()
        df_yearly_transpose.to_html(self.html_dir_yearly)

        # (2A) Convert to MONTHLY returns:
        monthlies = self.df_daily_return.groupby([self.df_daily_return.index.year,
                                                  self.df_daily_return.index.month]).apply(total_return_from_returns)
        monthlies.columns = self.tickers
        self.df_monthly_return = monthlies

        # (2B) Create HTML for monthly returns:
        self.html_dir_monthly = cwd + str('\\HTMLs\\html_monthlies_') + \
                               str(name_str) + str('_') + dtime_string + str('.html')
        df_previous_fourteen_months = self.df_monthly_return.iloc[-14:, :]
        df_monthly_transpose = df_previous_fourteen_months[::-1].transpose()
        df_monthly_transpose.to_html(self.html_dir_monthly)

        # (3A) Convert to QUARTERLY returns:
        quarterlies = self.df_daily_return.groupby([self.df_daily_return.index.year,
                                                  self.df_daily_return.index.quarter]).apply(total_return_from_returns)
        quarterlies.columns = self.tickers
        self.df_quarterly_return = quarterlies

        # (3B) Create HTML for quarterly returns:
        self.html_dir_quarterly = cwd + str('\\HTMLs\\html_quarterlies_') + \
                               str(name_str) + str('_') + dtime_string + str('.html')
        df_previous_fourteen_quarters = self.df_quarterly_return.iloc[-14:, :]
        df_quarterly_transpose = df_previous_fourteen_quarters[::-1].transpose()
        df_quarterly_transpose.to_html(self.html_dir_quarterly)

        # Concatenate daily HTML to yearly HTML:
        html_dir_dy = cwd + str('\\HTMLs\\html_D+Y_') + str(name_str) + str('_') + dtime_string + str('.html')
        concat_html(self.html_dir_daily, self.html_dir_yearly, html_dir_dy)

        # Add monthly to the previous HTML concatenation:
        html_dir_dym = cwd + str('\\HTMLs\\html_D+Y+M_') + str(name_str) + str('_') + dtime_string + str('.html')
        concat_html(html_dir_dy, self.html_dir_monthly, html_dir_dym)

        # Add quarterly to the previous HTML concatenation:
        html_dir_dymq = cwd + str('\\HTMLs\\html_D+Y+M+Q_') + str(name_str) + str('_') + dtime_string + str('.html')
        concat_html(html_dir_dym, self.html_dir_quarterly, html_dir_dymq)

        # Finally, whenever any class instance is created, save a full CSV of all returns (really?)
        # # (how to clean/purge older copies?) :
        self.html_dir_all_freq = html_dir_dymq


def send_html_via_gmail(username, password, toaddrs_list,
                        msg_text, fromaddr=None, subject="Test mail",
                        attachment_path_list=None):
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login(username, password)
    msg = MIMEMultipart()
    sender = fromaddr
    recipients = toaddrs_list
    msg['Subject'] = subject
    if fromaddr is not None:
        msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    if attachment_path_list is not None:
        os.chdir(attachment_path_list)
        files = os.listdir()
        for f in files:  # add files to the message
            try:
                file_path = os.path.join(attachment_path_list, f)
                attachment = MIMEApplication(open(file_path, "rb").read(), _subtype="txt")
                attachment.add_header('Content-Disposition', 'attachment', filename=f)
                msg.attach(attachment)
            except:
                print("could not attach file")
    msg.attach(MIMEText(msg_text, 'html'))
    s.sendmail(sender, recipients, msg.as_string())


def total_return_from_returns(returns):
    """Retuns the return between the first and last value of the DataFrame.
    Parameters
    ----------
    returns : pandas.Series or pandas.DataFrame
    Returns
    -------
    total_return : float or pandas.Series
        Depending on the input passed returns a float or a pandas.Series.
    """
    return (returns + 1).prod() - 1


def concat_html(html1_path, html2_path, html_concat_path):
    # CONCAT two HTML files:
    file_object1 = open(html1_path, "r")
    data1 = file_object1.read()
    file_object2 = open(html2_path, "r")
    data2 = file_object2.read()
    data3 = data1 + '\n' + '\n' + data2
    with open(html_concat_path, "w+") as file:
        file.write(data3)
