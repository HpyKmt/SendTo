"""
7zip
■　ダウンロード
    https://www.7-zip.org/

    https://sevenzip.osdn.jp/chm/cmdline/index.htm

■　7z.exeの使い方
    7z.exe is the command line version of 7-Zip.
    7z.exe uses 7z.dll from the 7-Zip package.
    7z.dll is used by the 7-Zip File Manager also.
    - Command Line syntax
    - Exit Codes
    - Commands
    - Switches

    ================================================
    Command Description
    ------- -----------
         a  Add
         b  Benchmark
         d  Delete
         e  Extract
         h  Hash
         i  Show information about supported formats
         l  List
        rn  Rename
         t  Test
         u  Update
         x  extract with full paths

    ================================================
     Switch  Description
    -------- ------------
         -r  Enable recurse subdirectories
         -o  set output directory
"""
import os
import enum
import subprocess


# 普通にインストールしたら、ここにファイルがあるはず。
# このファイルが無いと、このスクリプトは機能しない。
FP_EXE = r"C:\Program Files\7-Zip\7z.exe"
FP_DLL = r"C:\Program Files\7-Zip\7z.dll"

# デフォルトのパスワード
DFT_PWD = '0123456789' * 5


class ErrorCode(enum.IntEnum):
    # https://sevenzip.osdn.jp/chm/cmdline/exit_codes.htm
    # Exit Codes from 7-Zip
    # 7-Zip returns the following exit codes:
    # Code Meaning
    # ---- -------------------------------------------------------------------
    #   0  No error
    #   1  Warning (Non fatal error(s)).
    #      For example, one or more files were locked by some other application
    #   2  Fatal error
    #   7  Command line error
    #   8  Not enough memory for operation
    # 255  User stopped the process
    NO_ERROR = 0
    WARNING = 1
    FATAL_ERROR = 2
    COMMAND_LINE_ERROR = 7
    NOT_ENOUGH_MEMORY = 8
    USER_STOPPED = 255


# subprocess.run()で7z.exeを実行する時のラッパー関数
# エラーが発生したらエラーコードを表示する。
def execute_statement(statement):
    # execute
    ret = subprocess.run(statement)

    # returned code
    return_code = ret.returncode

    # description
    if return_code in ErrorCode.__members__.values():
        description = ErrorCode(return_code).name
    else:
        description = 'This returned code is not documented.'

    # print result
    print(f'returned code: {return_code}, description: {description}')


def enclose(s):
    # 一旦、ダブルクオートを排除してから、ダブルクオートで括りなおす。
    return '"' + s.strip('"') + '"'


def is_str(s):
    if type(s) == str and len(s) > 0:
        return True
    else:
        return False


class Command:
    # コンストラクタ
    # EXEとDLLがシステム上に存在しているか？を確認しておく。
    def __init__(self):
        # ライブラリ「7z.dll」が見つからなかったら例外
        if not os.path.isfile(FP_DLL):
            raise ValueError(f'7z.dll was not found at {FP_EXE}')

        # アプリケーション「7z.exe」が見つからなかったら例外
        if not os.path.isfile(FP_EXE):
            raise ValueError(f'7z.exe was not found at {FP_EXE}')

        # アプリケーションを登録
        self.app = FP_EXE
        self.prm_lst = []

    def construct_statement(self):
        # パラメータリストで、要素が文字列で長さが存在する場合は、ステートメントに加える。
        return self.app + ' ' + ' '.join([i for i in self.prm_lst if type(i) == str and len(i) > 0])


class Add(Command):
    # Adds files to archive.
    def __init__(self,
                 dir_in, dir_out, fn_out_wo_ext,
                 flt_exp='*', archive_type='7z', volume_size='100m',
                 pwd=DFT_PWD, header_encryption=True, recurse=True):
        """ Constructor
        ----------- 必須 -----------
        :param dir_in:　圧縮対象のファイルが存在するフォルダ。CWDとして設定される。
        :param dir_out: 圧縮されたファイルを保存するフォルダ。
        :param fn_out_wo_ext: 圧縮ファイルの拡張子無しのファイル名称

        ----------- オプション -----------
        :param flt_exp: ワイルドカードで圧縮対象のファイル名称を指定。単一ファイルの場合はファイル名称をワイルドカード無しで設定する。
        :param archive_type: 「zip」にしたら機能が減るので、基本的に「7z」だけしか使わないようにしたい。
        :param volume_size: 分割された１つファイルのサイズ。100mで、100MegaBytesという意味
        :param pwd: パスワード
        :param header_encryption: ファイルの名称等のヘッダー情報も隠すフラグ。
        :param recurse: 再帰検索のフラグ。
        """
        super().__init__()

        # 圧縮コマンド
        # https://sevenzip.osdn.jp/chm/cmdline/commands/add.htm
        self.cmd = 'a'

        # CWDにdir_inを圧縮対象のフォルダとして登録する。
        os.chdir(dir_in)

        # 拡張子無しの圧縮ファイルの絶対パス。
        self.fp_out_wo_ext = enclose(os.path.join(dir_out, fn_out_wo_ext))

        # 圧縮対象ファイルのフィルタのワイルドカード表現
        # スペースが複数の表現をORで繋ぐので、本表現はクオートで括ってはいけない。
        # https://sevenzip.osdn.jp/chm/cmdline/syntax.htm
        self.flt_exp = flt_exp

        # タイプ
        # https://sevenzip.osdn.jp/chm/cmdline/switches/type.htm
        self.t = None
        if is_str(archive_type):
            self.t = f'-t{archive_type}'

        # パスワード
        # https://sevenzip.osdn.jp/chm/cmdline/switches/password.htm
        self.p = None
        if is_str(pwd):
            self.p = f'-p{pwd}'

        # https://sevenzip.osdn.jp/chm/cmdline/switches/method.htm#
        self.m = '-mhe' if header_encryption else None

        # 再帰
        # https://sevenzip.osdn.jp/chm/cmdline/switches/recurse.htm
        self.r = f'-r' if recurse else None

        # 分割サイズ
        # https://sevenzip.osdn.jp/chm/cmdline/switches/volume.htm
        self.v = f'-v{volume_size}'

        # パラメータのリストを構築
        self.prm_lst.extend([
            # positional
            self.cmd, self.fp_out_wo_ext, self.flt_exp,
            # keyword
            self.t, self.p, self.m, self.r, self.v
        ])


