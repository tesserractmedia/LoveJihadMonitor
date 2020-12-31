from bs4 import BeautifulSoup
import requests
from datetime import datetime
import json
from newspaper import Article
import time
import re

source = {
    "OpIndia": "https://www.opindia.com/",
    "Times of India": "https://timesofindia.indiatimes.com/",
}


def scrap(cases, month=str(datetime.now().month), year=str(datetime.now().year)):
    with open("errorlog.txt", "a") as file:
        file.write("\nScrapError "+str(year) + "/" + str(month)+"\n")
        try:
            r = requests.get(source["OpIndia"]+year+"/"+month+"/")
        except:
            print("Error opening", source["OpIndia"]+year+"/"+month+"/")
            file.write("PageError "+source["OpIndia"]+year+"/"+month+"/\n")
            exit(-1)
        soup = BeautifulSoup(r.content, "html.parser")
        try:
            count = soup.find("span", attrs={"class": "pages"}).text.split()
        except:
            print("Error:Corrupted page!")
            file.write("PageError "+source["OpIndia"]+year+"/"+month+"/\n")
            exit(-1)
        count = int(count[-1])
        print("Total pages :", count)
        print("Total estimated time :", count/10, " minutes")
        for i in range(0, count):
            print("Processing page", i+1)
            try:
                r = requests.get(source["OpIndia"] +
                                 year+"/"+month+"/"+"page/"+str(i+1))
            except:
                print("Error opening ",
                      source["OpIndia"]+year+"/"+month+"/"+"page/"+str(i+1))
                file.write("PageError "+source["OpIndia"]+year+"/"+month+"/\n")
                continue
            try:
                soup = BeautifulSoup(r.content, "html.parser")
            except:
                print("Parsing error",
                      source["OpIndia"]+year+"/"+month+"/"+"page/"+str(i+1))
                file.write(
                    "ParseError "+source["OpIndia"]+year+"/"+month+"/"+"page/"+str(i+1)+"\n")
            articles = list(soup.find_all("div", attrs={"class": [
                            "tdb_module_loop", "td_module_wrap", "td-animation-stack"]}, partial=False))
            for article in articles:
                title = str(article.div.h3.a.text)
                if "Jihad" in title and ("Grooming" in title or "Love" in title):
                    a = {}
                    try:
                        a["title"] = title.encode('ascii',errors='ignore').decode("ascii",errors='ignore')
                        print(title)
                        a["link"] = article.div.h3.a["href"]
                        a["date"] = {}
                        d = re.search("[0-9]+-[0-9]+-[0-9]+",
                                      article.find("time")["datetime"]).group(0)
                        d = d.split('-')
                        a["date"]["day"] = int(d[2])
                        a["date"]["month"] = int(d[1])
                        a["date"]["year"] = int(d[0])
                    except AttributeError:
                        print("Error in", article)
                    finally:
                        cases.append(a)
            time.sleep(3)
        print("Finished!")


def process(year, month, cases):
    print("Total cases :", len(cases))
    with open("errorlog.txt", "a") as file:
        file.write("\nProcessError "+str(year) + "/" + str(month)+"\n")
        for i in range(0, len(cases)):
            try:
                a = Article(cases[i]["link"])
                a.download()
                a.parse()
                a.nlp()
                cases[i]["summary"] = a.summary.replace("\n", ' ').encode('ascii',errors='ignore').decode("ascii",errors='ignore')
                print(i+1, " cases processed")
                time.sleep(3)
            except:
                print("Processing error at", i+1)
                try:
                    file.write(cases[i]["title"]+"\n")
                except:
                    file.write("TitleError\n")
                try:
                    file.write(str(cases[i]["date"]["day"]) + "/" + str(
                        cases[i]["date"]["month"]) + "/" + str(cases[i]["date"]["year"])+"\n")
                except:
                    file.write("0/"+str(month)+"/"+str(year)+"\n")
                try:
                    file.write(cases[i]["link"]+"\n")
                except:
                    file.write("LinkError\n")
                try:
                    if "summary" in cases[i].keys():
                        pass
                    else:
                        file.write("SummaryError\n")
                except:
                    file.write("SummaryError\n")



def work(year=None, month=None):
    if year is None or month is None:
        year = int(input("Enter the year :"))
        month = int(input("Enter the month :"))
    print("Scraping",year,month)
    data = {}
    data["date"] = {}
    data["date"]["month"] = month
    data["date"]["year"] = year

    cases = []
    scrap(cases, str(month), str(year))
    process(month, year, cases)

    data["cases"] = cases
    if month < 10:
        filename = str(year)+"0"+str(month)+".json"
    else:
        filename = str(year)+str(month)+".json"
    with open(filename, "w") as file:
        json.dump(data, file)
    """
    yearmonth.json
    {
        date : 
        {
            month: m,
            year : y
        }
        cases :
        [
            {
                title :"sample title",
                link : "www.sample.com",
                date : 
                {
                    day : d,
                    month : m,
                    year : y
                },
                summary : " string "
            },
            {
                title :"sample title",
                link : "www.sample.com",
                date : 
                {
                    day : d,
                    month : m,
                    year : y
                },
                summary : " string "
            }
        ]
    }
    """
    record = None
    try:
        with open("record.json", "r") as file:
            record = json.load(file)
    except:
        record = {}
    try:
        record[str(year)][str(month)] = len(cases)
    except:
        record[str(year)] = {}
        record[str(year)][str(month)] = len(cases)
    with open("record.json", "w") as file:
        json.dump(record, file)
    """
    record.json 
    {
        year1 : 
        {
            month1 : case_count1,
            month2 : case_count2
        }
    }
    """


if __name__ == "__main__":
    work()
