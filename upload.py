import sys
import boto3
import requests
import os
from functools import reduce

# https://docs.python.org/3/library/pathlib.html
import pathlib

#       constants       #
bucket_name = 'pdf-dev-learning'
s3 = boto3.resource('s3')

#       all the places the system scans to find pdfs
source_dirs = [
        '/var/spool/cups-pdf/ANONYMOUS/',
        '/var/spool/cups-pdf/JOBBOX/',
        '/home/PDF/',
        '/var/spool/cups-pdf/ANONYMOUS/'
]


#       HELPER FUNCTIONS        #

#       takes a file path and returns the email address stored in that file
def get_email (email_file):
        email = ""

        #       this is a default option for debugging; do not hardcode emails in production scripts
        if not email_file: 
                email = "jason.s.trager@gmail.com"
                print("setting email to the default value; should NEVER get here!!!")
        else:
                try: 
                        f = open(email_file, 'r')
                        email = f.read().strip()
                        f.close()
                except Exception as e:
                        print("a problem occurred opening this machine's email file: %s" % e)

        return email

#       saves a pdf to the remote server
def upload_pdf (pdf):
        data = pdf.open(mode='rb')
        name = pdf.name
        
        s3.Bucket(bucket_name).put_object(ACL='public-read', Key=name, Body=data, ContentType='pdf')
        url = 'https://%s.s3.amazonaws.com/%s' % (bucket_name, name)
        body = {'email': email, 'url': url, 'name': name, 'bucket': bucket_name}
        r = requests.post('https://job-box-server.herokuapp.com/api/pdfs/testing123', body)

        #       archive the PDF in the hidden .archived directory
        archive = pdf.parent.joinpath('.archived')
        if archive.is_dir():
                archived_file = archive.joinpath(pdf.name)
                archived_file.write_bytes(pdf.open(mode='rb').read())
                pdf.unlink()
        else:
                archive.mkdir(exist_ok=True, parents=True)
                archived_file = archive.joinpath(pdf.name)
                archived_file.write_bytes(pdf.open(mode='rb').read())
                pdf.unlink()


#       get file paths from a source directory path
def source_to_paths (source_dir):
        gen = pathlib.Path(source_dir).glob('*')
        file_paths = [p.absolute() for p in gen if p.is_file() and (p.match('*.pdf') or p.match('*.PDF') or p.match('*.Pdf'))]
        return file_paths


#       get the paths of all non-hidden files/directories in the source_dirs
pdfs = reduce((lambda x, y: x + y), [source_to_paths(s) for s in source_dirs])

#       gets the system email or a default; should never get the default (it's just there for error checking)
email = get_email('/etc/jobbox/user_email')


responses = [upload_pdf(p) for p in pdfs]

print(responses)
