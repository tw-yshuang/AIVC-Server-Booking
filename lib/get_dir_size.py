import os

# def get_dir_size(folder_path, full_size = 0): 
#     for parent, dirs, files in os.walk(folder_path):
#         full_size = sum(os.path.getsize(os.path.join(parent, file)) for file in files)
#     return full_size

# def get_dir_size(path, size = 0):
#     dir_list = os.listdir(path)
#     for file in dir_list:
#         f = os.path.join(path, file)
#         if os.path.isfile(f):
#             size += (os.path.getsize(f))
#         else:
#             size = get_dir_size(f, size)
#     return size

def get_dir_size(path, size: float = 0.0):
    for root, dirs, files in os.walk(path):
        for f in files:
            size+=os.path.getsize(os.path.join(root, f))
        # print(size)      
    return size
# print(get_dir_size("/home/tdd/Downloads"))