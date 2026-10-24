#!/usr/bin/env python3
"""Fetch 臺灣銀行牌告匯率 (rate.bot.com.tw) and write fx.json with 即期賣出 rates.
即期賣出 = rate the bank sells foreign currency for TWD account transfer, i.e. what a client pays
to buy USD/AUD/CNY to fund a foreign-currency premium. rate.bot.com.tw has a JS proof-of-work
challenge, so a headless browser is used. On any failure, fx.json is left unchanged (exit 1)."""
import json,re,sys,datetime
from playwright.sync_api import sync_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else 'fx.json'
CUR=['USD','AUD','CNY','EUR','JPY','HKD','GBP','NZD','ZAR','CAD','SGD','CHF']
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',locale='zh-TW')
    pg=c.new_page();pg.goto('https://rate.bot.com.tw/xrt?Lang=zh-TW',timeout=90000)
    for _ in range(30):
        if '牌告' in pg.title(): break
        pg.wait_for_timeout(3000)
    txt=pg.inner_text('body')
    csv=c.request.get('https://rate.bot.com.tw/xrt/flcsv/0/day').body().decode('utf-8-sig')
    b.close()
rates={}
for line in csv.splitlines():
    f=line.split(',')
    if len(f)>13 and f[0] in CUR and f[11]=='本行賣出':
        v=float(f[13])
        if v>0: rates[f[0]]=round(v,4 if v<1 else 3 if v<10 else 2)
m=re.search(r'(\d{4})/(\d{2})/(\d{2})\s+(\d{2}:\d{2})',txt)
if 'USD' not in rates or not 20<rates['USD']<50: print('fetch failed',csv[:200]); sys.exit(1)
d=f'{m[1]}-{m[2]}-{m[3]}' if m else datetime.datetime.utcnow().strftime('%Y-%m-%d')
J={'date':d,'time':m[4] if m else '','source':'臺灣銀行牌告匯率 即期賣出','url':'https://rate.bot.com.tw/xrt?Lang=zh-TW','rates':rates}
open(OUT,'w').write(json.dumps(J,ensure_ascii=False,indent=1)); print(J)
