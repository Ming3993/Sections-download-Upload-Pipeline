import requests
import os

def find_first_mp4(directory="."):
    for filename in os.listdir(directory):
        if filename.lower().endswith(".mp4"):
            return os.path.join(directory, filename)
    return None

def upload_file(item_id, access_token):
    file_name = find_first_mp4()
    if file_name != None:
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}:/{file_name}:/createUploadSession"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, headers=headers, json={})
        resp.raise_for_status()
        upload_url = resp.json()["uploadUrl"]
        
        chunk_size = 5 * 1024 * 1024  # 5MB
        file_size = os.path.getsize(file_name)
        with open(file_name, "rb") as f:
            start = 0
            chunk_num = 0
            while start < file_size:
                end = min(start + chunk_size, file_size) - 1
                f.seek(start)
                chunk = f.read(end - start + 1)

                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}"
                }
                r = requests.put(upload_url, headers=headers, data=chunk)
                
                if r.status_code in (200, 201):
                    print(f"Uploaded last chunk successfully, status: {r.status_code}")
                    print("✅ Uploaded successfully!")
                    break
                elif r.status_code == 202:
                    print(f"Uploaded chunk {chunk_num+1}: bytes {start}-{end}")
                    start = end + 1
                    chunk_num += 1
                else:
                    print(f"Error uploading chunk: {r.status_code}, {r.text}")
                    return False
        # Close and delete the file
        f.close()
        os.remove(file_name)
        print(f"Deleted local file: {file_name}")
        return True