class Extract(Command):
    # ExtractWithFullPath
    def __init__(self,
                 fp_in, dir_out,
                 flt_exp='*', archive_type='7z', split=True,
                 pwd=DFT_PWD, recurse=True):
        """ Constructor
        ----------- 必須 -----------
        :param fp_in:　圧縮ファイル。
        :param dir_out: 解凍先のフォルダ。

        ----------- オプション -----------
        :param flt_exp: ワイルドカードで圧縮対象のファイル名称を指定。単一ファイルの場合はファイル名称をワイルドカード無しで設定する。
        :param archive_type: 「zip」にしたら機能が減るので、基本的に「7z」だけしか使わないようにしたい。
        :param pwd: パスワード
        :param recurse: 再帰検索のフラグ。
        """
        super().__init__()

        # 相対パスを保持する解凍コマンド
        # https://sevenzip.osdn.jp/chm/cmdline/commands/extract_full.htm
        self.cmd = 'x'

        # 圧縮ファイルの絶対パス
        # ファイルが分割されている場合は、一つ目の圧縮ファイル「ファイル名.7z.001」をえらばなくてはいけない。
        self.fp_in = enclose(fp_in)

        # 解凍ファイルの出力先フォルダ
        self.dir_out = '-o' + enclose(dir_out)

        # 解凍対象ファイルのフィルタのワイルドカード表現
        # スペースが複数の表現をORで繋ぐので、本表現は「"」で括ってはいけない。
        # https://sevenzip.osdn.jp/chm/cmdline/syntax.htm
        self.flt_exp = flt_exp

        # タイプ
        # https://sevenzip.osdn.jp/chm/cmdline/switches/type.htm
        self.t = None
        if is_str(archive_type):
            self.t = f'-t{archive_type}'

            # ファイルが分割されている場合は、splitのフラグをONにしないといけない。
            if split:
                self.t += '.split'

        # パスワード
        # https://sevenzip.osdn.jp/chm/cmdline/switches/password.htm
        self.p = None
        if is_str(pwd):
            self.p = f'-p{pwd}'

        # 再帰
        # https://sevenzip.osdn.jp/chm/cmdline/switches/recurse.htm
        self.r = f'-r' if recurse else None

        # パラメータのリストを構築
        self.prm_lst.extend([
            # positional
            self.cmd, self.fp_in, self.dir_out, self.flt_exp,
            # keyword
            self.t, self.p, self.r
        ])


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compress files in a folder')

    parser.add_argument('-c', '--cmd', type=str, help='Command')
    parser.set_defaults(cmd='x')

    parser.add_argument('-d', '--dir_in', type=str, help='Input Folder')
    parser.add_argument('-i', '--fp_in', type=str, help='Input Archive')
    parser.add_argument('-o', '--dir_out', type=str, help='Output Folder')
    parser.add_argument('-n', '--fn_out', type=str, help='Output File Name')

    parser.add_argument('-f', '--flt_exp', type=str, help='Filter Wild Card')
    parser.set_defaults(flt_exp='*')

    args = parser.parse_args()

    obj = None
    if args.cmd == 'a':
        obj = Add(dir_in=args.dir_in,
                  dir_out=args.dir_out,
                  fn_out_wo_ext=args.fn_out,
                  )
    elif args.cmd == 'x':
        obj = Extract(fp_in=args.fp_in,
                      dir_out=args.dir_out,
                      flt_exp=args.flt_exp,
                      )

    if obj:
        execute_statement(obj.construct_statement())


if __name__ == '__main__':
    main()
