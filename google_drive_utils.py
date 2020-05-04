import io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Returns an authenticated pydrive object
def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("google_drive_credentials.txt")
    drive = GoogleDrive(gauth)
    return drive

# Upload a pandas df to a csv file in Google Drive
def upload_df_to_gd(file_name, df, folder_id):
    drive = authenticate_google_drive()
    stream = io.StringIO()
    df.to_csv(stream)
    file_to_upload = drive.CreateFile({'title': file_name, 'mimeType': 'text/csv',
                                       "parents": [{"kind": "drive#fileLink", "id": folder_id}]})
    file_to_upload.SetContentString(stream.getvalue())
    file_to_upload.Upload()

# Gets a df from a csv contained on Google Drive
def get_df_from_gd_csv(folder_id, file_name):
    drive = authenticate_google_drive()
    downloaded = drive.CreateFile({'id': folder_id})
    downloaded.GetContentFile(file_name)
    df = pd.read_csv(file_name)
    return df
