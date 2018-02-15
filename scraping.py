from requests import get as resget
from bs4 import BeautifulSoup
import urllib.request, json

def main(url, downall=False):
    print('Loading page!')
    response = resget(url)
    if(response.status_code == 200):
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('enclosure')
        for link in links:
            url = link.get('url')
            filename = url.split('/')[-1]
            try:
                with open(filename, 'r') as f:
                    print('{} already exists.'.format(filename))
            except IOError:
                print('Current downloading file: {}'.format(filename))
                f = urllib.request.urlopen(url)
                data = f.read()
                with open(filename, "wb") as code:
                    code.write(data)
                    print(':: {} successfully downloaded!'.format(filename))
            if(not downall):
                break

if(__name__ == '__main__'):
    try:
        conf = json.load(open('config.json'))
        if(conf['url'] == '' or type(conf['url']) != str):
           raise(TypeError)
    except IOError:
        print('Oops, config.json not found.')
    except Exception:
        print('Oops, something went wrong.')
    else:
        main(conf['url'],conf['down_all_ep'])
    input('\nPress any key to continue!')
    

    





    

    




