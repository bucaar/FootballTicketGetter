import requests
import sys
import time
from lxml.html import fromstring, tostring

def main():
  print(time.time())
  
  sys.path.append('/home/aabuchho/config')
  from credentials import credentials

  for cred in credentials:
    getTicket(cred["u"], cred["p"])

def getTicket(username, password):
  print("Getting ticket for " + username)
  #create the session so we can log in and persist that data
  session = requests.session()

  #some base urls used throughout the script
  base_url = 'https://apps.ndsu.edu/footballtickets/'
  login_path = 'login.php'

  #get the login page so we can scrape the url and the form elements
  result = session.get(base_url + login_path)
  tree = fromstring(result.text)

  #scrape the input values in the form
  inputs = tree.xpath("//input")
  data = {x.name: x.value for x in inputs}

  #set my form data
  data["username"] = username
  data["password"] = password

  #post the form and collect the new page, it should be the ticket_status.php page now
  url = result.url
  result = session.post(url, data=data)
  tree = fromstring(result.text)
  if result.url == url:
    print("Incorrect credentials")
    return

  #gather the first row in the table for the games
  first_row = tree.xpath("//tr[2]")

  #if we have a result
  if(len(first_row)>0):
    #get the td elements in this row
    columns = first_row[0].xpath("td")

    #list of column text
    column_text = [''.join(columns[x].itertext()) for x in range(len(columns))]

    #if we have an action text
    if column_text[4]:
      #normalize the action text
      column_text[4] = column_text[4].lower()

      #try to get the link in the column
      links = columns[4].xpath("a")

      #if we have a link
      if(len(links)>0):
        #get the path of that link (contains the game id)
        link_path = links[0].get("href")

        #what type of action do we have
        if column_text[4] == "reserve ticket":
          #follow the link and get the results of that page (h2 element)
          result = session.get(base_url + link_path)
          tree = fromstring(result.text)
          result_text = ''.join(tree.xpath("//h2")[0].itertext())
          print(result_text + " for '" + column_text[0] + "'")
        elif column_text[4] == "return ticket":
          #we dont want this script to return the ticket ever. let that be the user's decision
          print("Already has reserved the ticket for game '" + column_text[0] + "'")
        else:
          #not sure what to do in this case?
          print("Unknown action '" + column_text[4] + "' for game '" + column_text[0] + "'")
      else:
        #no link in the last column
        print("No link for game '" + column_text[0] + "', action '" + column_text[4] + "'")
    else:
      #No action text probably means reservation is unavailable
      print(column_text[3] + " for game '" + column_text[0] + "'")
  else:
    #If there are no <tr> available
    print("No games available!")

if __name__ == "__main__":
  main()

