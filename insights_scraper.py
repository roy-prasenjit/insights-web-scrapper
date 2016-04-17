from bs4 import BeautifulSoup
import requests
import re

WEB_PAGE = "http://www.insightsonindia.com/"

# hit page
response = requests.get(WEB_PAGE)
content = response.content

# make soup; parse web pages
soup = BeautifulSoup(content,'html.parser')

# fetch urls
body = soup.body
list_latest_current_events = body.find_all(href=re.compile("insights-daily-current-events-"),limit=5)
list_latest_insights = body.find_all(href=re.compile("insights-into-editorial-"),limit=5)

def fetch(link):
    response = requests.get(link)
    if response.status_code != 200: return False
    content = response.content
    s = BeautifulSoup(content,'html.parser')
    body = s.body
    #locate article
    data = body.find("article").find('div', class_="pf-content")
    # remove unnecesary divs
    data.find('div', class_="printfriendly").decompose()
    #remove scripts
    for d in data.find_all("script"):
        d.decompose()
    # remove google's insert tag
    data.find('ins').decompose()
    return data

def send_email(user, pwd, recipients, subject, body):
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body,'html')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] =  ", ".join(recipients)

    FROM = user
    TO = recipients if type(recipients) is list else [recipients]
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user,pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")

		

msg_body = fetch(list_latest_current_events[0]['href'])

receivers = ['xyz@gmail.com']
message = msg_body.prettify()
username = ''
password = ''
send_email(username,password,receivers,"Insights test mail",message)
