import urllib.request
import re
import time
import json

def awaitContinueRequest(action = "continue"):
    input("Press Enter to " + action + "...\n")

class TenMinuteMailGenerator(object):
    """generates 10 minute mails from 10minutemail.com"""

    def __init__(self):
        self.SIDCookie = ""

    def get10MinuteMail(self, simulate = False):
        """gets the email adress of 10 minute mail

            *Returns*: email address"""
        if simulate != True:

            req = urllib.request.Request(
                "https://10minutemail.com/10MinuteMail/index.html", 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
                }
            )

            ## get 10 mail ##
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
                m = re.search('data-clipboard-text="([a-zA-Z0-9@.]*)" id="copyAddress"', html)
            
                headers = response.getheaders()
                self.SIDCookie = next(y for x, y in headers if x == "Set-Cookie" and y.startswith("JSESSIONID"))

                return m.group(1)


        else:
            self.SIDCookie = "JSESSIONID=LIKd7IlHq0lhpTOsWJdPY-RPCTpk5vr3qXuvque4.syndi; path=/10MinuteMail; secure; HttpOnly";
            return "r446338@mvrht.net"

    def anyNewMessage(self, currentMessageCount):
        """checks for new messages as long as necessary 
            currentMessageCount: The current count of messages the new count of messages shall be compared with

            *Returns*: new message count as int"""

        totalPointCount = 3
        pointCount = 1

        while (True):
            req = urllib.request.Request(
                "https://10minutemail.com/10MinuteMail/resources/messages/messageCount", 
                data=None, 
                headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
            )
        
            req.add_header("Accept", "*/*")
            req.add_header("Connection", "keep-alive")
            req.add_header("cookie", self.SIDCookie)

            with urllib.request.urlopen(req) as response:
                messageCount = response.read().decode('utf-8')

            if int(messageCount) > currentMessageCount:
                print("You got new mail! " + messageCount)
                break;
            else:
                print("Waiting for new mails.. currently " + messageCount + " messages" + ('.' * pointCount) + (" " * (totalPointCount - pointCount))+ "\r", end="", flush=True)

            # the page works with a 10-second-interval, so adjust that if necessary
            time.sleep(5)

            # reset point count so we can get a smooth "animation"
            if pointCount >= totalPointCount:
                pointCount = 1
            else:
                pointCount += 1

        return int(messageCount)

    def getMessage(self, messageID):
        """get message with given ID and return a json object with mail parameters 
            messageID: Message to load

            *Returns*: message as json object"""

        print("getting mail " + str(messageID))

        req = urllib.request.Request(
            "https://10minutemail.com/10MinuteMail/resources/messages/messagesAfter/" + str(messageID), 
            data=None, 
            headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
           )
    
        req.add_header("Accept", "*/*")
        req.add_header("Connection", "keep-alive")
        req.add_header("cookie", self.SIDCookie)

        with urllib.request.urlopen(req) as response:
            message = response.read().decode('utf-8')

        # example:
        # [{"id":"-2768562531071984888","subject":"Fw: Test-Mail","attachments":[],"forwarded":false,"fromList":["test@xyz.de"],"formattedDate":"Oct 23, 2017 9:15:56 AM","bodyPreview":"","attachmentCount":0,"recipientList":["r525128@mvrht.net"],"read":false,"repliedTo":false,"expanded":false,"bodyPlainText":null,"bodyText":"<html><head></head><body><div style=\"font-family: Verdana;font-size: 12.0px;\"><div>&nbsp;\r\n<div>&nbsp;\r\n<div name=\"quote\" style=\"margin:10px 5px 5px 10px; padding: 10px 0 10px 10px; border-left:2px solid #C3D9E5; word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;\">\r\n<div style=\"margin:0 0 10px 0;\"><b>Gesendet:</b>&nbsp;Montag, 23. Oktober 2017 um 12:52 Uhr<br/>\r\n<b>Von:</b>&nbsp;&quot;Max Mustermann&quot; &lt;text@xyz.de&gt;<br/>\r\n<b>An:</b>&nbsp;r505895@mvrht.net<br/>\r\n<b>Betreff:</b>&nbsp;Fw: Test-Mail</div>\r\n\r\n<div name=\"quoted-content\">\r\n<div style=\"font-family: Verdana;font-size: 12.0px;\">\r\n<div>&nbsp;\r\n<div>&nbsp;\r\n<div style=\"margin: 10.0px 5.0px 5.0px 10.0px;padding: 10.0px 0 10.0px 10.0px;border-left: 2.0px solid rgb(195,217,229);\">\r\n<div style=\"margin: 0 0 10.0px 0;\"><b>Gesendet:</b>&nbsp;Montag, 23. Oktober 2017 um 12:50 Uhr<br/>\r\n<b>Von:</b>&nbsp;&quot;Max Mustermann&quot; &lt;test@xyz.de&gt;<br/>\r\n<b>An:</b>&nbsp;r506390@mvrht.net<br/>\r\n<b>Betreff:</b>&nbsp;Test-Mail</div>\r\n\r\n<div>\r\n<div style=\"font-family: Verdana;font-size: 12.0px;\">\r\n<div>Kleiner Test ob das auch funktioniert</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div></div></body></html>\r\n","sentDate":1508768156000,"primaryFromAddress":"test@xyz.de"}]
        return json.loads(message);

    def showMessage(self, json):
        return "Sender: " + json[0]['primaryFromAddress'] + "\nSubject: " + json[0]['subject'] + "\nMessage: " + json[0]['bodyText'] + "\n"

if __name__ == '__main__':
    
    awaitContinueRequest("generate a mail adress")
    Tenmmg = TenMinuteMailGenerator()

    print ("Generating mail..")
    print(Tenmmg.get10MinuteMail())
    
    i = -1
    while True:
        option = input("Waiting for new message? [Y]es (json raw output), [N]o (Ends script), Yes but show me extracted sender, subject and [B]ody\n")
        i += 1

        if option.lower().startswith("y"):
           print (Tenmmg.getMessage(Tenmmg.anyNewMessage(i) - 1)) 
        elif option.lower().startswith("b"):
           print (Tenmmg.showMessage(Tenmmg.getMessage(Tenmmg.anyNewMessage(i) - 1)))
        else:
            break;
    