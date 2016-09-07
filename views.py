# -*- coding: utf-8 -*-

import argparse
from flask import *
import os, sys
import json
import re
import sys

app = Flask(__name__)
app.secret_key = 'xxx'

IMAGE_ROOT = os.path.join('static', 'img')
IMAGE_PATTERN = re.compile('.*[.](jpg|jpeg|png|bmp|gif)$')
POSITIVE_FILE = 'positive.dat'
NEGATIVE_FILE = 'negative.dat'


def get_images(dir_name):
    dir_path = os.path.join(IMAGE_ROOT, dir_name)
    return [img for img in os.listdir(dir_path) if IMAGE_PATTERN.match(img)]


def parse_dat(datfile):
    parsed = []
    for l in datfile:
        row = l.strip().split('  ')
        parsed.append([
            row[0],
            int(row[1]),  # number of box
            [
                [int(_) for _ in r.split(' ')]
                for r in row[2:]
            ]
        ])
    return parsed

def parse_neg_dat(datfile):
    return [[l.strip()] for l in datfile]


def load_info(dir_name):
    pos_path = os.path.join(IMAGE_ROOT, dir_name, POSITIVE_FILE)
    neg_path = os.path.join(IMAGE_ROOT, dir_name, NEGATIVE_FILE)
    pos = parse_dat(open(pos_path)) if os.path.exists(pos_path) else []
    neg = parse_neg_dat(open(neg_path)) if os.path.exists(neg_path) else []
    return pos, neg


@app.route('/<path:img_dir>/')
def index(img_dir):
    images = get_images(img_dir)
    pos, neg = load_info(img_dir)
    processed_images = set([_[0] for _ in pos + neg])
    remained_images = [
        img for img in images
        if img not in processed_images
    ]
    print(remained_images)
    num_images = len(images)
    num_boxes = sum([_[1] for _ in pos]) if pos else 0

    if len(remained_images) == 0:
        return 'Finished! {} images, {} boxes'.format(num_images, num_boxes)

    img_path = os.path.join('..', IMAGE_ROOT, img_dir, remained_images[0])
    count = len(processed_images) + 1

    counter = '{}/{} ({})'.format(count, num_images, num_boxes)

    return render_template(
        'index.html',
        imgdir=img_dir,
        imgsrc=img_path,
        imgnum=num_images,
        count=count,
        counter=counter
    )


@app.route('/_next')
def _next():
    img_dir = request.args.get('imgdir')
    images = get_images(img_dir)
    pos, neg = load_info(img_dir)
    processed_images = set([_[0] for _ in pos + neg])
    print(processed_images)
    remained_images = [
        img for img in images
        if img not in processed_images
    ]
    print(remained_images)
    count = len(processed_images) + 1
    num_boxes = sum([_[1] for _ in pos]) if pos else 0
    img_file = remained_images[0]

    #その画像をスキップするか
    skip = request.args.get('skip')

    if skip == u'0':

        #囲まれた範囲の座標
        coords = request.args.get('coords')
        coords = json.loads(coords)

        #正例か負例か
        if len(coords) == 0:
            with open(os.path.join(IMAGE_ROOT, img_dir, NEGATIVE_FILE), 'a') as o_:
                o_.write('{}\n'.format(img_file))
        else:
            s = ''
            for coord in coords:
                s = '  '.join( [ s, ' '.join( [ str(int(e)) for e in coord])])

            with open(os.path.join(IMAGE_ROOT, img_dir, POSITIVE_FILE), 'a') as o_:
                o_.write('%s  %d%s\n' % (img_file, len(coords), s))
            num_boxes += len(coords)
    else:
        with open(os.path.join(IMAGE_ROOT, img_dir, NEGATIVE_FILE), 'a') as o_:
            o_.write('{}\n'.format(img_file))

    print('images: {}, count: {}, boxes: {}'.format(len(images), count, num_boxes))
    #まだ画像があるか
    if len(images) <= count:
        imgsrc = ''
        finished = True
    else:
        finished = False
        imgsrc = os.path.join('..', IMAGE_ROOT, img_dir, remained_images[1])

    return jsonify(imgsrc=imgsrc, finished=finished, count=count, numboxes=num_boxes)


def build_argparser():
    parser = argparse.ArgumentParser('TrainingAssistant')
    parser.add_argument(
        '--port',
        default=5000,
        help='port (default: 5000)'
    )
    parser.add_argument(
        '--ip',
        default='localhost',
        help='host (default: localhost)'
    )
    return parser

if __name__ == '__main__':
    argparser = build_argparser()
    args = argparser.parse_args(sys.argv[1:])

    app.debug = True
    app.run(host=args.ip, port=args.port)
