#!../env/bin/python3
import pandas
from PIL import Image
from random import randint
from random import uniform

__license__ = """
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""
__author__ = 'Daniel Ward'
__version__ = '1.0'
__copyright__ = 'GPL 3'

MAX_DOMAIN = 0.34
MAX_WALKERS = 5
SPAWN_RATE = 0.02
DEATH_RATE = 0.75

def __convert_array__(df, width, height):
    """Get and convert pandas array into JPEG image map."""
    img = Image.new('1', (width, height))
    for x in df.columns:
        for y in df.index:
            img.putpixel((x, y), int(df.iat[y, x]))
    return img

def __gen_level__(x, y):
    """Returns pixel map."""
    gen_cols = [i for i in range(x)]
    gen_rows = [i for i in range(y)]
    df = pandas.DataFrame(index=gen_rows, columns=gen_cols)
    df.fillna(0, inplace=True)
    walkers = [[int(x * 0.5), int(y * 0.5)]]
    mapping = True
    x_bbox = lambda i: False if i in [0, x - 1] else True
    y_bbox = lambda i: False if i in [0, y - 1] else True
    map_size = x * y
    while mapping:
        walker_index = 0
        walker_count = len(walkers)
        dead_walkers = list()
        alive_walkers = list()
        if walker_count > 1 and len(dead_walkers) > 0:
            for i in range(walker_count):
                if not i in dead_walkers:
                    alive_walkers.append(walkers[i])
            walkers = list(alive_walkers)
        for w in walkers:
            c = df.iat[w[1], w[0]]
            if c == 0 and x_bbox(w[0]) and y_bbox(w[1]):
                df.iat[w[1], w[0]] = 1
            if len(walkers) < MAX_WALKERS:
                spawn_walker = uniform(0, 1)
                if spawn_walker <= SPAWN_RATE:
                    walkers.append([w[0], w[1]])
            walk_dir = randint(1, 4)
            if walk_dir == 1:
                if x_bbox(w[0] + 1):
                    w[0] += 1
            elif walk_dir == 2:
                if x_bbox(w[0] - 1):
                    w[0] -= 1
            elif walk_dir == 3:
                if y_bbox(w[1] + 1):
                    w[1] += 1
            elif walk_dir == 4:
                if y_bbox(w[1] - 1):
                    w[1] -= 1
            if walker_count > 1:
                if uniform(0, 1) <= DEATH_RATE:
                    dead_walkers.append(walker_index)
            walker_index += 1
        domain = df.to_numpy().sum()
        if domain != 0 and domain / map_size >= MAX_DOMAIN:
            mapping = False
    return __convert_array__(df, x, y)

def make_dungeon(width, height, auto_save=True):
    """Create new dungeon map."""
    if auto_save:
        pixel_map = __gen_level__(width, height)
        pixel_map.save('auto_save.jpeg', 'JPEG')
    else:
        return __gen_level__(width, height)

def __worker__(queue):
    """Multiprocessing worker thread."""
    while True:
        job = queue.get()
        if job is None: break
        maps_folder, xv, yv, i, count = job
        print(f'Creating a {xv}x{yv} dungeon map ({i + 1} / {count})')
        pixel_map = make_dungeon(xv, yv, auto_save=False)
        pixel_map.save(f'{maps_folder}dungeon-{i}.jpeg', 'JPEG')
        queue.task_done()
    queue.task_done()

def make_dungeons(maps_folder, x=128, y=64, v=256, count=10000):
    """Create multiple dungeon maps and save them to maps folder."""
    from multiprocessing import Process, JoinableQueue, cpu_count
    cores = cpu_count() - 1
    if cores == 0:
        print("CPU Cores must be greater than 1.")
    q = JoinableQueue()
    workers = list()
    for i in range(count):
        xv = x + randint(0, v)
        yv = y + randint(0, v)
        q.put((maps_folder, xv, yv, i, count))
    print(f'CPU Count: {cores + 1}')
    print(f'Creating {cores} worker processes...')
    for i in range(cores):
        w = Process(target=__worker__, args=(q,))
        w.daemon = True
        w.start()
        workers.append(w)
    for worker in workers:
        worker.join()

if __name__ == '__main__':
    print(__license__)
    print('Author:', __author__,
          'Version', __version__,
          'Copyright:', __copyright__)
    xy = (128, 64)
    print(f'Creating {xy[0]}x{xy[1]} map...')
    make_dungeon(*xy)
    print('Map creation complete!')
