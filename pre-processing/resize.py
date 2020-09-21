import os
from fnmatch import fnmatch
from multiprocessing import Pool
import random

import cv2
import tqdm

source_path = "/home/rik/nsfw_classifier/nsfw_data_scraper/source"
save_path = "/home/rik/apps/youtube/nsfw-classifier-demo/data/train/positive"

size = 306


def process_image(image_file):
    filename = image_file.split("/")[-1]
    global size
    try:
        oriimage = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
        if oriimage.shape[1] and oriimage.shape[0] >= 306:
            img = cv2.resize(oriimage, (size, size))
            cv2.imwrite(os.path.join(save_path, filename), img)
    except Exception as e:
        # print("Error : {}".format(str(e)))
        pass


if __name__ == "__main__":
    pattern = "*.jpg"
    image_files = []
    for path, subdirs, files in os.walk(source_path):
        for name in files:
            if fnmatch(name, pattern):
                image_files.append(os.path.join(path, name))
    sample = random.sample(image_files, 49000)
    print("1st file : {}".format(sample[0]))
    pool = Pool(processes=4)
    list(tqdm.tqdm(pool.imap(process_image, sample), total=len(sample)))
    pool.close()
    pool.join()
