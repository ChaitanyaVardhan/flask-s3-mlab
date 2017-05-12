from flask import Flask, render_template, request, redirect, url_for

from flask import render_template

import os, json, boto3, sys

from mlab import read_from_mlab, update_to_mlab, delete_from_mlab

from aws import delete_from_s3

import logging

app = Flask(__name__)

app.config.from_object('config')

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

CACHE = {}

@app.route('/')
def index():
  key = 'FRONT'
  if key in CACHE:
    images = CACHE[key]
  else:  
    images, status_code = read_from_mlab()
    CACHE[key] = images

  return render_template('index.html', images=images)

# Listen for POST requests to yourdomain.com/submit_form/
@app.route("/submit", methods = ["POST"])
def submit_form():
  # Collect the data posted from the HTML form in account.html:
  caption = request.form["caption"]
  description = request.form["description"]
  image_url = request.form["image-url"]

  # Upload image caption, image description and image url to mlab cloud nosql db
  image_data = dict(
    caption=caption,
    description=description,
  image_url=image_url
  )
  update_to_mlab(image_data=image_data)
  CACHE['FRONT'], status_code = read_from_mlab()

  # Redirect to the user's profile page, if appropriate
  return redirect(url_for('index'))

# Listen for GET requests to yourdomain.com/sign_s3/
@app.route('/sign-s3/')
def sign_s3():
  S3_BUCKET = app.config['S3_BUCKET']

  # Load required data from the request
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')

  # Initialise the S3 client
  s3 = boto3.client('s3')

  # Generate and return the presigned URL
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  # Return the data to the client
  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

# route to create presigned post for delete request
@app.route('/delete-image/')
def delete_s3_image():

  S3_BUCKET = app.config['S3_BUCKET']  
  file_name = request.args.get('img')
  url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)

  # Initialise the S3 client
  s3 = boto3.client('s3')  

  # Generate and return the presigned URL
  presigned_url = s3.generate_presigned_url(  
    ClientMethod='delete_object',
    Params={
        'Bucket': S3_BUCKET,
        'Key': file_name
    }
  )

  if presigned_url:
    status_code_delete = delete_from_s3(presigned_url)
    if status_code_delete == 200 or 204:
      status_code_delete_mlab = delete_from_mlab(url)
      if status_code_delete_mlab == 200:
        CACHE['FRONT'], status_code = read_from_mlab()
        if status_code == 200:    
          return json.dumps({
            'url': presigned_url,
            'status_code': status_code
            })

  return json.dumps({
  'status_code': -1
  })  

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
