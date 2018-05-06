import requests
import base64
import json
from lxml import html
import os
import glob
import sys

class UTorrentAPI(object):

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth     = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.token, self.cookies  = self._get_token()

    def _get_token(self):
        url = self.base_url + '/token.html'

        token    = -1
        cookies  = -1

        try:
            response = requests.get(url, auth=self.auth)

            token = -1

            if response.status_code == 200:
                xtree = html.fromstring(response.content)
                token = xtree.xpath('//*[@id="token"]/text()')[0]
                guid  = response.cookies['GUID']
            else:
                token = -1

            cookies = dict(GUID = guid)

        except requests.ConnectionError as error:
            token = 0
            cookies = 0
            print(error)
        except:
            print('error')

        return token, cookies

    def is_online(self):
        if self.token != -1 and self.token != 0:
            return True
        else:
            return False

# public sectin -->
    def get_list(self):
        torrents = []
        try:
            status, response = self._action('list=1')
            if status == 200:
                torrents = response.json()
            else:
                print(response.status_code)

        except requests.ConnectionError as error:
            print(error)
        except Exception as ex:
            print(str(ex))

        return torrents

    def get_files(self, torrentid):
        path = 'action=getfiles&hash=%s' % (torrentid)
        status, response = self._action(path)

        files = []

        if status == 200:
            files = response.json()
        else:
            print(response.status_code)

        return files

    def start(self, torrentid):
        return self._torrentaction('start', torrentid)

    def stop(self, torrentid):
        return self._torrentaction('stop', torrentid)

    def pause(self, torrentid):
        return self._torrentaction('pause', torrentid)

    def forcestart(self, torrentid):
        return self._torrentaction('forcestart', torrentid)

    def unpause(self, torrentid):
        return self._torrentaction('unpause', torrentid)

    def recheck(self, torrentid):
        return self._torrentaction('recheck', torrentid)

    def remove(self, torrentid):
        return self._torrentaction('remove', torrentid)

    def removedata(self, torrentid):
        return self._torrentaction('removedata', torrentid)

    def recheck(self, torrentid):
        return self._torrentaction('recheck', torrentid)

    def set_priority(self, torrentid, fileindex, priority):
        # 0 = Don't Download
        # 1 = Low Priority
        # 2 = Normal Priority
        # 3 = High Priority
        path = 'action=%s&hash=%s&p=%s&f=%s' % ('setprio', torrentid, priority, fileindex)
        status, response = self._action(path)

        files = []

        if status == 200:
            files = response.json()
        else:
            print(response.status_code)

        return files

    def add_file(self, file_path):

        file = []

        url = '%s/?%s&token=%s' % (self.base_url, 'action=add-file', self.token)
        headers = {
        'Content-Type': "multipart/form-data"
        }

        files = {'torrent_file': open(file_path, 'rb')}

        try:
            if files:
                response = requests.post(url, files=files, auth=self.auth, cookies=self.cookies)
                if response.status_code == 200:
                    file = response.json()
                    print('file added')
                else:
                    print(response.status_code)
            else:
                print('file not found')

            pass
        except requests.ConnectionError as error:
            print(error)
        except Exception as e:
            print(e)

        return file

    def add_url(self, fiel_path):
        path = 'action=add-url&s=%s' % (fiel_path)
        status, response = self._action(path)

        files = []

        try:
            if status == 200:
                files = response.json()
            else:
                print(response.status_code)

            pass
        except requests.ConnectionError as error:
            print(error)
        except Exception as e:
            print(e)

        print(files)

        return files


# private section -->
    def _torrentaction(self, action, torrentid):
        path = 'action=%s&hash=%s' % (action, torrentid)

        files = []

        try:
            status, response = self._action(path)

            if status == 200:
                files = response.json()
            else:
                print(response.status_code)

        except requests.ConnectionError as error:
            print(error)
        except:
            print('error')

        return files

    def _action(self, path):
        url = '%s/?%s&token=%s' % (self.base_url, path, self.token)
        headers = {
        'Content-Type': "application/json"
        }
        try:
            response = requests.get(url, auth=self.auth, cookies=self.cookies, headers=headers)
        except requests.ConnectionError as error:
            print(error)
        except Exception as ex:
            print(str(ex))
            pass

        return response.status_code, response


