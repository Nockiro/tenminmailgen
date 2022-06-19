import urllib.request
import time
import json

def awaitContinueRequest(action = "continue"):
    input("Press Enter to " + action + "...\n")

BASE_URI = "https://10minutemail.com/"
ENDPOINT_GETADDRESS = "session/address"
ENDPOINT_RESETINTERVAL = "session/reset"
ENDPOINT_GETMSGCOUNT = "messages/messageCount"
ENDPOINT_GETMSG = "messages/messagesAfter/{0}"

FAKE_REQUEST_HEADERS = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' }

# the page works with a 10-second-interval, so adjust that if necessary
REQUEST_INTERVAL = 5

class TenMinuteMailGenerator(object):
    """generates 10 minute mails from 10minutemail.com"""

    def __init__(self):
        self.SIDCookie = ""

    def get10MinuteMail(self, simulate = False):
        """gets the email adress of 10 minute mail

            *Returns*: email address"""
        if simulate != True:

            req = urllib.request.Request( "https://10minutemail.com/session/address", data=None, headers= FAKE_REQUEST_HEADERS )

            ## get 10 mail ##
            with urllib.request.urlopen(req) as response:
                jsonResponse = response.read().decode('utf-8')
                mailResponseObject = json.loads(jsonResponse)
                self.SIDCookie = response.info().get_all('Set-Cookie')[0]

                return mailResponseObject["address"]

        else:
            self.SIDCookie = "JSESSIONID=LIKd7IlHq0lhpTOsWJdPY-RPCTpk5vr3qXuvque4.syndi; path=/10MinuteMail; secure; HttpOnly";
            return "r446338@mvrht.net"

    def anyNewMessage(self, currentMessageCount):
        """waits/checks for new messages as long as necessary
            currentMessageCount: The current count of messages the new count of messages shall be compared with

            *Returns*: new message count as int"""

        totalPointCount = 3
        pointCount = 1

        totalWaitTime = 0

        while (True):
            messageCount = json.loads(self.doApiRequest(ENDPOINT_GETMSGCOUNT))["messageCount"]

            if messageCount > currentMessageCount:
                print("\n> You got new mail! " + str(messageCount))
                break
            else:
                print("> Waiting for new mails.. currently " + str(messageCount) + " messages" + ('.' * pointCount) + (" " * (totalPointCount - pointCount))+ "\r", end="", flush=True)

            time.sleep(REQUEST_INTERVAL)
            totalWaitTime += REQUEST_INTERVAL

            if totalWaitTime > 500:
                print("> 500 seconds over.. requesting extension.")
                self.renewInterval()

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

        print("> Getting mail " + str(messageID))
        message = self.doApiRequest(ENDPOINT_GETMSG.format(messageID), True)

        # example:
        # [{"read":false,"expanded":false,"forwarded":false,"repliedTo":false,"sentDate":"2022-06-19T20:37:33.000+00:00","sentDateFormatted":"Jun 19, 2022, 8:37:33 PM","sender":"sender@mail.de","from":"[Ljavax.mail.internet.InternetAddress;@1dd3705c","subject":"Test-Mail","bodyPlainText":"\r\n\r\n\r\nDies ist eine Test-Mail - Yay.\r\n-- Für mehr Informationen gerne nachfragen.","bodyHtmlContent":"<html>\r\n  <head>\r\n\r\n    <meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\">\r\n  </head>\r\n  <body>\r\n    <p><br>\r\n    </p>\r\n  Dies ist eine Test-Mail - Yay.<br>\r\n    </div>\r\n    Für mehr Informationen gerne nachfragen.</div>\r\n  </body>\r\n</html>\r\n","bodyPreview":"\r\n\r\n\r\n-------- Forwarded Message --------\r\nSubject","id":"10531382251204271300"}]
        return json.loads(message)

    def showMessage(self, json):
        return "Sender: " + json[0]['sender'] + "\nSubject: " + json[0]['subject'] + "\nMessage: " + json[0]['bodyPlainText'] + "\n"

    def renewInterval(self):
        """requests another 10 minutes to keep the mail address active"""

        print("Sending renewal request..")
        return self.doApiRequest(ENDPOINT_RESETINTERVAL, True)

    def doApiRequest(self, apiEndpoint: str, printOkay: bool = False):
        req = urllib.request.Request(BASE_URI + apiEndpoint, data=None, headers= FAKE_REQUEST_HEADERS)
        req.add_header("Accept", "*/*")
        req.add_header("Connection", "keep-alive")

        if self.SIDCookie != "":
            req.add_header("cookie", self.SIDCookie)

        with urllib.request.urlopen(req) as response:
            message = response.read().decode('utf-8')

        if printOkay and response.getcode() == 200:
            print("> Request successful!")

        if response.getcode() >= 400:
            print("> Something went wrong!")

        return message

if __name__ == '__main__':

    awaitContinueRequest("generate a mail adress")
    Tenmmg = TenMinuteMailGenerator()

    print("> Generating mail.. ")
    print("> Generated mail: " + Tenmmg.get10MinuteMail())

    i = -1
    while True:
        option = input("> Waiting for new message? [Y]es (json raw output), [N]o (Ends script), Yes but show me extracted sender, subject and [B]ody\n")
        i += 1

        if option.lower().startswith("y"):
           print (Tenmmg.getMessage(Tenmmg.anyNewMessage(i) - 1))
        elif option.lower().startswith("b"):
           print (Tenmmg.showMessage(Tenmmg.getMessage(Tenmmg.anyNewMessage(i) - 1)))
        else:
            break
