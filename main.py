from __future__ import print_function
import pickle
import time
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

qstring = 'from: no-reply@m.mail.coursera.org'


def cred():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            return creds
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        return creds


def gsearch(service, qstring):
    final = []
    results = service.users().messages().list(userId='me', q=qstring).execute()
    if results['resultSizeEstimate'] > 0:
        final.extend(results['messages'])
        print(results)
    else:
        print("No results for query string: ", qstring)
    nextpagetoken = results.get('nextPageToken', None)
    x = 1
    while nextpagetoken:
        # pause after every 5 requests to stay under the free threshold
        if (x % 5) == 0:
            time.sleep(1)
        results = service.users().messages().list(userId='me', q=qstring, pageToken=nextpagetoken).execute()
        if results['resultSizeEstimate'] > 0:
            final.extend(results['messages'])
        nextpagetoken = results.get('nextPageToken', None)
        x += 1
    print(final)
    print(len(final))
    return final


def gtrash(service, del_list):
    # Since this is sequential and blocking, the code will not hit the API free threshold
    for i in del_list:
        result = service.users().messages().trash(userId='me', id=i['id']).execute()
        print(result)



def main():
    """Search and delete email based on quey string. """
    creds = cred()
    service = build('gmail', 'v1', credentials=creds)
    del_list = gsearch(service, qstring)
    gtrash(service, del_list)
    service.close()


if __name__ == '__main__':
    main()