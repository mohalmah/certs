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
import string

ses_client = boto3.client('ses')

# Global Variables
urllib.request.urlretrieve(
  'https://docs.google.com/spreadsheets/d/e/2PACX-1vQpWW0q9KHe0sMjcLW4Xi6kU9AhfVmrIUyhrHy-dgUrj1Fm0yLX1RCBIfJbCQVyvV6NwiXC90EyK9oN/pub?gid=1419166889&single=true&output=csv',
   "params/params.csv")
params_col_list = ["Item", "URLofparam"]
allparams = pd.read_csv("params/params.csv", usecols=params_col_list)
itemparam = allparams["Item"]
urlparam = allparams["URLofparam"]
#print(urlparam,"###################\n###############")
certtemplatelink = urlparam[0]
fonttemplatelink = urlparam[1] 
bodytemplatelink = urlparam[2]
textpos = float(urlparam[3])
fontcolor = urlparam[4]
fontSize = int(float(urlparam[5]))
print("text position in certificate: ",textpos)   
urllib.request.urlretrieve(
  #'https://github.com/mohalmah/certs/blob/main/Cairo-SemiBold.ttf?raw=true',
   fonttemplatelink,"font.ttf")
urllib.request.urlretrieve(
  'https://docs.google.com/spreadsheets/d/e/2PACX-1vQpWW0q9KHe0sMjcLW4Xi6kU9AhfVmrIUyhrHy-dgUrj1Fm0yLX1RCBIfJbCQVyvV6NwiXC90EyK9oN/pub?gid=0&single=true&output=csv',
   "params/list2.csv")
urllib.request.urlretrieve(
  #'https://github.com/mohalmah/certs/blob/main/certtemplate.png?raw=true',
   certtemplatelink,"params/certtemp.png")
urllib.request.urlretrieve(
  #'https://raw.githubusercontent.com/mohalmah/certs/main/body.html',
  bodytemplatelink,"params/body.html")
FONT_FILE = ImageFont.truetype(r'font.ttf', fontSize)
FONT_COLOR = fontcolor
#response = requests.get("https://github.com/mohalmah/certs/blob/main/certtemplate.png")
#template = Image.open(BytesIO(response.content))
#template = Image.open(r'https://github.com/mohalmah/certs/blob/main/certtemplate.png')

#url = 'https://github.com/mohalmah/certs/blob/main/certtemplate.png'
#urlretrieve(url, 'certtemp.png')
#with urllib.request.urlopen(URL) as url:
#    with open('certtemp.png', 'wb') as f:
#        f.write(url.read())

template = Image.open(r'params/certtemp.png')
WIDTH, HEIGHT = template.size

def remove_dir_content():
    files = glob.glob('out/*')
    for f in files:
        os.remove(f)
def make_certificates(name):
    '''Function to save certificates as a .png file'''

#    image_source = Image.open(r'https://github.com/mohalmah/certs/blob/main/certtemplate.png')
    image_sourcergba = Image.open(r'params/certtemp.png')

    #rgba = Image.open(PNG_FILE)
    rgb = Image.new('RGB', image_sourcergba.size, (255, 255, 255))  # white background
    rgb.paste(image_sourcergba, mask=image_sourcergba.split()[3])               # paste using alpha channel as mask
    #rgb.save(PDF_FILE, 'PDF', resoultion=100.0)

    #rgb_im = image_source.convert('RGB')
    #png = Image.open(object.logo.path)
    #image_source.load() # required for png.split()
    newname = name.translate(str.maketrans('', '', string.punctuation))
    #image_source = Image.new("RGB", image_source.size, (255, 255, 255))
    #image_source.paste(image_source, mask=image_source.split()[3])
    #image_source.paste(image_source, mask=image_source.split()[3]) # 3 is the alpha channel
    draw = ImageDraw.Draw(rgb)
    try:
        # Finding the width and height of the text. 
        name_width, name_height = draw.textsize(name, font=FONT_FILE)

        # Placing it in the center, then making some adjustments.
        draw.text(((WIDTH - name_width) / 2, (HEIGHT - name_height) / textpos - 31), name, fill=FONT_COLOR, font=FONT_FILE)
        #rgb = Image.new('RGB', image_source.size, (255, 255, 255))  # white background
        #rgb.paste(image_source, mask=image_source.split()[3])               # paste using alpha channel as mask
            
        rgb.save( 'out/'+newname.replace(" ", "_")+'.pdf', "PDF", resolution=100.0)
        # Saving the certificates in a different directory.
        #image_source.save("./out/" + name.replace(" ", "_") +".png")
        #print('Saving Certificate of:', name.replace(" ", "_"))
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
    # HTML based email body
    #with open('email/body.html', 'r') as f:
    #    BODY_HTML = f.read()
    HtmlFile = open('params/body.html', 'r', encoding='utf-8')
    BODY_HTML = HtmlFile.read() 
    #BODY_HTML = "<html><head><title>Hello Buddy</title></head><body><h1>Hello Buddy</h1><p>This is html based email.</p></body></html>"
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
        #print("Message id : ", response['MessageId'])
        #print("Message send successfully!")
    except Exception as e:
        print("Error: ", e)
        

if __name__ == "__main__":

    #names = ['Tushar Nankani', "Full Name", 'Some Long Ass Name Might Not Work']
    col_list = ["Name", "Emailsofparticipant"]
    names = pd.read_csv("params/list2.csv", usecols=col_list,na_filter= False)
    #names = names.fillna(0, inplace=True)
    namesofpart = names["Name"]
    reciveremail = names["Emailsofparticipant"]
    #namesofpart= list(filter(None, namesofpart))
    #reciveremail = list(filter(None, reciveremail))
    
    remove_dir_content()
    for name in namesofpart:
        make_certificates(name)
    print("#############",len(names), " certificates done.\n#########")

    for partiemail, partiname in zip(reciveremail, namesofpart):
        send_cert_email(partiemail,partiname)
    print("#############",len(names), "  emails sent\n########")
    
    #for name in reciveremail:
       # for realname in namesofpart:
       #     send_cert_email(name,realname)

    #print(len(names), "email sent")

