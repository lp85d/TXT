import base64 as O00OO0,logging as O0OO0O,pandas as O00O0O
from selenium import webdriver as O00OOO
from selenium.webdriver.chrome.service import Service as O0O0OO
from webdriver_manager.chrome import ChromeDriverManager as O0O00O
from selenium.webdriver.chrome.options import Options as O0O0O0
from selenium.webdriver.common.by import By as O0OO00
from selenium.webdriver.support.ui import WebDriverWait as O0OOO0
from selenium.webdriver.support import expected_conditions as O0OOOO
from selenium.common.exceptions import TimeoutException as OO0000
import time as OOO000,re as OO0O00
from urllib.parse import urlparse as OO0OO0,urljoin as OO00O0
import concurrent.futures as OOO0O0,threading as OOOO00
from selenium_stealth import stealth as OOOOO0
OOO00O=2
O000O0=base64.b64decode('dXJscy5jc3Y=').decode('utf-8')
O00O00=base64.b64decode('c2l0ZXMudHh0').decode('utf-8')
O00OO0=base64.b64decode('cGhvbmVzLnR4dA==').decode('utf-8')
O00O_0=base64.b64decode('ZW1haWxzLnR4dA==').decode('utf-8')
O0OO0O.basicConfig(level=O0OO0O.INFO,format='%(asctime)s | %(threadName)s | %(levelname)s | %(message)s')
_O0O0O0=sorted
_O0O0OO=False
_O0O0O_=['languages','vendor','platform','webgl_vendor','renderer','fix_hairline']
_O0O00O={'ru-RU','ru'},'Google Inc.','Win32','Intel Inc.','Intel Iris OpenGL Engine',True
def O00000():
	OO00OO=O0O0O0();OO00OO.add_argument(base64.b64decode('LS1oZWFkbGVzcw==').decode('utf-8'));OO00OO.add_argument(base64.b64decode('LS1uby1zYW5kYm94').decode('utf-8'));OO00OO.add_argument(base64.b64decode('LS1kaXNhYmxlLWdwdQ==').decode('utf-8'));OO00OO.add_argument(base64.b64decode('LS1kaXNhYmxlLWRldi1zaG0tdXNhZ2U=').decode('utf-8'));OO00OO.add_argument(base64.b64decode('LS13aW5kb3ctc2l6ZT0xOTIwLDEwODA=').decode('utf-8'));OO00OO.add_argument(base64.b64decode('LS1kaXNhYmxlLWJsaW5rLWZlYXR1cmVzPUF1dG9tYXRpb25Db250cm9sbGVk').decode('utf-8'));OO00OO.add_experimental_option(base64.b64decode('ZXhjbHVkZVN3aXRjaGVz').decode('utf-8'),[base64.b64decode('ZW5hYmxlLWF1dG9tYXRpb24=').decode('utf-8')]);OO00OO.add_experimental_option(base64.b64decode('dXNlQXV0b21hdGlvbkV4dGVuc2lvbg==').decode('utf-8'),_O0O0OO)
	try:O000_0=O0O0OO(O0O00O().install());O0000O=O00OOO.Chrome(service=O000_0,options=OO00OO);OOOOO0(O0000O,**dict(zip(_O0O0O_,_O0O00O)))
	except Exception as O000O_O:O0OO0O.critical(f"Не удалось инициализировать WebDriver: {O000O_O}.");raise
	O0000O.set_page_load_timeout(40);return O0000O
def O00001(phone_str):
	O00_00=base64.b64decode('Nw==').decode('utf-8');O0__00=base64.b64decode('OA==').decode('utf-8');O__000=OO0O00.sub('[^\\d]','',phone_str)
	if len(O__000)==10 and(O__000.startswith('9')or O__000.startswith(O0__00)):O__000=O00_00+O__000
	elif len(O__000)==11 and O__000.startswith(O0__00):O__000=O00_00+O__000[1:]
	elif len(O__000)==12 and O__000.startswith('+7'):O__000=O__000[1:]
	if not(len(O__000)==11 and O__000.startswith(O00_00)):return
	O___00=O__000[1:4]
	if not(O___00.startswith('9')or O___00=='800'):return
	if len(set(O__000[1:]))<3:return
	return O0__00+O__000[1:]
def O00010(email):
	_00000=email
	if'.'in _00000:
		_00001=_00000.split('@')[-1]
		if _00001.split('.')[-1].lower()in['png','jpg','jpeg','gif','svg','webp']:return _O0O0OO
	if OO0O00.fullmatch(base64.b64decode('KFthLXpBLVowLTlfLisuXSsAW2EtekEtWjAtOS1dK1wuW2EtekEtWl17Mix9KQ==').decode('utf-8'),_00000):return True
	return _O0O0OO
def O00011(html):
	_00010,O00100=set(),set();_00011=OO0O00.compile(base64.b64decode('W1wrXGRcc1wtXChcKV17MTAsMTh9').decode('utf-8'));O00101=OO0O00.compile(base64.b64decode('W1x3XC4tXSs@W1x3XC4tXSs=').decode('utf-8'))
	for O00110 in _00011.findall(html):
		_0001_ =O00001(O00110)
		if _0001_:_00010.add(_0001_)
	for O00111 in O00101.findall(html):
		if O00010(O00111.lower()):O00100.add(O00111.lower())
	return _00010,O00100
