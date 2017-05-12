import requests
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def delete_from_s3(presigned_url):
	r = requests.delete(presigned_url)
	return r.status_code
