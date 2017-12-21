import os
import sys
import shutil

from RFIDException import RFIDException
from pirc522 import RFID

rdr = RFID(dev='/dev/spidev1.0', pin_rst=37)

def main():


    print('Emmamusic - New Music Import')
    new_music_path = os.path.abspath('/home/pi/newmusic')
    process_singles(os.path.join(new_music_path, 'Singles'), os.path.join(new_music_path, 'Images'))
    process_albums(os.path.join(new_music_path,'Albums'), os.path.join(new_music_path,'Images'))

    rdr.cleanup()

    os.system("mpc update")


def process_singles(music_path, image_path):
    singles_dest = os.path.abspath('/home/pi/music/Singles')
    playlist_path = os.path.abspath('/home/pi/playlists')
    image_dest= os.path.abspath('/home/pi/music/images')

    path_items = os.listdir(music_path)

    for item in path_items:
        full_item = os.path.join(music_path, item)
        print('processing {}'.format(item))
        if os.path.isfile(full_item):
            try:
                print('RFID for {}'.format(full_item))
                id = get_rfid()
                print('RFID: {}'.format(id))
                imagefile = get_imagefile(image_path)

                create_m3u(os.path.join(playlist_path, id + '.m3u'),full_item)

                shutil.move(full_item,singles_dest)
                shutil.move(imagefile,os.path.join(image_dest,id+'.png'))

                update_index(id, item)

            except RFIDException as ex:
                print('RFID Error: {}'.format(ex))
                continue

            except Exception as ex:
                print('Error: {}'.format(ex))
                rdr.cleanup()
                sys.exit(1)


def process_albums(music_path, image_path):
    albums_dest = os.path.abspath('/home/pi/music/')
    playlist_path = os.path.abspath('/home/pi/playlists')
    image_dest= os.path.abspath('/home/pi/music/images')

    path_items = os.listdir(music_path)

    for item in path_items:
        full_item = os.path.join(music_path, item)
        print('processing {}'.format(item))
        if os.path.isdir(full_item):
            try:
                print('RFID for {}'.format(full_item))
                id = get_rfid()
                print('RFID: {}'.format(id))

                imagefile=get_imagefile(image_path)
                create_m3u(os.path.join(playlist_path, id + '.m3u'),full_item)
                shutil.move(imagefile, os.path.join(image_dest, id + '.png'))
                shutil.move(full_item,albums_dest)

                update_index(id, item)

            except RFIDException as ex:
                print('RFID Error: {}'.format(ex))
                continue

            except Exception as ex:
                print('Error: {}'.format(ex))
                rdr.cleanup()
                sys.exit(1)

def create_m3u(m3u_filename, file_or_path):
    with open(m3u_filename, "w") as f:
        if os.path.isfile(file_or_path):
            f.write(os.path.join('Singles', os.path.basename(file_or_path)+'\n'))
        else:
            for file in sorted(os.listdir(file_or_path)):
                if os.path.isfile(os.path.join(file_or_path,file)):
                    f.write(os.path.join(os.path.basename(file_or_path), file + '\n'))

def get_imagefile(image_path):
    filename = raw_input('Enter Image Filename (without path):')
    imagefile = os.path.join(image_path, filename)
    while not (os.path.exists(imagefile) and os.path.isfile(imagefile)):
        filename = raw_input('Enter Image Filename (without path):')
        imagefile = os.path.join(image_path, filename)
    return imagefile

def update_index(id, filename):
    with open (os.path.abspath('/home/pi/music/index.txt'),'a+') as f:
        f.write(id+': '+filename+'\n')

def get_rfid():
    retry = 0

    while retry < 20:
        (error, data) = rdr.request()
        if error:
            continue

        (error, uid) = rdr.anticoll()
        if error:
            raise RFIDException('Anticol Error')
        else:
            return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])

        retry += 1

        time.sleep(1)

    raise RFIDException('Timeout')


def process_file(file):
    pass


if __name__ == '__main__':
    main()
