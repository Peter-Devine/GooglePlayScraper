from google_drive_utils import upload_df_to_gd, get_df_from_gd_csv, authenticate_google_drive
import os


drive = authenticate_google_drive()

file_list = drive.ListFile({'q': "'1h2lBOSqLvzSoa5ZJ8bdrCNzqBKa823YP' in parents and trashed=false"}).GetList()

file_names = [(file.attr["metadata"]["title"], file["id"]) for file in file_list]

overall_df = None

for file_name, file_id in file_names:
    print(file_name)
    try:
        app_df = get_df_from_gd_csv(file_id, file_name)
    except Exception as err:
        print(f"Failed by giving {err}")
        continue

    if overall_df is None:
        overall_df = app_df
    else:
        overall_df = overall_df.append(app_df)

upload_df_to_gd("overall_app_data.csv", overall_df, "1M8Mjk_vIVFtnFflcr60y7jD8UadMc5uk")
