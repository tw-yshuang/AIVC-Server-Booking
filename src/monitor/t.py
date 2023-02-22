import os

user_ids = ["B10930010", "B10930011", "B10930012"]
for user_id in user_ids:
    os.system(f"sudo docker run --name {user_id} ubuntu")
