from bs4 import BeautifulSoup
from urllib.parse import urlparse

import praw
import time
import re
import requests
import bs4

path = '/Users/Randy/Documents/BC Level Bot/commented.txt'

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
	
	tag = soup.find('abbr')
	tag = tag.parent.nextSibling.nextSibling
	tag = tag.find('a')
	data = '\n\n' + tag.text.strip()
	tag = tag.nextSibling
	data = data + tag
	try:
		tag = tag.nextSibling.nextSibling
		tag_list = tag.find_all('a')
		tag_list2 = tag.find_all(string = re.compile('%'))
		my_list = [i.get_text() for i in tag_list]
	except:
		tag = tag
	else:
		for x in range(0, len(my_list)):
			data = data + '\n\n' + my_list[x]
			data = data + tag_list2[x]
	try:
		tag = soup.find(string = re.compile('Enemy Boss'))
		tag = tag.findParent('div')
		tag = tag.find('a')
		data = data + '\n\n' + '**Enemy Boss:** ' + tag.text
		tag = tag.nextSibling
		data = data + tag
	except:
		data = data + '\n\n' + '**Enemy Boss:** None'
	return data


def run_bclevelbot(reddit):
	
	print("Getting 250 comments...\n")
	pat = r'(?<=\[\[).+?(?=\]\])'
	
	for comment in reddit.subreddit('battlecats').comments(limit = 250):
		match = re.findall(pat, comment.body)
		if match:
			print("Link found in comment with comment ID: " + comment.id)
			user_levelname = match[0]
			bc_levelname = user_levelname.replace(' ', '_')
			myurl = 'http://battle-cats.wikia.com/wiki/' + str(bc_levelname)
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
					header = '**Enemies in ' + str(user_levelname) + ':**\n'
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