# services/outline_generator.py
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)


def search_ddg(q,count=3):
    try:
        with DDGS() as d:
            r=d.text(q,max_results=count)
            if not r:return []
            links=[x.get("href") for x in r if x.get("href")]
            return links
    except Exception as e:
        print("search err:",e)
        return []

def extract_headings(u):
    try:
        r=requests.get(u,timeout=6,headers={"User-Agent":"Mozilla/5.0"})
        s=BeautifulSoup(r.text,"html.parser")
        heads=[]
        for h in s.find_all(["h1","h2","h3"]):
            t=h.get_text().strip()
            if len(t)>3:heads.append(t)
        seen=set();out=[]
        for x in heads:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out[:6]
    except Exception as e:
        print("extract err:",e)
        return []

def make_outline_from_heads(hs,joined):
    intro=None;main=[];con=None
    for h in hs:
        t=h.lower()
        if "intro" in t or "overview" in t:
            if not intro:intro=h
        elif "concl" in t or "summary" in t:
            if not con:con=h
        else:
            if len(main)<3:main.append(h)
    if not intro:intro=f"Introduction to {joined}"
    if not main:main=[f"Key ideas about {joined}"]
    if not con:con=f"Conclusion on {joined}"
    return {"intro":intro,"sections":main,"conclusion":con}

def generate_outline(keyword_group):
    outlines={}
    for c,words in keyword_group.items():
        joined=", ".join(words)
        print("processing:",joined)
        all_heads=[]
        tries=0
        while tries<5:
            links=search_ddg(joined,count=3)
            if not links:
                tries+=1
                time.sleep(1)
                continue
            for l in links:
                hs=extract_headings(l)
                all_heads+=hs
            o=make_outline_from_heads(all_heads,joined)

            if o["intro"] and len(o["sections"])>0 and o["conclusion"]:
                outlines[c]=o
                break
            tries+=1
            time.sleep(1)
        if c not in outlines:
            outlines[c]=make_outline_from_heads([],joined)
    return outlines

def make_post_idea(joined):
    prompt=f"Give one catchy blog post idea in one line about: {joined}"
    try:
        m=genai.GenerativeModel("gemini-2.5-flash")
        r=m.generate_content(prompt)
        if r and hasattr(r,"text") and r.text.strip()!="":
            return r.text.strip().strip('**')
        else:
            return f"Idea about {joined}"
    except Exception as e:
        print("idea err:",e)
        return f"Idea about {joined}"

def generate_outline_with_idea(keyword_group):
    outlines=generate_outline(keyword_group)
    for c,o in outlines.items():
        joined=", ".join(keyword_group[c])
        o["idea"]=make_post_idea(joined)
    return outlines