#!/usr/bin/python
from bs4 import BeautifulSoup
import requests
import csv
import sys


if len(sys.argv) < 2:
	print 'Please enter the search query'
	sys.exit()

search_query = sys.argv[1]


base_url = 'https://www.data.gov'
res = requests.get(base_url)
soup = BeautifulSoup(res.text, 'lxml')


action = soup.header.find('form', role='search')['action']
query_url =  'https:{}?q={}'.format(action, search_query.encode('utf-8'))


res = requests.get(query_url)
soup = BeautifulSoup(res.text, 'lxml')

paginator = soup.find('div', class_='pagination pagination-centered')
bullets = paginator.find_all('li')
total_pages = len(bullets)-1

pages_visited = 1
counter = 1
with open('datagov_export.csv', 'w') as f:
	file_writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_MINIMAL)
	volume_header = ['Organization', 'Data Set Name', 'Data Formats']
	file_writer.writerow(volume_header)

	while pages_visited <= total_pages:
		results = soup.find('div', class_='new-results').text.strip()
		num_results = results.split(" datasets found for")[0]

		module_content = soup.findAll('div', class_='module-content')[0]
		contents = module_content.find_all('div', class_='dataset-content')

		for content in contents:
			try:
				heading = content.h3.a.text
				print '{} : {}'.format(counter, heading)
			except AttributeError:
				heading = ''

			try:
				organization = content.find('span', class_='organization-type').span.text
				print organization
			except AttributeError:
				organization = ''

			try:
				formats = content.ul.find_all('li')
				list_formats = []
				for format_ in formats:
					list_formats.append(str(format_.text).strip())
			except AttributeError:
				list_formats = []
			print 'Formats: {}\n\n'.format(list_formats)
			file_writer.writerow([organization, heading, ','.join(list_formats)])
			counter += 1

		pages_visited +=1
		query_url =  'https:{}?q={}&page={}'.format(action, search_query.encode('utf-8'), pages_visited)
		res = requests.get(query_url)
		soup = BeautifulSoup(res.text, 'lxml')

print 'Data successfully exported to file datagov_export.csv'