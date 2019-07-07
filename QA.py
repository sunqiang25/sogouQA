#!/usr/bin/env python3
# coding: utf-8

import urllib.request,requests
from urllib.parse import quote_plus
from lxml import etree
import json,time,re

class SogouQA:
    
    def __init__(self):
        return

    def get_html(self, url):
        if not url.startswith("http"):
            url = "https://www.sogou.com"+url
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17"}
        try:
            req = urllib.request.Request(url, headers=headers)
            html = urllib.request.urlopen(req).read().decode('utf-8')
            #response = requests.get(url, timeout=1, verify=False, headers=headers,allow_redirects=True)
            #response.encoding = "utf-8"
            #html = response.text
            regex= 'window\.location\.replace\(\"(.*?)\"\)'
            l = re.findall(regex,html)
            if l:
                url = l[0]
                req = urllib.request.Request(url, headers=headers)
                html = urllib.request.urlopen(req).read().decode('utf-8')                
                #response = requests.get(url, timeout=1, verify=False, headers=headers,allow_redirects=True)
                #response.encoding = "utf-8"
                #html = response.text                
        except Exception as e:
            print(e)
            html=None
        return html


    def collect_urls(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        top_pairs = []
        pairs = []
        final_answer = ""
        try:
            shizhi = selector.xpath('//div[@class="vrwrap"]/div[@class="vr-share180309 vrwrap-border"]')
            if shizhi:
                #question = selector.xpath('//div[@class="vrwrap"]/div[@class="vr-share180309 vrwrap-border"]/div[@class="vrTitle wd-result"]')[0].xpath('string(.)').strip()
                shizhi_value = selector.xpath('//div[@class="vrwrap"]/div[@class="vr-share180309 vrwrap-border"]/div[@class="share-main border-top"]/a/i/@js_value')[0].strip()
                answer = selector.xpath('//div[@class="vrwrap"]/div[@class="vr-share180309 vrwrap-border"]/div[@class="share-main border-top"]/a/text()')
                if len(answer)==2:
                    final_answer = answer[0]+shizhi_value+answer[1]
                return final_answer,pairs
            sougou_lizhi = selector.xpath('//div[@class="vrwrap"]/div[@class="jzwdFrom"]/text()')
            if "搜狗立知" in sougou_lizhi:
                #shici = selector.xpath('//div[@class="vrwrap"]/div[@class="jzwd-shici"]')
                #if shici:
                    #question = selector.xpath('//div[@class="vrwrap"]/h3[@class="vrTitle light-title"]')[0].xpath('string(.)').strip()
                    #answer = 
                questions = selector.xpath('//div[@class="vrwrap"]/div/div/div[@class="identity"]')
                if questions:question=questions[0].xpath('string(.)').strip()
                answers = selector.xpath('//div[@class="vrwrap"]/div/div[@class="proInfoBox"]/h4')
                if answers:answer=answers[0].xpath('string(.)')
                final_answer = question+"是:"+answer
                return final_answer.strip(),pairs
            sogou_wenwen = selector.xpath('//div[@class="vrwrap"]/div/a[@class="from"]/text()')
            if "搜狗问问" in sogou_wenwen:
                answer = selector.xpath('//div[@class="vrwrap"]/div/div/div[@class="text-layout"]/p')[0].xpath('string(.)').replace("查看全部>>","")
                return answer,pairs
            else:
                j
        except Exception as e:
            try:
                link = selector.xpath('//div[@class="vrwrap"]/div[@class="img-txt-box"]/a/@href')[0]
                #link = links[0] if links else ""
                question = selector.xpath('//div[@class="vrwrap"]/div/div/div[@class="identity"]')[0].xpath('string(.)').strip()
                #question = questions[0].xpath('string(.)').strip() if questions else ""
                if link and question:
                    html = self.get_html(link)
                    selector = etree.HTML(html)                
                    #top_pairs = list(zip([question],[link]))
            except Exception as e:
                print(e)
                pass
            finally:
                top_answer = selector.xpath('//div[@class="vrwrap"]/div/div/a/@href')
                if top_answer:
                    top_question = selector.xpath('//div[@class="vrwrap"]/div/div/a')[0].xpath('string(.)').strip().replace("\n","-")
                    if top_question:top_pairs = list(zip([top_question],[top_answer[0]]))
                questions = [i.xpath('string(.)').replace('搜狗问问','').replace('搜狗', '').replace('-','') for i in selector.xpath('//div[@class="vrwrap"]/h3[@class="vrTitle"]/a')]
                #links = ['https://wenwen.sogou.com/z/' + i.split('.htm&')[0].split('2F')[-1] + '.htm' for i in selector.xpath('//div[@class="vrwrap"]/h3[@class="vrTitle"]/a/@href')]
                #links = ['https://www.sogou.com'+i if not i.startswith("http") else i for i in selector.xpath('//div[@class="vrwrap"]/h3[@class="vrTitle"]/a/@href')]
                links = [i for i in selector.xpath('//div[@class="vrwrap"]/h3[@class="vrTitle"]/a/@href')]
                pairs = list(zip(questions, links))
                if top_pairs:
                    pairs.insert(0,top_pairs[0])
        return final_answer,pairs[:3]

    def parser_answer(self, url):
        html = self.get_html(url)
        answers = []
        if html:
            selector = etree.HTML(html)
            if not url.startswith("http"):
                answer=selector.xpath('//div[@class="abstract_wrap"]/div[@class="abstract_main"]/div[@class="abstract"]')
                if answer:
                    answers = [answer[0].xpath('string(.)').strip()]
            else:
                answers = [i.xpath('string(.)').replace('\u3000','').replace('\n', '').replace('\xa0', '').replace(' ', '。').replace('\r', '') for i in selector.xpath('//pre')]
                answers = [i for i in answers if '?' not in i and '？' not in i and len(set(i)) > 2 and '为什么' not in i]
                answer_dict = {answer:len(answer) for answer in answers}
                answers = [i[0] for i in sorted(answer_dict.items(), key=lambda asd:asd[1])]
        else:
            answers=[]
        return answers

    def collect_answers(self, url):
        answers_all = []
        final_answer,url_pairs = self.collect_urls(url)
        if final_answer:
            answers_all.append(final_answer)
        else:
            for question, answer_url in url_pairs:
                answers = self.parser_answer(answer_url)
                #pattern=re.match(r'[a-zA-z]+://[^\s]*',answer_url,re.IGNORECASE)
                if answers and not answer_url.startswith("http") and answer_url.startswith("/"):
                    answers_all += answers
                    break
                if answers:
                    answers_all += answers
            answer_dict = {answer:len(answer) for answer in answers_all}
        if len(answers_all)==1:
            best_answers = answers_all[0].strip()
        else:
            best_answers = [i[0] for i in sorted(answer_dict.items(), key=lambda asd:asd[1])][:5]
        return best_answers

    def expand_question(self, question):
        url = 'https://wenwenfeedapi.sogou.com/sgapi/web/related_search_new?key=' + quote_plus(question)
        data = json.loads(self.get_html(url))
        others = data["data"]
        return others

    def qa_main(self, question):
        #url = 'https://www.sogou.com/sogou?query='+quote_plus(question) +'&ie=utf8&s_from=result_up&insite=wenwen.sogou.com'
        now_timstamp = int(time.time())
        url = 'https://www.sogou.com/sogou?query='+quote_plus(question) +'&ie=utf8&_ast=%d&_asf=null&w=01029901&cid=&s_from=result_up'%(now_timstamp)
        answers = self.collect_answers(url)
        other_questions = self.expand_question(question)
        return answers, other_questions

def main():
    handler = SogouQA()
    while 1:
        question = input('你的问题:').strip()
        answers, other_questions = handler.qa_main(question)
        if not answers:
            answers = "小强还在努力学习哦"
        print('回答:', answers)
        print('你可能还想问:', other_questions)
        print('##########'*8)

if __name__ == '__main__':
    main()



