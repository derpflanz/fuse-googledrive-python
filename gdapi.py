from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import io
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

# this googledriveapi module does all the Google Drive
# communications

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
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

    return build('drive', 'v3', credentials=creds)




def get_file(service, id, destination = None):
    request = service.files().get_media(fileId=id)

    if destination == None:
        fh = io.BytesIO()
    else:
        fh = io.FileIO(destination, mode = 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download {}.".format(int(status.progress() * 100)))

    if destination == None:
        return fh.getvalue()
    else:
        fh.close()
        return None

# https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html
def get_files(service, pagesize = 100, parent = None):
    # Call the Drive v3 API
    # myDrive parent ID = 0ADZoyBWeSfDNUk9PVA
    # https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html#get

    if parent is not None:
        qry=f"'{parent}' in parents and trashed=false"
    else:
        qry = None

    results = service.files().list(
        pageSize=pagesize, 
        q=qry,
        fields="nextPageToken, files(id, name, size, kind, parents, spaces, driveId, mimeType, createdTime, viewedByMeTime, modifiedByMeTime)").execute()
    return results.get('files', [])

def get_fileinfo(service, filename):
    filename = filename.replace("'", "\\'")
    results = service.files().list(
        pageSize=1, q=f"name = '{filename}'", fields="nextPageToken, files(id, name, size, kind)", orderBy='name', spaces="drive", corpus="user").execute()
    fi = results.get('files', [])
    if len(fi) == 1:
        fi = fi[0]
    else:
        fi = {}

    return fi

# can be used for debugging, single shot tests, etc.
def main():
    service = get_drive_service()
    items = get_files(service, 100)


    if not items:
        print('No files found.')
    else:
        for item in items:
#            print(u'{0} ({1})'.format(item['name'], item['id']))
#            content = service.files().get(fileId=item['id']).execute()
#            fi = get_fileinfo(service, item['name'])
            print(item)

        print(f'Found {len(items)} files.')

if __name__ == '__main__':
    main()