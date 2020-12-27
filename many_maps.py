#!./env/bin/python3
from src import dungeon_floor as gen
from os.path import abspath

if __name__ == '__main__':
    print(gen.__license__)
    print('Author:', gen.__author__,
          'Version', gen.__version__,
          'Copyright:', gen.__copyright__)
    p = f'{abspath("./maps")}/'
    a = {'x': 64, 'y': 64, 'v': 256, 'count': 10000}
    gen.make_dungeons(p, **a)
