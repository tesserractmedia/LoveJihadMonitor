from bs4 import BeautifulSoup
import requests
from datetime import datetime
import json
from newspaper import Article
import time
import re

source = {
    "OpIndia" : "https://www.opindia.com/",
    "Times of India" : "https://timesofindia.indiatimes.com/",
    }

def scrap(cases,month = str(datetime.now().month),year = str(datetime.now().year)):
    r = requests.get(source["OpIndia"]+year+"/"+month+"/")
    soup = BeautifulSoup(r.content,"html.parser")
    count = soup.find("span",attrs = {"class" : "pages"}).text.split()
    count = int(count[-1])
    print("Total pages :",count)
    print("Total estimated time :",count/20," minutes")
    for i in range(0,count):
        print("Processing page",i+1)
        r = requests.get(source["OpIndia"]+year+"/"+month+"/"+"page/"+str(i+1))
        soup = BeautifulSoup(r.content,"html.parser")
        articles = list(soup.find_all("div",attrs = {"class" : ["tdb_module_loop","td_module_wrap","td-animation-stack"]},partial=False))
        for article in articles:
            title = str(article.div.h3.a.text)
            if "Jihad" in title and "Grooming" in title or "Love" in title:
                a = {}
                try:
                    a["title"] = title
                    print(title)
                    a["link"] = article.div.h3.a["href"]
                    a["date"] =  {}
                    d = re.search("[0-9]+-[0-9]+-[0-9]+",article.find("time")["datetime"]).group(0)
                    d = d.split('-')
                    a["date"]["day"] = int(d[2])
                    a["date"]["month"] = int(d[1])
                    a["date"]["year"] = int(d[0])
                except AttributeError:
                    print("Error in",article)
                finally:
                    cases.append(a)
        time.sleep(3)
    print("Finished!")

def process(cases):
    print("Total cases :",len(cases))
    for i in range(0,len(cases)):
        try:
            a = Article(cases[i]["link"])
            a.download()
            a.parse()
            a.nlp()
            cases[i]["summary"] = a.summary.replace("\n",' ')
            print(i+1," cases processed")
            time.sleep(3)
        except:
            print("Processing error at",i)
            exit()

def work(year=None,month=None):
    if year is None or month is None:
        year = int(input("Enter the year :"))
        month = int(input("Enter the month :"))
    data = {}
    data["date"] = {}
    data["date"]["month"] = month
    data["date"]["year"] = year

    cases = []
    scrap(cases,str(month),str(year))
    process(cases)

    data["cases"] = cases
    if month < 10:
        filename = str(year)+"0"+str(month)+".json"
    else:
        filename = str(year)+str(month)+".json"
    with open(filename,"w") as file:
        json.dump(data,file)
    record = None 
    try:
        with open("record.json","r") as file: 
            record = json.load(file)
    except:
        record = {}
    try:
        record[str(year)][str(month)] = len(cases)
    except:
        record[str(year)]= {}
        record[str(year)][str(month)] = len(cases)
    with open("record.json","w") as file:
        json.dump(record,file)

if __name__ == "__main__":
    work()
    