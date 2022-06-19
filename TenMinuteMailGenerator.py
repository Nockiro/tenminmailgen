import urllib.request
import time
import json

BASE_URI = "https://10minutemail.com/"
ENDPOINT_GETADDRESS = "session/address"
ENDPOINT_RESETINTERVAL = "session/reset"
ENDPOINT_GETMSGCOUNT = "messages/messageCount"
ENDPOINT_GETMSG = "messages/messagesAfter/{0}"

FAKE_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

# the page works with a 10-second-interval, so adjust that if necessary
REQUEST_INTERVAL = 5


def awaitContinueRequest(action="continue"):
    input("Press Enter to " + action + "...\n")


class TenMinuteMailGenerator(object):
    """generates 10 minute mails from 10minutemail.com"""

    def __init__(self):
        self.SIDCookie = ""

    def get10MinuteMail(self, simulate=False):
        """gets a new email adress of 10minutemail

        *Returns*: email address"""
        if simulate != True:
            req = urllib.request.Request(
                "https://10minutemail.com/session/address",
                headers=FAKE_REQUEST_HEADERS,
            )

            with urllib.request.urlopen(req) as response:
                jsonResponse = response.read().decode("utf-8")
                self.SIDCookie = response.info().get_all("Set-Cookie")[0]

                return json.loads(jsonResponse)["address"]
        else:
            self.SIDCookie = (
                "JSESSIONID=LIKd7IlHq0lhpTOsWJdPY; path=/; secure; HttpOnly"
            )
            return "r446338@mvrht.net"

    def anyNewMessage(self, currentMessageCount):
        """waits/checks for new messages as long as necessary
        currentMessageCount: The current count of messages the new count of messages shall be compared with

        *Returns*: new message count as int"""

        totalPointCount = 3
        pointCount = 1
        totalWaitTime = 0

        while True:
            messageCount = json.loads(self.doApiRequest(ENDPOINT_GETMSGCOUNT))[
                "messageCount"
            ]

            if messageCount > currentMessageCount:
                print("\n> You got new mail! " + str(messageCount))
                break
            else:
                print(
                    "> Waiting for new mails.. currently "
                    + str(messageCount)
                    + " messages"
                    + ("." * pointCount)
                    + (" " * (totalPointCount - pointCount))
                    + "\r",
                    end="",
                    flush=True,
                )

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
        # [{"read":false,"expanded":false,"forwarded":false,"repliedTo":false,"sentDate":"2022-06-19T20:37:33.000+00:00","sentDateFormatted":"Jun 19, 2022, 8:37:33 PM","sender":"sender@mail.de","from":"[Ljavax.mail.internet.InternetAddress;@1dd3705c","subject":"Test-Mail","bodyPlainText":"\r\n\r\n\r\nDies ist eine Test-Mail - Yay.\r\n","bodyHtmlContent":"<html>\r\n  <head>\r\n\r\n    <meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\">\r\n  </head>\r\n  <body>\r\n    <p><br>\r\n    </p>\r\n  Dies ist eine Test-Mail - Yay.<br>\r\n    </div>\r\n</div>\r\n  </body>\r\n</html>\r\n","bodyPreview":"\r\n\r\n\r\n-------- Forwarded Message --------\r\nSubject","id":"10123386541204271300"}]
        return json.loads(message)

    def showMessage(self, json):
        mailText = json[0]["bodyPlainText"]

        if mailText == None:
            mailText = json[0]["bodyHtmlContent"]

        return (
            "Sender: "
            + json[0]["sender"]
            + "\nSubject: "
            + json[0]["subject"]
            + "\nMessage: "
            + mailText
            + "\n"
        )

    def renewInterval(self):
        """requests another 10 minutes to keep the mail address active"""

        print("Sending renewal request..")
        return self.doApiRequest(ENDPOINT_RESETINTERVAL, True)

    def doApiRequest(self, apiEndpoint: str, printOkay: bool = False):
        req = urllib.request.Request(
            BASE_URI + apiEndpoint, headers=FAKE_REQUEST_HEADERS
        )
        req.add_header("Accept", "application/json, text/javascript, */*")
        req.add_header("Connection", "keep-alive")

        if self.SIDCookie != "":
            req.add_header("cookie", self.SIDCookie)

        with urllib.request.urlopen(req) as response:
            message = response.read().decode("utf-8")

        if printOkay and response.getcode() == 200:
            print("> Request successful!")

        if response.getcode() >= 400:
            print("> Something went wrong!")

        return message


if __name__ == "__main__":

    awaitContinueRequest("generate a mail address")
    Tenmmg = TenMinuteMailGenerator()

    print("> Generating mail.. ")
    print("> Generated mail: " + Tenmmg.get10MinuteMail())

    messageId = 0
    while True:
        print(
            "\n"
            + "> Do you want to watch for new messages? Your choices: \n"
            + "> [Y]es (json raw output) \n"
            + "> [N]o (Ends script) \n"
            + "> Yes but show me extracted sender, subject and [B]ody (plaintext version if available, otherwise html) \n",
        )
        option = input("> Your choice [Y, N, B]: ")

        if option.lower().startswith("y"):
            print(Tenmmg.getMessage(Tenmmg.anyNewMessage(messageId) - 1))
        elif option.lower().startswith("b"):
            print(
                Tenmmg.showMessage(
                    Tenmmg.getMessage(Tenmmg.anyNewMessage(messageId) - 1)
                )
            )
        else:
            break

        messageId += 1