def add_torrent_link(path):
    apiclient = UTorrentAPI('http://localhost:8080/gui', 'admin', '123456')
    apiclient.removedata('07E04940A37053FDC4A4096AF5CFF769AE6CBB8D')
    apiclient.removedata('088F490FD47D6A119A9C877515DBC5EE4AE36BCF')
    apiclient.removedata('0BF7F30F1FB8188F610C004D4854713FA87442D8')
    apiclient.removedata('170DFDCDE731CC3BC80B62AE3D176FCA827C09F1')
    apiclient.removedata('38815968E82E5850CF529B4A6233A908A8E4BA17')
    apiclient.removedata('3C6BB04F11910EC51F484B420E1900996144F812')
    apiclient.removedata('5B9552657705912186347E971D313EF1423D5989')
    
    '''
    for file_name in glob.glob('%s/*.torrent' % path)[:5]:
        print(file_name)
        file = apiclient.add_file(file_name)
        remove_file(file_name)
    '''
    file = apiclient.add_url('magnet:?xt=urn:btih:0157E33812D4F506B786A723807336F6859522B3&dn=K-pop+music+2157+Korean+pop+songs&tr=udp://9.rarbg.com:2710/announce&tr=udp://tracker.zer0day.to:1337/announce&tr=http://explodie.org:6969/announce&tr=udp://tracker.leechers-paradise.org:6969/announce&tr=udp://p4p.arenabg.com:1337/announce&tr=http://mgtracker.org:6969/announce&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=http://37.19.5.139:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce')

    list_torrent_ids = apiclient.get_list()
    print('==== List file add: ', json.dumps(list_torrent_ids, indent=1, ensure_ascii=False).encode('utf8'))

    #results = apiclient.recheck('07E04940A37053FDC4A4096AF5CFF769AE6CBB8D')
    #print('results: ', results)
    #file1 = apiclient.start('07E04940A37053FDC4A4096AF5CFF769AE6CBB8D')
    #print('results1: ', file1)
    #file2 = apiclient.start('088F490FD47D6A119A9C877515DBC5EE4AE36BCF')
    #print('results2: ', file2)

    #for file_name in os.listdir('/mnt/V1/torrent_raw'):
    #    file = apiclient.add_file('/home/trinhkhoi/Downloads/torrent_raw/%s' % file_name)
    #apiclient.remove('EE7569EA381602193AA5EDD11256EBA682B6AA59')
    #status_code, response = apiclient.add_url('magnet:?xt=urn:btih:74f72538ac932f2fe4975c96fc26baec030b226e&dn=52nd%20Street%20Swing.%20New%20York%20in%20the%2030%27s&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.to%3a2710%2fannounce&tr=udp%3a%2f%2ftracker.internetwarriors.net%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.skyts.net%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.safe.moe%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.piratepublic.com%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fwambo.club%3a1337%2fannounce&tr=udp%3a%2f%2ftrackerxyz.tk%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.xku.tv%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.vanitycore.co%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.uw0.xyz%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.tvunderground.org.ru%3a3218%2fannounce&tr=udp%3a%2f%2ftracker.swateam.org.uk%3a2710%2fannounce&tr=udp%3a%2f%2ftracker.kamigami.org%3a2710%2fannounce&tr=udp%3a%2f%2ftracker.halfchub.club%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.grepler.com%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.files.fm%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.dutchtracking.com%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.dler.org%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.desu.sh%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.cypherpunks.ru%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.cyberia.is%3a6969%2fannounce&tr=udp%3a%2f%2ftc.animereactor.ru%3a8082%2fannounce&tr=udp%3a%2f%2fsd-95.allfon.net%3a2710%2fannounce&tr=udp%3a%2f%2fsantost12.xyz%3a6969%2fannounce&tr=udp%3a%2f%2fsandrotracker.biz%3a1337%2fannounce&tr=udp%3a%2f%2fretracker.nts.su%3a2710%2fannounce&tr=udp%3a%2f%2fretracker.lanta-net.ru%3a2710%2fannounce&tr=udp%3a%2f%2fretracker.coltel.ru%3a2710%2fannounce&tr=udp%3a%2f%2fmgtracker.org%3a6969%2fannounce&tr=udp%3a%2f%2fipv4.tracker.harry.lu%3a80%2fannounce&tr=udp%3a%2f%2finferno.demonoid.pw%3a3418%2fannounce&tr=udp%3a%2f%2fallesanddro.de%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.justseed.it%3a1337%2fannounce&tr=udp%3a%2f%2fpackages.crunchbangplusplus.org%3a6969%2fannounce&tr=udp%3a%2f%2fexplodie.org%3a6969%2fannounce&tr=udp%3a%2f%2fbt.xxx-tracker.com%3a2710%2fannounce&tr=udp%3a%2f%2fbt.aoeex.com%3a8000%2fannounce&tr=udp%3a%2f%2f104.238.198.186%3a8000%2fannounce&tr=udp%3a%2f%2finferno.demonoid.pw%3a3391%2fannounce&tr=http%3a%2f%2fmgtracker.org%3a2710%2fannounce&tr=http%3a%2f%2ftracker.kamigami.org%3a2710%2fannounce&tr=http%3a%2f%2ftracker.mg64.net%3a6881%2fannounce&tr=http%3a%2f%2ftracker2.wasabii.com.tw%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.me%3a2720%2fannounce&tr=udp%3a%2f%2fopentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fwww.eddie4.nl%3a6969%2fannounce&tr=udp%3a%2f%2fzer0day.to%3a1337%2fannounce&tr=udp%3a%2f%2ftracker1.wasabii.com.tw%3a6969%2fannounce&tr=udp%3a%2f%2f185.50.198.188%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969&tr=udp%3a%2f%2ftracker2.indowebster.com%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969&tr=http%3a%2f%2fbt.ttk.artvid.ru%3a6969%2fannounce&tr=http%3a%2f%2fbt.artvid.ru%3a6969%2fannounce&tr=udp%3a%2f%2fthetracker.org.%2fannounce&tr=udp%3a%2f%2ftracker4.piratux.com%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.zer0day.to%3a1337%2fannounce&tr=udp%3a%2f%2f62.212.85.66%3a2710%2fannounce&tr=udp%3a%2f%2feddie4.nl%3a6969%2fannounce&tr=udp%3a%2f%2fpublic.popcorn-tracker.org%3a6969%2fannounce&tr=http%3a%2f%2ftracker.dler.org%3a6969%2fannounce&tr=http%3a%2f%2ftracker.tiny-vps.com%3a6969%2fannounce&tr=http%3a%2f%2ftracker.filetracker.pl%3a8089%2fannounce&tr=http%3a%2f%2ftracker.tvunderground.org.ru%3a3218%2fannounce&tr=http%3a%2f%2ftracker.grepler.com%3a6969%2fannounce&tr=http%3a%2f%2ftracker.kuroy.me%3a5944%2fannounce&tr=http%3a%2f%2f210.244.71.26%3a6969%2fannounce&tr=http%3a%2f%2ffrom_torrentkim.net')
    #file = apiclient.add_file('/data/155522.torrent')
    #file = apiclient.add_file('/data/52nd+Street+Swing.+New+York+in+the+30%27s.torrent')
    #print('status_code: ', status_code)
    #print('response: ', response)

    #files = apiclient.get_files('EE7569EA381602193AA5EDD11256EBA682B6AA59')
    #print(files)

def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


def rename_downloaded_folder():
    base = '/root/'
    print('older folders: ', os.listdir(base))
    for index, old_name in enumerate(os.listdir(base)):
        # [::-1] is slice notation for "reverse"
        os.rename(os.path.join(base, old_name),
                  os.path.join(base, str(index)))

    print('new folders: ', os.listdir(base))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'rename':
            rename_downloaded_folder()
        else:
            add_torrent_link(sys.argv[1])
    else:
        add_torrent_link('/mnt/V1/torrent_raw')
