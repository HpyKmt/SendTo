"""
ファイル・フォルダのパスを解析・構築をするモジュール
"""
import os
import collections


# パスはベースのAbstractクラスっぽい雰囲気をだしているけど、、
# ファイルか、フォルダか、が明確じゃない「曖昧なパス」の場合、Pathをそのまま使うと、コードがまとまる。
class Path:
    def __init__(self, path):
        self.path = path

    def is_args_valid(self):
        if os.path.exists(self.path):
            return True
        else:
            return False

    @property
    def time_stamp(self):
        return os.path.getmtime(self.path)

    @property
    def base_name(self):
        return os.path.basename(self.path)

    @property
    def parent(self):
        return os.path.dirname(self.path)


# ファイル
class File(Path):
    def is_args_valid(self):
        if os.path.isfile(self.path):
            return True
        else:
            return False

    # 拡張子を大文字にして返す。
    # 例　「r"C:\\temp\2.2-1.tsv"」-->「".TSV"」
    @property
    def ext_upper(self):
        return os.path.splitext(self.path)[1].upper()


# フォルダ
class Dir(Path):
    def is_args_valid(self):
        if os.path.isdir(self.path):
            return True
        else:
            return False

    # 絶対パスを返すジェネレータ
    def mapper(self, target='file', recursive=True):
        # 再帰
        if recursive:
            for root, dirs, files in os.walk(self.path):
                # ファイル
                if target == 'file':
                    for file in files:
                        yield os.path.join(root, file)
                # フォルダ
                elif target == 'dir':
                    for _dir in dirs:
                        yield os.path.join(root, _dir)
        # 直下
        else:
            for basename in os.listdir(self.path):
                abs_path = os.path.join(self.path, basename)
                # ファイル
                if target == 'file' and os.path.isfile(abs_path):
                    yield abs_path
                # フォルダ
                elif target == 'dir' and os.path.isdir(abs_path):
                    yield abs_path


# 相対パス
class Rel(Dir):
    # 中間フォルダを考慮する場合、再帰は自明の理なのでrecursive=Trueで固定すべきだけど、
    # Relクラスの使い勝手を考えると、recursiveも含めておくと使い勝手が良いので、recursiveもメンバーに含めておく。
    # path_inは、フォルダであるべき。
    def __init__(self, path, dir_out, target='file', recursive=True):
        super().__init__(path)
        self.dir_out = dir_out
        self.target = target
        self.recursive = recursive
        self.src_rel_lst = []
        self.src_abs_lst = []
        self.dst_dir_lst = []
        self.dst_abs_lst = []

        # 渡された引数が適切な場合はリストデータを構築する。
        if self.is_args_valid():
            self.populate_list()
        # 不適切な引数の場合はエラー
        else:
            raise ValueError('Invalid Input!')

    def is_args_valid(self):
        if os.path.isdir(self.path):
            if os.path.isdir(self.dir_out):
                if self.target in ['file', 'dir']:
                    return True
        return False

    def populate_list(self):
        for src_abs in self.mapper(target=self.target, recursive=self.recursive):
            # 絶対　入力パス
            self.src_abs_lst.append(src_abs)

            # 相対　入力パス
            src_rel = src_abs.replace(self.path, '').strip(os.sep)
            self.src_rel_lst.append(src_rel)

            # 絶対　出力パス
            dst_abs = os.path.join(self.dir_out, src_rel)
            self.dst_abs_lst.append(dst_abs)

            # 絶対　出力パスの親フォルダ
            # 出力先に相対フォルダを作成する為に必要
            dst_dir = os.path.dirname(dst_abs)
            self.dst_dir_lst.append(dst_dir)

    def yield_rel_tpl(self):
        for src_abs, src_rel, dst_abs, dst_dir in zip(
                self.src_abs_lst, self.src_rel_lst, self.dst_abs_lst, self.dst_dir_lst):
            yield RelTpl(src_abs=src_abs, src_rel=src_rel, dst_abs=dst_abs, dst_dir=dst_dir)


RelTpl = collections.namedtuple('RelTpl', ['src_abs', 'src_rel', 'dst_abs', 'dst_dir'])


class Prompt:
    @staticmethod
    def get_file(msg='File: '):
        while True:
            s = input(msg).replace('"', '')
            if os.path.isfile(s):
                return s
            else:
                print('Input Invalid')

    @staticmethod
    def get_dir(msg='Folder: '):
        while True:
            s = input(msg).replace('"', '')
            if os.path.isdir(s):
                return s
            else:
                print('Input Invalid')

    @staticmethod
    def get_file_or_dir(msg='File or Folder: '):
        while True:
            s = input(msg).replace('"', '')
            if os.path.isdir(s) or os.path.isfile(s):
                return s
            else:
                print('Input Invalid')

    @staticmethod
    def get_target(msg='Target "file" or "dir": '):
        while True:
            s = input(msg)
            if s in ['file', 'dir']:
                return s
            else:
                print('Input Invalid')


def yield_sort_modified(path_lst):
    """絶対パスのリストを受信して、更新日時に昇べき順に並び替えて、ファイルパスを返すジェネレータ"""
    for ts, path in sorted([(os.path.getmtime(path), path) for path in path_lst]):
        yield path


def get_path_type(path):
    if os.path.isdir(path):
        return 'dir'
    elif os.path.isfile(path):
        return 'file'
    else:
        return 'err'


def _test():
    pass


if __name__ == '__main__':
    _test()
