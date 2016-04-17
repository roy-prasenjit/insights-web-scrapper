from bs4 import BeautifulSoup
import re
import requests
import sys
"""
insights web scrapper

Main block
sys args block
email connection establishment using tokens(make it a diff module)

pull links as requested in sys args
Parse each link and make a pdfs


add attachments and send if file size less than 10 MB
"""

WEB_PAGE = "http://www.insightsonindia.com/"

def fetch_links(current_date,number_of_days=1,pdf=False):
	#hit page
	try:
		response = requests.get(WEB_PAGE)
		content = response.content

		# make soup; parse web pages
		soup = BeautifulSoup(content,'html.parser')

		# fetch urls
		result_set = soup.find_all(class_='pf-content')
		div=result_set[0]
		# div = soup.findAll('div', { "class" : "pf-content" })

		daily_events = "insights-daily-current-events-[0-9]+-{}-{}".format(current_date.strftime("%B").lower(),current_date.year)
		editorials = "insights-into-editorial-"

		list_latest_current_events = div.find_all(href=re.compile(daily_events),limit=number_of_days)
		list_latest_insights = div.find_all(href=re.compile(editorials),limit=number_of_days)

		return (list_latest_current_events,list_latest_insights)
	except:
		print("Unable to fetch links")
		return(None,None)


def fetch(link):
    response = requests.get(link)
    if response.status_code != 200: return False
    content = response.content
    s = BeautifulSoup(content,'html.parser')
    title = s.title
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
    return [title,data]

def fetch_data(list1,list2):
	data = []
	for link in list1:
		t = fetch(link['href'])
		if t is not False: data.append(t)
	for link in list2:
		t = fetch(link['href'])
		if t is not False: data.append(t)
	return data

def prepare_data(data,date):
	with open('Insights.txt','w') as f:
		try:
			for title, info in data:
				#f.write(title.get_text() + "\n") # redundant. skip it
				for line in info.get_text():
					try:
						f.write(line)
					except Exception:
						pass # log error
		except Exception, e:
			pass # log error

def main():
	from datetime import datetime
	current_date = datetime.now()
	args = sys.argv
	l1 = None # current events
	l2 = None # insights
	if len(args) > 1:
		days_passed = current_date.day
		days_requested = int(args[1])
		if days_requested > days_passed: print("Please contact author for articles published in the previous month(s)")
		else: l1,l2 = fetch_links(current_date,number_of_days=days_requested)
	else: 
		l1,l2 = fetch_links()
	if l1 is not None and l2 is not None:
		data = fetch_data(l1,l2)
		prepare_data(data,current_date)
		generate_and_send_mail()
		return 0
	else:
		print("Unable to send mail")
		return 1


if __name__=='__main__':
	sys.exit(main())
