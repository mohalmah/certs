from threading import Thread
from time import perf_counter
from PIL import Image, ImageFont, ImageDraw
import glob
import pandas as pd
import requests
from io import BytesIO
import urllib.request
from urllib.request import urlretrieve
import xlrd
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import boto3
import string

ses_client = boto3.client('ses')

# Global Variables
SHEET_URL_PARAMS = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQpWW0q9KHe0sMjcLW4Xi6kU9AhfVmrIUyhrHy-dgUrj1Fm0yLX1RCBIfJbCQVyvV6NwiXC90EyK9oN/pub?gid=1419166889&single=true&output=csv'
SHEET_URL_LIST = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQpWW0q9KHe0sMjcLW4Xi6kU9AhfVmrIUyhrHy-dgUrj1Fm0yLX1RCBIfJbCQVyvV6NwiXC90EyK9oN/pub?gid=0&single=true&output=csv'
urllib.request.urlretrieve(
  SHEET_URL_PARAMS,
   "params/params.csv")
params_col_list = ["Item", "URLofparam"]
allparams = pd.read_csv("params/params.csv", usecols=params_col_list)
itemparam = allparams["Item"]
urlparam = allparams["URLofparam"]
certtemplatelink = urlparam[0]
fonttemplatelink = urlparam[1] 
bodytemplatelink = urlparam[2]
textpos = float(urlparam[3])
fontcolor = urlparam[4]
fontSize = int(float(urlparam[5]))
print("text position in certificate: ",textpos)   
urllib.request.urlretrieve(
  
   fonttemplatelink,"font.ttf")
urllib.request.urlretrieve(
  SHEET_URL_LIST,
   "params/list2.csv")
urllib.request.urlretrieve(
  
   certtemplatelink,"params/certtemp.png")
urllib.request.urlretrieve(
  
  bodytemplatelink,"params/body.html")
FONT_FILE = ImageFont.truetype(r'font.ttf', fontSize)
FONT_COLOR = fontcolor


template = Image.open(r'params/certtemp.png')
WIDTH, HEIGHT = template.size

def remove_dir_content():
    files = glob.glob('out/*')
    for f in files:
        os.remove(f)
def make_certificates(name):
    '''Function to save certificates as a .png file'''


    image_sourcergba = Image.open(r'params/certtemp.png')

    
    rgb = Image.new('RGB', image_sourcergba.size, (255, 255, 255))  # white background
    rgb.paste(image_sourcergba, mask=image_sourcergba.split()[3])               # paste using alpha channel as mask
 
    newname = name.translate(str.maketrans('', '', string.punctuation))

    draw = ImageDraw.Draw(rgb)
    try:
        # Finding the width and height of the text. 
        name_width, name_height = draw.textsize(name, font=FONT_FILE)

        # Placing it in the center, then making some adjustments.
        draw.text(((WIDTH - name_width) / 2, (HEIGHT - name_height) / textpos - 31), name, fill=FONT_COLOR, font=FONT_FILE)
    
            
        rgb.save( 'out/'+newname.replace(" ", "_")+'.pdf', "PDF", resolution=100.0)

    except Exception as e:
        print("Error: ", e)  

def send_cert_email(reciveremail,name):
    SENDER = "Ahmed AlQadasi <team@ahmedalqadasi.com>"
    RECEIVER = reciveremail
    CHARSET = "utf-8"
    msg = MIMEMultipart('mixed')
    msg['Subject'] = "Certificate of Attendance - Ahmed AlQadasi"
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    newname = name.translate(str.maketrans('', '', string.punctuation))
    msg_body = MIMEMultipart('alternative')
    # text based email body
    BODY_TEXT = "Dear,\n\rPlease using the given link to register today."

    HtmlFile = open('params/body.html', 'r', encoding='utf-8')
    BODY_HTML = HtmlFile.read() 
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Full path to the file that will be attached to the email.
    ATTACHMENT1 = 'out/'+newname.replace(" ", "_")+'.pdf'
    ATTACHMENT2 = 'out/'+newname.replace(" ", "_")+'.pdf'

    # Adding attachments
    att1 = MIMEApplication(open(ATTACHMENT1, 'rb').read())
    att1.add_header('Content-Disposition', 'attachment',
                    filename=os.path.basename(ATTACHMENT1))
    att2 = MIMEApplication(open(ATTACHMENT1, 'rb').read())
    att2.add_header('Content-Disposition', 'attachment',
                    filename=os.path.basename(ATTACHMENT2))

    msg.attach(msg_body)
    msg.attach(att1)
    msg.attach(att2)

    try:
        response = ses_client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECEIVER
            ],
            RawMessage={
                'Data': msg.as_string(),
            },
            #ConfigurationSetName="ConfigSet"
        )

    except Exception as e:
        print("Error: ", e)
        
def main():
    col_list = ["Name", "Emailsofparticipant"]
    names = pd.read_csv("params/list2.csv", usecols=col_list,na_filter= False)
    namesofpart = names["Name"]
    reciveremail = names["Emailsofparticipant"]

    
    remove_dir_content()

    # create threads
    threads = [Thread(target=make_certificates, args=(name,))
            for name in namesofpart]

    # start the threads
    for thread in threads:
        thread.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()

    #for name in namesofpart:
       # make_certificates(name)
    print("#############",len(names), " certificates done.\n#########")

    #for partiemail, partiname in zip(reciveremail, namesofpart):
    #    send_cert_email(partiemail,partiname)
    threads = [Thread(target=send_cert_email, args=(partiemail,partiname))
            for partiemail, partiname in zip(reciveremail, namesofpart)]

    # start the threads
    for thread in threads:
        thread.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()
    print("#############",len(names), "  emails sent\n########")

if __name__ == "__main__":

    start_time = perf_counter()

    main()

    end_time = perf_counter()
    print(f'It took {end_time- start_time :0.2f} second(s) to complete.')


    


