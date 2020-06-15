import os, requests, json, re
from bs4 import BeautifulSoup

class ZKTeco:
	def __init__(self, *arg, **kwargs):
		self.conf = os.path.join(os.path.dirname(__file__), "settings.conf")
		self.username = ""
		self.password = ""
		self.domain = ""
		self.cookies = None
		self.timeout = 3
		self.r = None
		self.read_conf()

	def purify_conf(self, block: str) -> dict:
		# block_list = block\
		block = block.replace("zkteco]\n", "")
		# 	.replace("\n", "=")\
		# 	.replace("\"","")\
		# 	.replace("\'", "")\
		# 	.strip().split("=")

		conf = dict()
		for line in block.splitlines():
			line_content = re.search(r'(?P<key>\w+)[ ]*[=]["]?(?P<value>(\w+[.]?)+)["]?', line)
			try:
				line_content = line_content.groupdict()
				conf[line_content.get("key")] = line_content.get("value")
			except:
				continue
		return conf

	def read_conf(self) -> None:
		with open(self.conf, "r") as fichier:
			conf = ""
			for block in fichier.read().split("["):
				if block.startswith("zkteco"):
					conf = self.purify_conf(block)
					self.username = conf.get("username")
					self.userpwd = conf.get("userpwd")
					self.domain = conf.get("domain")
					self.timeout = float(conf.get("timeout", 3))
					break
			if(conf == ""):
				raise Exception("settings.conf [zkteco] session not valid")

	def create_connection(self) -> None:
		logins = {
			"username":self.username,
			"userpwd":self.userpwd
		}
		try:
			self.r = requests.get("http://"+self.domain, timeout=self.timeout)
		except:
			return {"erreur": "une erreur de connectivité est survenue"}
		self.cookies = self.r.cookies
		try:
			self.r = requests.post("http://"+self.domain+"/csl/check", data=logins, cookies=self.cookies, timeout=self.timeout)
		except:
			return {"erreur": "une erreur de connectivité est survenue"}

	def logs(self, id_user, sdate="2020-05-25", edate="2020-05-31", tryout=True) ->str:
		api_request = {
			"sdate":sdate,
			"edate":edate,
			"period":4,
			"uid":id_user,
		}
		# self.r = requests.post("http://"+self.domain+"/csl/query?action=run", data=api_request, cookies=self.cookies, timeout=self.timeout)
		try:
			self.r = requests.post("http://"+self.domain+"/csl/query?action=run", data=api_request, cookies=self.cookies, timeout=self.timeout)
		except:
			return {"erreur": "une erreur de connectivité est survenue"}
		if(self.r.content.startswith(b"HTTP") and tryout):
			print("======= NEW SESSION =======")
			self.create_connection()
			return self.logs(id_user, sdate, edate, tryout=False)

		soup = BeautifulSoup(self.r.content)
		soup_table = soup.find_all("tr")
		data = []
		colums = [x.text for x in soup_table.pop(0).find_all('td')]
		for row in soup_table:
			new_data = {}
			for i, value in enumerate(row.find_all("td")):
				new_data[colums[i]] = value.text
			data.append(new_data)
		return data
		# return str(self.r.content)

	def users(self, first=None, last=None, tryout=True) ->str:
		data = {
			"first":first if first else 0,
			"last":last if last else 1000
		}

		try:
			self.r = requests.get("http://"+self.domain+"/csl/user", params=data, cookies=self.cookies, timeout=self.timeout)
		except:
			return {"erreur": "une erreur de connectivité est survenue"}

		if(self.r.content.startswith(b"HTTP") and tryout):
			self.create_connection()
			return self.users(first, last, tryout=False)

		soup = BeautifulSoup(self.r.content).find("div", class_="t_i")
		soup_table = soup.find_all("tr")
		data = []
		colums = [x.text for x in soup_table.pop(0).find_all('td')]
		for row in soup_table:
			new_data = {}
			for i, value in enumerate(row.find_all("td")):
				if value.text.lower()=="option":
					continue
				if(i == 0):
					new_data["uid"] = value.find('input').get("value")
					continue
				new_data[colums[i]] = value.text	
			data.append(new_data)
		return data
		# return str(self.r.content)