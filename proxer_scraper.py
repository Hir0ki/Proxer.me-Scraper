from selenium import webdriver 
import selenium
import os
import argparse 
import sys

parser = argparse.ArgumentParser(description='Script for downloading anime from proxer')

parser.add_argument('--user', type=str, 
                    help='Username for proxer.me')

parser.add_argument('--paswd', type=str,
                    help='Password for proxer.me')

parser.add_argument('--ser_id', type=int, 
                    help='serien id of the anime, can be found in the url')

parser.add_argument('--ser_name', type=str,
                    help='name of the anime')

parser.add_argument('--ser_type', type=str,
                    help='type of translation of anime options: engsub, engdub, gersub, gerdub')
                
parser.add_argument('--output_path', type=str,
                    help='output path for anime mp4')

parser.add_argument('--start_ep', type=int,
                    help='from episode number x')

parser.add_argument('--end_ep', type=int,
                    help='to episode number x')


def validate_inputarguments(parser: argparse.ArgumentParser):
    args = parser.parse_args()

    if args.start_ep != None and args.end_ep != None:
        if args.start_ep > args.end_ep:
            print('please enter a start episode that is less then the end episode')
            sys.exit()

    if args.start_ep == None or args.end_ep == None:
        print('please enter a start episode and a end episode')
        sys.exit()
    
    if os.path.exists(args.output_path) == False:
        print(f"the path { args.output_path } is dosen't exist!")
        sys.exit()

    if args.ser_type == None:
        print('please enter a serien type!')
        sys.exit()

    possibal_ser_types = ('engsub', 'engdub', 'gersub', 'gerdub')

    ser_type_valid = True

    for possibility in possibal_ser_types:
        if args.ser_type == possibility: 
            ser_type_valid = False
            return args


    if ser_type_valid == True:  
        print('please enter a valid serien type option')
        sys.exit()


def wget_download(url, output_path):
    os.system(f"wget {url} -O { output_path}")

class Proxer():

    def __init__(self, base_url: str, username: str, password: str, serien_id: int,serien_name: str, serien_type: str, output_path:str ):
        self.driver = webdriver.Firefox()
        self.base_url = base_url
        self.serien_id = serien_id
        self.serien_type = serien_type 
        self.serien_name = serien_name
        self.output_path = output_path
        self.login(username, password)
        self.download_queue = []

    def login(self, username, password): 
        #gets base html site
        print("start login")
        self.driver.get(self.base_url)
        self.driver.find_element_by_id("loginNav").click()
        #sets username for login
        self.driver.find_element_by_id("mod_login_username").send_keys(username)
        #sets password for login
        self.driver.find_element_by_id("mod_login_password").send_keys(password)
        #subsmits form
        self.driver.find_element_by_id("mod_login_submit").click()
        print("done with login")


    def get_download_queue(self, from_episode: int, to_episode: int):
        try:
            next_episode = from_episode

            while next_episode <= to_episode:
                print(f"starting dowload episode: {next_episode}")
                self.driver.get(f"https://proxer.me/watch/{self.serien_id}/{next_episode}/{self.serien_type}")
                try:
                    video_page = self.driver.find_element_by_class_name("wStream").find_element_by_tag_name("iframe")
                    self.driver.get(video_page.get_attribute('src'))
                
                
                    self.download_queue.append([ f"{self.serien_name}_{next_episode}" , self.driver.find_element_by_tag_name("source").get_attribute("src") ])
                    
                    name = f"{self.serien_name}_{next_episode}"
                    url = self.driver.find_element_by_tag_name("source").get_attribute("src")
                    output_path = str(self.output_path)+"/"+str(name)+ ".mp4"
                    wget_download( url, output_path)
                except selenium.common.exceptions.NoSuchElementException:
                    print(f"error at {next_episode}")
                    if len(self.download_queue) > next_episode - 5:
                        return False
                next_episode += 1
        finally:
            self.driver.quit()
        return True

args = validate_inputarguments(parser)


p = Proxer("https://proxer.me/", username=args.user, password=args.paswd,
            serien_id=args.ser_id, serien_name=args.ser_name, serien_type=args.ser_type, output_path=args.output_path)

p.get_download_queue(from_episode=75,to_episode=168)
