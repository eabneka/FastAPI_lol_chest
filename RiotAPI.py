from requests import Session
from .config import settings
from .schemas import SummonerBase

def summonerByName(name:str):
	s = Session()
	s.headers.update({'X-Riot-Token': f'{settings.X_Riot_Token}'})

	response = s.get(f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}')
	if response.status_code != 200:
		raise Exception()

	dictionary = response.json()
	return dictionary['accountId'], dictionary['id'], dictionary['name']

def top_n_Mastery(summonerId:str):
	s = Session()
	s.headers.update({'X-Riot-Token': f'{settings.X_Riot_Token}'})

	response = s.get(f'https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/top?count=10')
	if response.status_code != 200:
		raise Exception()

	championList = response.json()

	keys = ['championId', 'championPoints', 'lastPlayTime', 'chestGranted', 'summonerId']
	ls = []
	for i in range(len(championList)):
		ls.append({k:championList[i][k] for k in keys})

	return ls

def fillChampion():
	s = Session()

	response = s.get('https://ddragon.leagueoflegends.com/cdn/13.11.1/data/ko_KR/champion.json')
	data = response.json()['data']

	champions = list(data)
	keys = ['id','key','name']

	ls=[]

	for champ in champions:
		ls.append({k:data[champ][k] for k in keys})

	return ls


