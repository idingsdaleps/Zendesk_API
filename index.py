creds = {
    'email' : 'idingsdale@postscript.co.uk',
    'token' : 'uLo4Cg0JilT83of8JotroT3Cu8zDP7qLjk0B7vE7',
    'subdomain': 'postscriptbookssupport'
}


# Import the Zenpy Class
from zenpy import Zenpy
import datetime
import time
from flask import Flask, request
app = Flask(__name__)

# Default
zenpy_client = Zenpy(**creds)


founduser = ""
founduseremail = ""
newuser = ""


def searchById(customerId):
    print("Searching for Netsuite ID " + str(customerId))
    userid = ""
    for user in zenpy_client.search(type='user', ns_externalid=customerId):
        userid = user.id
    if not userid:
        print("No result for ID search")
    else:
        global founduser 
        founduser = user
        print(str(founduser.id) + " found by ID")


def searchByEmail(customerEmail, customerNsId):
    userid = ""
    for user in zenpy_client.search(type='user', email=customerEmail):
        userid = user.id
    if not userid:
        print("No result for email search")
    else:
        global founduseremail 
        founduseremail = user
        print(str(founduseremail.id) + " found by email")
        user = zenpy_client.users(id=founduseremail.id)
        user.user_fields.update(dict(ns_externalid=customerNsId))
        print('Adding NS ID to Customer')
        zenpy_client.users.update(user)


def createUser(customerName, customerEmail, customerNsId):
    from zenpy.lib.api_objects import User
    uf = {"ns_externalid" : str(customerNsId)}
    user = User(name=customerName, email=customerEmail, user_fields=uf)
    created_user = zenpy_client.users.create(user)
    print("User ID " + str(created_user.id) + " created")
    global newuser
    newuser = created_user



def createTicket(userid, ticketbody, ticketsubject):
    from zenpy.lib.api_objects import Ticket, User, Comment
    zenpy_client.tickets.create(
    Ticket(subject=ticketsubject,requester_id=userid.id,comment=Comment(body=ticketbody, public=False))
)



def searchAndCreate(email, nsID, name, body, subject):

    searchById(nsID)
    if founduser:
        ticketuserId = founduser
    if not founduser and email:
        searchByEmail(email, nsID)
    if founduseremail:
        ticketuserId = founduseremail
    if not founduseremail and not founduser:
        print("No results, creating user")
        createUser(name, email, nsID)
        ticketuserId = newuser
    time.sleep(2.5)
    print ("Creating ticket with ID " + str(ticketuserId.id))
    createTicket(ticketuserId, body, subject)
    return 'Success!'

@app.route('/zendesk', methods=['GET', 'POST'])
def zendesk_route():
   if request.method == 'GET':
       return 'Zendesk API Running'
   elif request.method == "POST":
    content = request.json
    return searchAndCreate(content['email'],content['nsID'],content['name'],content['body'],content['subject'])




if __name__ == "__main__":
    app.run(host='0.0.0.0')