def O00100(driver,start_url,max_pages=5):
	_00100=start_url;O01000=driver;O01001,O0100_=[],_00100;O01010,O01011=set(),set()
	try:_00101=OO0OO0(_00100).netloc
	except Exception:return O01010,O01011
	_00110=0;_00111=['contact','kontakt','about','info']
	while O0100_ and _00110<max_pages:
		_001_0=O0100_.pop(0)
		if _001_0 in O01001 or not OO0OO0(_001_0).netloc.endswith(_00101):continue
		O01001.append(_001_0)
		try:
			O01000.get(_001_0);OOO000.sleep(1);_00_00,_00_01=O00011(O01000.page_source);O01010.update(_00_00);O01011.update(_00_01);_00110+=1
			for _0_0_0 in O01000.find_elements(O0OO00.TAG_NAME,'a'):
				_0_0_1=_0_0_0.get_attribute(base64.b64decode('aHJlZg==').decode('utf-8'))
				if _0_0_1:
					O01_00=OO00O0(_001_0,_0_0_1)
					if OO0OO0(O01_00).netloc==_00101 and O01_00 not in O01001 and O01_00 not in O0100_:
						if any(O01_0_ in O01_00.lower()for O01_0_ in _00111):O0100_.insert(0,O01_00)
						else:O0100_.append(O01_00)
		except Exception:pass
	return O01010,O01011
def O00101(index,row):
	_01010=index;_01011=str(row[base64.b64decode('dXJs').decode('utf-8')]).strip();O01010=_01011.split(';')[0]
	if not O01010:return{'final_url':'EMPTY_URL','phones':'','emails':''}
	O0OO0O.info(f"[Строка #{_01010+1}] Начинаю обработку URL-посредника: {O01010}");_0101_=O00000()
	try:
		_0101_.get(O01010);_01100=None;_01101=O0OOO0(_0101_,10)
		try:O0OO0O.info(f"[Строка #{_01010+1}] Ищу ссылку на реальный сайт...");_01110=_01101.until(O0OOOO.presence_of_element_located((O0OO00.CSS_SELECTOR,base64.b64decode('YVtkYXRhLXFhPSdzaXRlLWxpbmsn]').decode('utf-8'))));_01100=_01110.get_attribute(base64.b64decode('aHJlZg==').decode('utf-8'))
		except OO0000:raise Exception('Не удалось найти ссылку на реальный сайт (timeout). Stealth-режим активен, но ссылка не найдена.')
		if not _01100:raise Exception('Ссылка на реальный сайт найдена, но она пустая.')
		O0OO0O.info(f"[Строка #{_01010+1}] Найден реальный сайт: {_01100}");_01111,_0_1_1=O00100(_0101_,_01100);O0__10=';'.join(_O0O0O0(list(_01111)));O0__11=';'.join(_O0O0O0(list(_0_1_1)));O0OO0O.info(f"[Строка #{_01010+1}] Найдено для {_01100}: {len(_01111)} тел., {len(_0_1_1)} email.");return{'final_url':_01100,'phones':O0__10,'emails':O0__11}
	except Exception as O0___1:O10000=str(O0___1).splitlines()[0];O0OO0O.error(f"[Строка #{_01010+1}] ОШИБКА при обработке {O01010}: {O10000}");return{'final_url':f"ERROR on {O01010}",'phones':'','emails':''}
	finally:_0101_.quit()
def O00110():
	_10000='\n';_10001='utf-8'
	try:_10010=O00O0O.read_csv(O000O0,sep=';',header=None,names=[base64.b64decode('dXJs').decode('utf-8')])
	except FileNotFoundError:O0OO0O.error(f"Файл с URL не найден: {O000O0}");return
	for _10011 in[O00O00,O00OO0,O00O_0]:
		with open(_10011,'w')as _1001_:0
	_10100=OOOO00.Lock();_10101=len(_10010)
	with OOO0O0.ThreadPoolExecutor(max_workers=OOO00O,thread_name_prefix='Worker')as _1010_:
		_10110={_1010_.submit(O00101,_10111,_10_00):_10111 for(_10111,_10_00)in _10010.iterrows()};_10_01=0
		for _10_10 in OOO0O0.as_completed(_10110):
			_10_01+=1;_10_11=_10110[_10_10]
			try:
				_11000=_10_10.result();_11001=_11000.get('final_url','');_11010=_11000.get('phones','');_11011=_11000.get('emails','')
				with _10100:
					with open(O00O00,'a',encoding=_10001)as _110_0,open(O00OO0,'a',encoding=_10001)as _110_1,open(O00O_0,'a',encoding=_10001)as _11100:_110_0.write(_11001+_10000);_110_1.write(_11010+_10000);_11100.write(_11011+_10000)
				O0OO0O.info(f"({_10_01}/{_10101}) [Строка #{_10_11+1}] Результат записан в файлы.")
			except Exception as _11101:O0OO0O.error(f"Критическая ошибка при обработке результата для строки #{_10_11+1}: {_11101}")
	O0OO0O.info(f"Обработка завершена. Результаты в файлах: {O00O00}, {O00OO0}, {O00O_0}")
if __name__=='__main__':O00110()
