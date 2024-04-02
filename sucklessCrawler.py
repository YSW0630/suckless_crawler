# Python Version: 3.12.2
# Requests lib Version: 2.31.0
# BeautifulSoup lib Version: 4.12.3
# Autor: 盛wei

# This is my first crawler written in Python,  
# Purpose is to remind me to manually patch some of my suckless programs which have a new commit.
# todo: 1. put this file into bashrc/zshrc, when open the terminal it will start crawling
#       2. add a function which can try to merge a commit automatically

import os
import json
import requests 
from bs4 import BeautifulSoup

# open some cute suckless programs from json: 
with open('suckless_programs.json', 'r') as json_file:
    suckless_programs = json.load(json_file)

headers  = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36' } 

def AddCommitCode(program_name, Link):
    PatchLinkResponse = requests.get(f"https://git.suckless.org/{program_name}/{Link}", headers=headers)
    Div = BeautifulSoup(PatchLinkResponse.text, 'html.parser').find('div')
    # check the <div> element exsited or not
    if Div is not None:
        return Div.get_text()
    else:
        print("No <div> element found!")
        return ""

def Update(program_name, Tbody):
    Trs = Tbody.find_all("tr")
    CheckLatest = 0
    LatestDate  = ""
    print(f"Start fetching {program_name} from {suckless_programs[program_name][0]}......")
    for trs in Trs:
        td_lists = trs.find_all("td")
        Date = td_lists[0].text
        Link = td_lists[1].find('a')['href'] 
        if Date == suckless_programs[program_name][1]:
            if CheckLatest == 0:
                print(f"{program_name} has nothing to fetch!\n")
                break
            else:
                print(f"{program_name} fetching is complete!\n")
                break
        else:
            if CheckLatest == 0:
                CheckLatest = 1
                LatestDate = Date
            # Create a patch folder and put patches inside
            folder_name = f"{program_name}_patches"
            folder_path = os.path.join(".", folder_name)
            file_path = os.path.join(folder_path, f"{Link.replace('/', '_').replace('.html', '.diff')}")
            os.makedirs(folder_path, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(AddCommitCode(program_name, Link))
            print(f"Added: {Link.replace('.html', '.diff')} patch to {folder_name}")
    # update suckless_programs date to latest
    if (LatestDate != ""):
        suckless_programs[program_name][1] = LatestDate
        with open('suckless_programs.json', 'w') as json_file: 
            json.dump(suckless_programs, json_file, indent=4)

def main():
    for key, val in suckless_programs.items():
        Response = requests.get(val[0], headers=headers) 
        Tbody = BeautifulSoup(Response.text, "html.parser").find("tbody")
        if Response.status_code == requests.codes.ok:
            print(f"Success to get {key} connection")
            Update(key, Tbody)
        else:
            print(f"Failed to get {key} connection")

if __name__ == "__main__":
    main()
