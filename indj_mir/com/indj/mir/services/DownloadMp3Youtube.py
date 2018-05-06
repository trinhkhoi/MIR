import youtube_dl
import urllib
from bs4 import BeautifulSoup
from xlrd import open_workbook
from indj_mir.com.indj.mir.services.HandleAudioFile import upload_file
from django.conf import settings
import time


# pdalbumlist-playlist.xls
def download_all_mp3s(path, col_name = 5, col_artist = 7, co_name_stored = 0, start_row = 0):
    print('Start load excel file ------- ')
    wb = open_workbook(path)
    print('Load excel file successfully ------- ')
    for sheet in wb.sheets():
        number_of_rows = sheet.nrows
        for row in range(start_row, number_of_rows):
            file1 = open('link-youtube.csv', 'a')
            file2 = open('log-download-youtube.txt', 'a')
            file3 = open('error-download-youtube.txt', 'a')
            try:
                file2.write('\nRow order: %s' % row)
                textToSearch = '%s %s' % (sheet.cell(row, col_name).value, sheet.cell(row, col_artist).value)
                query = urllib.parse.quote(textToSearch)
                file2.write('\nquery: %s' % query)
                print('query: ', query)
                url = "https://www.youtube.com/results?search_query=" + query
                file_name = str(sheet.cell(row, co_name_stored).value).strip() + '.mp3'
                response = urllib.request.urlopen(url)
                html = response.read()
                soup = BeautifulSoup(html)

                for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
                    youtube_link = 'https://www.youtube.com' + vid['href']
                    file1.write('\n%s %s' % (file_name, youtube_link))
                    file2.write('\n%s %s' % (file_name, youtube_link))
                    print('%s %s' % (file_name, youtube_link))
                    try:
                        download_youtube(youtube_link, file_name)
                        time.sleep(2)
                        upload_file('%s%s' % (settings.INPUT_PATH_MP3, file_name), '%s/%s' % (settings.PREFIX_YOUTUBE, file_name),
                                   settings.BUCKET_NAME)
                        time.sleep(2)
                    except Exception as ex:
                        print(str(ex))
                        print('Error: %s %s' % (file_name, youtube_link))
                        file3.write('\nError: %s %s' % (file_name, youtube_link))
                    break
            except Exception as ex:
                file2.write(str(ex))

            file1.close()
            file2.close()
            file3.close()


def download_mp3_by_text_search(text_search, file_name):
    print('query: ', text_search)
    query = urllib.parse.quote(text_search)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        youtube_link = 'https://www.youtube.com' + vid['href']
        print('%s %s' % (file_name, youtube_link))
        try:
            download_youtube(youtube_link, file_name)
            #time.sleep(2)
            #upload_file('%s%s' % (settings.INPUT_PATH_MP3, file_name), '%s/%s' % (settings.PREFIX, file_name),
            #            settings.BUCKET_TRAINING_DATA)
            #time.sleep(2)
        except Exception as ex:
            print(str(ex))
            print('Error: %s %s' % (file_name, youtube_link))
        break


def download_youtube(youtube_link, file_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'audio-quality': '0',
        'outtmpl': '%s%s' % (settings.INPUT_PATH_MP3, file_name)
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_link])
    print('Download mp3 from youtube successfully')


if __name__ == "__main__":
    download_all_mp3s()