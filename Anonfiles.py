# Made By : Zach without love
# Date : 2022-08-19
# Version : 1.0
# Description : This is an annonfiles api wrapper

import urllib.request
from tqdm import tqdm
from requests import Session
from bs4 import BeautifulSoup


class DownloadProgressBar(tqdm): # Progress bar for downloads
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class Anonfiles:
    def __init__(self, link:str=None) -> None:
        self.session = Session() # create session
        self.html_content = None # html content of anonfiles page
        # get code from link
         # validate code
        if link is None:
            return # no code found
        
        self.valid = self.validate()
        if self.valid is False:
            return None # code is not valid

        self.code = link.split("/")[-1] 
        pass
    
    
    def upload(self, file_path:str) -> dict: # upload file to anonfiles

        files = {'file': open(file_path, 'rb')}
        r = self.session.post("https://api.anonfiles.com/upload", files=files)
        if r.status_code == 200:
            return {"error":None, "link":r.json()["data"]["file"]["url"]["full"]} # return link to file
        else:
            return {"error":r.json()["error"]} # return error while uploading file

    def download_files(self, folder:str=None) -> dict: # download file from anonfiles to folder
        if self.valid is False:
            return
        files = self.get_files()["data"] # get file info
        for dl_info in files:

            self.download(dl_info, folder) # download file from anonfiles to folder
    
    def download(self, dl_info:dict, folder:str=None) -> dict:
        if self.valid is False:
            return
        url = dl_info["link"]

        if self.valid_link(url) is False:
            return {"error":"File fetch failed"} # file fetch failed

        if folder is None: # if folder is not specified then download to current directory
            folder = "."
        
        local_filename = folder.replace("/", "")+"/"+url.split('/')[-1] # get file name from url
        try:
            with DownloadProgressBar(unit='B', unit_scale=True,
                                        miniters=1, desc=url.split('/')[-1]) as t:
                    urllib.request.urlretrieve(url, filename=local_filename, reporthook=t.update_to) # download file  from url to local_filename with progress bar 

        except Exception as e:
            return {"error":str(e)}
        
        return {"error":None, "file":local_filename} # return file name

    def get_files(self): # returns file name and download links
        if self.valid is False:
            return
        if self.html_content is None: 
            return {"error":"No html_content"} # no html_content found
        
        soup = BeautifulSoup(self.html_content, "html.parser") # parse html_content
        file_name = soup.find("h1").text # get file name
        dl_infos = [] # list of download links

        a_elems = soup.find_all("a") # get all <a> elements
        for a in a_elems:
            dl_link = a.get("href") # get download link
            if len(a) > 0 and a != "":
                a = a.text.replace(" ", "").replace("\r", "").replace("\n", "")
                if "Download" in a: # check if download button is present
                    
                    a = a.replace("Download", "").replace(")", "") # remove download button text
                    if a.split("(")[0] == "":
                        dl_type = "Regular" # regular download
                    else:
                        dl_type = a.split("(")[0] # get download type
                
                    dl_size = a.split("(")[1] # get download size

                    dl_infos.append({ 
                        "name":file_name,
                        "type":dl_type, 
                        "size":dl_size, 
                        "link":dl_link.replace(" ","")
                        }
                    ) # append download link to list
        
        return {"error":None, "data":dl_infos} # return list of download links


    def valid_link(self, link:str) -> bool: # check if  file cdn link is valid or not
        if self.valid is False:
            return
        try:
            r = self.session.head(link, timeout=3)
        except Exception as e:
            return False
        
        if r.status_code == 200:
            return True # file cdn link is valid
        else:
            return False # file cdn link is not valid 

    def validate(self) -> bool: # check if anonfiles code is valid or not 
        r = self.session.get("https://anonfiles.com/"+self.code)
        
        status_code = r.status_code
        
        if status_code != 404: # if status code is not 404 then code is valid
            self.html_content = r.text # get html content
            return True # code is valid
        else:
            return False # code is not valid