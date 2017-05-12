import requests
import json
import logging
import sys

from config import MLAB_API_KEY

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def read_from_mlab(**kwargs):
	q = {}
	if kwargs.get('caption'):
		q['caption'] = kwargs.get('caption')
	if kwargs.get('description'):
		q['description'] = kwargs.get('description')
	if kwargs.get('image_url'):
		q['image_url'] = kwargs.get('image_url')

	api_key = MLAB_API_KEY
	url_base = 'https://api.mlab.com/api/1/databases/sellsnapshots-test/collections/photos?q='
	url = url_base  + json.dumps(q) + '&apiKey='+ api_key

	logging.info("Read api call to mlab")
	response = requests.get(url)
	search_results = response.json()
	status_code = response.status_code

	return search_results, status_code

def update_to_mlab(image_data):
	api_key = MLAB_API_KEY
	url = 'https://api.mlab.com/api/1/databases/sellsnapshots-test/collections/photos?apiKey=' + api_key
	headers = {'content-type': 'application/json; charset=utf-8'}
	data = json.dumps(image_data)

	logging.info("Update api call to mlab")
	response = requests.post(url, data=data, headers=headers)

	return response.status_code

def delete_from_mlab(image_url):
	api_key = MLAB_API_KEY
	search_results, staus_code = read_from_mlab(image_url=image_url)
	if len(search_results) == 1:
		id = search_results[0].get("_id").get("$oid")
		url = 'https://api.mlab.com/api/1/databases/sellsnapshots-test/collections/photos/' + id + '?apiKey=' + api_key		
		r = requests.delete(url)
		return r.status_code
	return -1
