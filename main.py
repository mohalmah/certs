from PIL import Image, ImageFont, ImageDraw
import glob
#import win32com.client as win32
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

ses_client = boto3.client('ses')

# Global Variables
FONT_FILE = ImageFont.truetype(r'font/Spectral-Bold.ttf', 60)
FONT_COLOR = "#efdeaf"
#response = requests.get("https://github.com/mohalmah/certs/blob/main/certtemplate.png")
#template = Image.open(BytesIO(response.content))
#template = Image.open(r'https://github.com/mohalmah/certs/blob/main/certtemplate.png')
urllib.request.urlretrieve(
  'https://github.com/mohalmah/certs/blob/main/certtemplate.png?raw=true',
   "certtemp.png")
urllib.request.urlretrieve(
  'https://docs.google.com/spreadsheets/d/e/2PACX-1vQpWW0q9KHe0sMjcLW4Xi6kU9AhfVmrIUyhrHy-dgUrj1Fm0yLX1RCBIfJbCQVyvV6NwiXC90EyK9oN/pub?gid=0&single=true&output=csv',
   "list2.csv")
#url = 'https://github.com/mohalmah/certs/blob/main/certtemplate.png'
#urlretrieve(url, 'certtemp.png')
#with urllib.request.urlopen(URL) as url:
#    with open('certtemp.png', 'wb') as f:
#        f.write(url.read())

template = Image.open(r'certtemp.png')
WIDTH, HEIGHT = template.size

def make_certificates(name):
    '''Function to save certificates as a .png file'''

#    image_source = Image.open(r'https://github.com/mohalmah/certs/blob/main/certtemplate.png')
    image_source = Image.open(r'certtemp.png')

    draw = ImageDraw.Draw(image_source)

    # Finding the width and height of the text. 
    name_width, name_height = draw.textsize(name, font=FONT_FILE)

    # Placing it in the center, then making some adjustments.
    draw.text(((WIDTH - name_width) / 2, (HEIGHT - name_height) / 1.68 - 31), name, fill=FONT_COLOR, font=FONT_FILE)
    #rgb = Image.new('RGB', image_source.size, (255, 255, 255))  # white background
    #rgb.paste(image_source, mask=image_source.split()[3])               # paste using alpha channel as mask
        
    image_source.save( './out/'+name.replace(" ", "_")+'.pdf', "PDF", resolution=100.0)
    # Saving the certificates in a different directory.
    #image_source.save("./out/" + name.replace(" ", "_") +".png")
    print('Saving Certificate of:', name.replace(" ", "_"))  

def send_cert_email(reciveremail,name):
    SENDER = "Ahmed AlQadasi <team@ahmedalqadasi.com>"
    RECEIVER = reciveremail
    CHARSET = "utf-8"
    msg = MIMEMultipart('mixed')
    msg['Subject'] = "This is test email For Ahmed AlQadasi Certificate Mailer"
    msg['From'] = SENDER
    msg['To'] = RECEIVER

    msg_body = MIMEMultipart('alternative')
    # text based email body
    BODY_TEXT = "Dear,\n\rPlease using the given link to register today."
    # HTML based email body
    #with open('email/body.html', 'r') as f:
    #    BODY_HTML = f.read()
    HtmlFile = open('emailbody/body.html', 'r', encoding='utf-8')
    BODY_HTML = HtmlFile.read() 
    #BODY_HTML = "<html><head><title>Hello Buddy</title></head><body><h1>Hello Buddy</h1><p>This is html based email.</p></body></html>"
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Full path to the file that will be attached to the email.
    ATTACHMENT1 = 'out/'+name.replace(" ", "_")+'.pdf'
    ATTACHMENT2 = 'out/'+name.replace(" ", "_")+'.pdf'

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
        print("Message id : ", response['MessageId'])
        print("Message send successfully!")
    except Exception as e:
        print("Error: ", e)
        

if __name__ == "__main__":

    #names = ['Tushar Nankani', "Full Name", 'Some Long Ass Name Might Not Work']
    col_list = ["Name", "Emailsofparticipant"]
    names = pd.read_csv("list2.csv", usecols=col_list)
    namesofpart = names["Name"]
    reciveremail = names["Emailsofparticipant"]
    

    for name in namesofpart:
        make_certificates(name)
    print(len(names), "certificates done.")

    for partiemail, partiname in zip(reciveremail, namesofpart):
        send_cert_email(partiemail,partiname)
    
    #for name in reciveremail:
       # for realname in namesofpart:
       #     send_cert_email(name,realname)

    print(len(names), "email sent")

