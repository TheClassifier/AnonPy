from Anonfiles import Anonfiles

url = "https://anonfiles.com/g0Xcfbf8b9"

a = Anonfiles(url) # initialize anonfiles class

upload = a.upload("test.py") # upload file to anonfiles
print(upload)

files = a.get_files()["data"] # get file info
print(files)

for dl_info in files: # download files from anonfiles to folder
    print(dl_info)
    a.download(dl_info, ".")

