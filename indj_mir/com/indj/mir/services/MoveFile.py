import shutil
import time
import os


def move_file():
    base = '/opt/utorrent-server-alpha-v3_3'
    destination = '/mnt/V1/torrent_download'
    for folder in os.listdir(base):
        print(folder)
        #for file_name in glob.glob(r'''%s\%s\*.mp3''' % (base, folder)):
        try:
            for file_name in os.listdir('%s/%s' % (base, folder)):
                if 'mp3' in file_name:
                    print(file_name)
                    file_name_store = time.time()
                    shutil.move('%s/%s/%s' % (base, folder, file_name), '%s/%s.mp3' % (destination, str(file_name_store).replace('.','')))
                else:
                    try:
                        for file_name1 in os.listdir('%s/%s/%s' % (base, folder, file_name)):
                            if 'mp3' in file_name1:
                                print(file_name1)
                                file_name1_store = time.time()
                                shutil.move('%s/%s/%s/%s' % (base, folder, file_name, file_name1), '%s/%s.mp3' % (destination, str(file_name1_store).replace('.','')))
                            else:
                                try:
                                    for file_name2 in os.listdir('%s/%s/%s/%s' % (base, folder, file_name, file_name1)):
                                        if 'mp3' in file_name2:
                                            print(file_name2)
                                            file_name2_store = time.time()
                                            shutil.move('%s/%s/%s/%s/%s' % (base, folder, file_name, file_name1, file_name2),
                                                        '%s/%s.mp3' % (destination, str(file_name2_store).replace('.', '')))
                                except Exception as ex:
                                    print(file_name)
                                    print(ex)
                    except Exception as ex:
                        print(file_name)
                        print(ex)
        except Exception as ex:
            print(file_name)
            print(ex)

if __name__ == "__main__":
    move_file()