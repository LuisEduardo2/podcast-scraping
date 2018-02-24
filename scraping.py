from requests import get as resget
from bs4 import BeautifulSoup
from pyperclip import paste
from os import system, name as osname, mkdir
from tqdm import tqdm
import json

clear = lambda: system('cls') if osname == 'nt' else system('clear')

class PodcastScraping():
    def __init__(self, confdata):
        self.data = confdata

    def menu(self):
        while True:
            print('-------------------------------------')
            print(':  0 - Sair                         :')
            print(':  1 - Cadastrar novo podcast       :')
            print(':  2 - Listar podcasts Cadastrados  :')
            print(':  3 - Baixar Episodio(s)           :')
            print('-------------------------------------')
            while True:
                try:
                    option = int(input('Digite uma opção: '))
                    if(option < 0 or option > 3):
                        raise(TypeError)
                except TypeError:
                    print('Opção invalida.')
                except ValueError:
                    print('O codigo inserido não e valido!')
                else:
                    break
            if(option == 0):
                break
            clear()
            if(option == 1):
                self.Register()
            if(option == 2):
                self.List()
            if(option == 3):
                self.PodcastDownload()

    def Register(self):
        print("OBS: Para colar um conteudo da area de transferencia, digite 'paste' sem aspas!")
        print(':-+.. Cadastrar novo Podcast ..+-:')
        key = (str(input('Insira o nome do podcast: '))).replace(' ','_')
        if(key=='paste'): key=paste()
        url = str(input('Insira a url do feed rss: '))
        if(url=='paste'): url=paste()

        print('Nome: {} - Url: {}'.format(key,url))

        self.data['values'].append( [key, url] )
        json.dumps(self.data,indent=2)
        with open('config.json','w') as file:
            file.write(json.dumps(self.data,indent=2))
                
    def List(self):
        print(':-+.. PodCasts Cadastrados ..+-:')
        [print(' {} - {}'.format(index,values[0])) for index,values in enumerate(self.data['values'])]
    
    def PodcastDownload(self):
        print(':-+.. Donwload de Episodios ..+-:')
        [print(' {} - {}'.format(index,values[0])) for index,values in enumerate(self.data['values'])]
        try:
            code = int(input('Escolha um podcast: '))
            if(code < 0 or code >= len(self.data['values'])):
                raise(TypeError)
        except (TypeError,ValueError):
            print('Codigo invalido!')
        else:
            podname, url = self.data['values'][code]
            self.__DownloadEpisode(podname, url)

    def __DownloadFile(self,url,filename,podname):
        try:
            with open('podcasts/'+podname+'/'+filename, 'r') as f:
                print('{} already exists.'.format(filename))
        except IOError:
            print('Current downloading file: {}'.format(filename))
            r = resget(url, stream=True)
            filesize = int(r.headers['content-length']) / 1024
            with open('podcasts/'+podname+'/'+filename, 'wb') as f:
                for data in tqdm(iterable = r.iter_content(1024),total=filesize,unit='KB',unit_scale=True):
                    f.write(data)
            print(':: {} successfully downloaded'.format(filename))

    def __DownloadEpisode(self,podname,podurl):
        try:
            response = resget(podurl)
        except Exception:
            print('Ocorreu um erro ao conectar a url cadastrada, tente novamente mais tarde!')
        else:
            if(response.status_code == 200):
                print('Recuperando Lista de Episodios.')
                soup = BeautifulSoup(response.content, 'html.parser')
                links = []
                for link in reversed(soup.find_all('enclosure')):
                    url = link.get('url')
                    filename = ((url.split('/')[-1]).split('.mp3'))[0] + '.mp3'
                    links.append( [url,filename] )

                if(len(links) == 0):
                    print('Não foi encontrado nenhum episodio.')
                else:
                    [print(' {}  -  {}'.format(index,episodes[1])) for index,episodes in enumerate(links)]
                    try:
                        selected = str(input("Digite 'all' para baixar todos os episodios ou insira os codigos dos episodios que deseja baixar \nseparado por um '-': "))
                        if(selected == ''):
                            raise(ValueError)
                        try:
                            mkdir('podcasts/'+podname)
                        except FileExistsError:
                            pass
                        if(selected == 'all'):
                            for url,filename in links:
                                try:
                                    self.__DownloadFile(url,filename,podname)
                                except ValueError:
                                    print("Podcast de nome '{}' não encontrado".format(filename))
                            print('Episodios Baixados com sucesso!')
                        else:
                            selected = [int(i) for i in selected.split('-')]
                            for i in selected:
                                try:
                                    url,filename = links[i]
                                    self.__DownloadFile(url,filename,podname)
                                except(TypeError,ValueError,IndexError):
                                    print('Podcast de código {} não encontrado'.format(i))
                    except ValueError:
                        print('Codigo Invalido. Retornando ao menu!')


def main():
    try:
        confdata = json.load(open('config.json'))
    except FileNotFoundError:
        confdata = {}
        confdata['values'] = []
    finally:
        try: 
            mkdir('podcasts')
        except FileExistsError:
            pass
        PodcastScraping(confdata).menu()
    input('\nPress any key to continue!')

if(__name__ == '__main__'):
    main()
