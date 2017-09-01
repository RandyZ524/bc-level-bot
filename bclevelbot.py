from bs4 import BeautifulSoup
from urllib.parse import urlparse

import praw
import time
import re
import requests
import bs4
import locale

path = 'commented.txt'

header = '**Enemies in the level:**\n'
footer = '\n\n^I\'m ^a ^bot ^| ^I ^was ^developed ^by ^u/RandyZ524 ^| ^Please ^PM ^him ^for ^any ^comments, ^suggestions, ^or ^bug ^reports'

def authenticate():
	
	print('Authenticating...\n')
	reddit = praw.Reddit('bclevelbot', user_agent = 'web:battle-cats-level-info:v0.1 (by /u/RandyZ524)')
	print('Authenticated as {}\n'.format(reddit.user.me()))
	return reddit


def fetchdata(url):
	
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	
	[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
	visible_data = soup.getText()
	
	visible_data = visible_data[visible_data.find('Stage Information') + len('Stage Information'):visible_data.find('Prev. Stage')]
	
	print(visible_data)
	
	energy = 'N/A'
	basehealth = 'N/A'
	enemieslist = 'N/A (0%)'
	enemyboss = 'N/A'
	treasure = 'N/A (Unlimited)'
	xp = 'N/A'
	stagewidth = 'N/A'
	
	energy_string = visible_data[:visible_data.find('Enemy Base\'s Health')]
	energy_string = re.sub(r'\s+', '', energy_string)
	energy = re.sub('\D', '', energy_string)
	visible_data = visible_data[visible_data.find('Enemy Base\'s Health'):]
	
	basehealth_string = visible_data[:visible_data.find('Enemies')]
	basehealth_string = re.sub(r'\s+', '', basehealth_string)
	basehealth = re.sub('\D', '', basehealth_string)
	visible_data = visible_data[visible_data.find('Enemies'):]
	
	enemies_string = visible_data[:visible_data.find('Enemy Boss')]
	enemies_string = enemies_string[8:].strip()
	enemies_string = enemies_string.replace('-', '')
	enemies_string = enemies_string.replace('%)', '%)\n\n* ')
	enemieslist = enemies_string.replace('*  ', '* ')
	visible_data = visible_data[visible_data.find('Enemy Boss'):]
	
	enemyboss_string = visible_data[:visible_data.find('Treasure')]
	enemyboss = enemyboss_string[11:].strip()
	visible_data = visible_data[visible_data.find('Treasure'):]
	
	treasure_string = visible_data[9:visible_data.find('Misc. Information')]
	treasure_string = treasure_string.replace('- ', '').strip()
	treasure = treasure_string.replace(')', ')\n\n* ')
	if (treasure[-2:] == '* '):
		treasure = treasure[:-2]
	visible_data = visible_data[visible_data.find('Misc. Information'):]
	
	xp_string = visible_data[:visible_data.find('Stage Width')]
	xp_string = re.sub(r'\s+', '', xp_string)
	xp = re.sub(r'[^\d~]+', '', xp_string)
	visible_data = visible_data[visible_data.find('Stage Width'):]
	
	stagewidth_string = visible_data[:visible_data.find('Max number of Enemies')]
	stagewidth_string = re.sub(r'\s+', '', stagewidth_string)
	stagewidth = re.sub('\D', '', stagewidth_string)
	visible_data = visible_data[visible_data.find('Max number of Enemies'):]
	
	maxenemies_string = visible_data[:visible_data.find('Location Information')]
	maxenemies_string = re.sub(r'\s+', '', maxenemies_string)
	maxenemies = re.sub('\D', '', maxenemies_string)
	visible_data = visible_data[visible_data.find('Location Information'):]
	
	subchapter_string = visible_data[visible_data.find('Sub-chapter') + len('Sub-chapter:'):]
	subchapter = subchapter_string.strip()
	
	data = '**Energy Cost:** ' + energy + '\n\n**Enemy Base Health:** ' + basehealth + '\n\n**Enemies:**\n\n* ' + enemieslist + '**Enemy Boss:** ' + enemyboss + '\n\n**Treasure:**\n\n* ' + treasure + '\n\n**XP gained:** ' + xp + '\n\n**Stage Width:** ' + stagewidth + '\n\n**Max Enemies:** ' + maxenemies + '\n\n**Subchapter:** ' + subchapter
	print(data)
	return data


def run_bclevelbot(reddit):
	
	print("Getting 250 comments...\n")
	pat = r'(?<=\[\[).+?(?=\]\])'
	
	for comment in reddit.subreddit('test').comments(limit = 250):
		match = re.findall(pat, comment.body)
		if match:
			print("Link found in comment with comment ID: " + comment.id)
			user_levelname = match[0]
			bc_levelname = user_levelname.replace(' ', '_')
			bc_levelname = bc_levelname.replace("'", '%27')
			bc_levelname = bc_levelname.replace('&', '%26')
			myurl = 'http://battle-cats.wikia.com/wiki/' + bc_levelname
			print(myurl)
			
			file_obj_r = open(path,'r')

			try:
				enemies = fetchdata(myurl)
				print(enemies)
			except:
				print('Exception!!! Possibly incorrect URL...\n')
			else:
				if comment.id not in file_obj_r.read().splitlines():
					print('Link is unique...posting enemies\n')
					header = '# **' + str(user_levelname) + '**\n'
					comment.reply(header + enemies + footer)

					file_obj_r.close()

					file_obj_w = open(path,'a+')
					file_obj_w.write(comment.id + '\n')
					file_obj_w.close()
				else:
					print('Already visited link...No reply needed\n')
					
			time.sleep(10)

	print('Waiting 60 seconds...\n')
	time.sleep(60)


def main():
	reddit = authenticate()
	while True:
		run_bclevelbot(reddit)


if __name__ == '__main__':
	main()