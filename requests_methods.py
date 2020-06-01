import os, requests, json
from bs4 import BeautifulSoup

class ZKTeco:
	def __init__(self, *arg, **kwargs):
		self.conf = os.path.join(os.path.dirname(__file__), "settings.conf")
		self.username = ""
		self.password = ""
		self.domain = ""
		self.cookies = None
		self.r = None
		self.read_conf()

	def purify_conf(self, block: str) -> dict:
		block_list = block\
			.replace("zkteco]\n", "")\
			.replace("\n", "=")\
			.replace("\"","")\
			.replace("\'", "")\
			.strip().split("=")

		conf = dict()
		while block_list:
			conf[block_list.pop(0).strip()] = block_list.pop(1).strip()
		return conf

	def read_conf(self) -> None:
		with open(self.conf, "r") as fichier:
			conf = ""
			for block in fichier.read().split("["):
				if block.startswith("zkteco"):
					conf = self.purify_conf(block)
					self.username = conf["username"]
					self.userpwd = conf["userpwd"]
					self.domain = conf["domain"]
					# timeout = float(conf["timeout"])
					break
			if(conf == ""):
				raise Exception("settings.conf [zkteco] session not valid")

	def create_connection(self) -> None:
		logins = {
			"username":self.username,
			"userpwd":self.userpwd
		}
		self.r = requests.get("http://"+self.domain)
		self.cookies = self.r.cookies
		self.r = requests.post("http://"+self.domain+"/csl/check", data=logins, cookies=self.cookies)

	def logs(self, id_user, sdate="2020-05-25", edate="2020-05-31", tryout=True) ->str:
		api_request = {
			"sdate":sdate,
			"edate":edate,
			"period":4,
			"uid":id_user,
		}
		# self.r = requests.post("http://"+self.domain+"/csl/query?action=run", data=api_request, cookies=self.cookies)
		self.r = requests.post("http://"+self.domain+"/csl/query?action=run", data=api_request, cookies=self.cookies)
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
		return json.dumps(data)
		# return str(self.r.content)

	def users(self, first=None, last=None, tryout=True) ->str:
		data = {
			"first":first if first else 0,
			"last":last if last else 1000
		}

		self.r = requests.get("http://"+self.domain+"/csl/user", params=data, cookies=self.cookies)
		print(self.r.raw)

		if(self.r.content.startswith(b"HTTP") and tryout):
			print("======= NEW SESSION =======")
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
		return json.dumps(data)
		# return str(self.r.content)