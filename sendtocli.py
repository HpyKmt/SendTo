"""
SendTo Command Line Interface
"""
import sys
import os
import shutil
import yaml

from hlib import hpath
from hlib import hrgx
from hlib import hdt
from hlib import hxml
from hlib import h7z
from hlib import hcli


# 他のmoduleからこのfunctionをimportした場合、importしたcallerのmoduleのbatch scriptが作られる。
# 例えば、caller.pyが、この関数をimportして実行した場合、caller.batがSendToフォルダに構築される。
def setup_sendto_batch():
    """Create a batch script in the SendTo folder"""
    # インタープリターのパス
    fp_python = sys.executable
    # 現在実行中のモジュール
    fp_module = sys.argv[0]
    # SendTo のフォルダ
    dir_sendto = os.path.join(os.getenv('appdata'), 'Microsoft', 'Windows', 'SendTo')
    # バッチスクリプトのファイル名称は現在実行中のモジュール名称から拝借
    fn_bat = os.path.splitext(os.path.basename(fp_module))[0] + '.bat'
    # 出力用の絶対パスを構築する。
    fp_bat = os.path.join(dir_sendto, fn_bat)
    # %Arg1%：SendToの場合は右クリックしたファイルもしくはフォルダ
    script = fr"""@echo off
rem python accepts both slash and backslash as path separator.
set "Python="{fp_python}""
set "Script="{fp_module}""
set "Arg1=%1"
set Statement=%Python% %Script% %Arg1%
%Statement%
pause
"""
    # ファイルへの書き込み
    with open(fp_bat, 'w') as f:
        f.write(script)
    # 完了報告
    print(f'{fp_bat} was created.')
    print(script)


def _get_all_any(msg='Logic? 1=all or 0=any:'):
    while True:
        s = input(msg)
        if s == '1':
            return all
        elif s == '0':
            return any
        else:
            print('Invalid Input.')


# 動的にファイル・フォルダをフィルタリングをする関数を作成する。
def _create_filter_function():
    # 判定に使う関数のリスト
    # ユーザーの判断によりLambda関数をAppendする。
    #
    # Lambda関数の設計ルール
    # 　「argument」は「Path object」
    # 　「return」は判定結果の「Boolean」
    fnc_lst = []

    # ---------------------------------------------------------------------------------
    # 正規表現

    # os.path.basenameでフィルタする？
    if hcli.get_yes_no(msg='Filter by Regex on Base Name?'):
        pattern = hrgx.Prompt.get_pattern_ignore_case(msg='Basename Rgx:')
        fnc_lst.append(lambda pat_obj: pattern.match(pat_obj.path) is not None)

    # 絶対パスでフィルタする？
    if hcli.get_yes_no(msg='Filter by Regex on Absolute Path?'):
        pattern = hrgx.Prompt.get_pattern_ignore_case(msg='Absolute Path Rgx:')
        fnc_lst.append(lambda pat_obj: pattern.match(pat_obj.base_name) is not None)

    # ---------------------------------------------------------------------------------
    # タイムスタンプ

    # 更新日時　最小
    if hcli.get_yes_no(msg='Add Minimum Modified Date?'):
        ts_min = hdt.DateTime.prompt_datetime(msg='Minimum Modified Date: ').timestamp()
        fnc_lst.append(lambda pat_obj: pat_obj.time_stamp > ts_min)

    # 更新日時　最大
    if hcli.get_yes_no(msg='Add Maximum Modified Date?'):
        ts_max = hdt.DateTime.prompt_datetime(msg='Max Modified Date: ').timestamp()
        fnc_lst.append(lambda pat_obj: pat_obj.time_stamp < ts_max)

    # --------------------------------------------------------------------------------
    # 関数「all()」もしくは、関数「any()」をユーザーから取得する。
    all_or_any = _get_all_any()

    # 関数を作る
    def fnc_ret(pat_obj):
        # fnc_lstが空なら判別する必要が無いので「True」を返す。
        # fnc_lstが空でないなら、all もしくは any で、ファイル・フォルダの合否を判定する。。
        return True if len(fnc_lst) == 0 else all_or_any([fnc(pat_obj) for fnc in fnc_lst])

    # 構築された関数を渡す。
    return fnc_ret


# 中間フォルダを作る関数。
# すでにフォルダが存在した場合のエラーは無視する。
def _wrap_make_dirs(dst_dir):
    try:
        os.makedirs(dst_dir)
    except FileExistsError:
        pass
    else:
        print(f'created "{dst_dir}"')


# ファイルやフォルダをコピーする。
# Callerは、ファイルか？フォルダか？を意識しなくてよい。
def _wrap_copy(src_abs, dst_dir):
    # 出力フォルダの確認
    dst_type = hpath.get_path_type(dst_dir)
    if dst_type != 'dir':
        raise ValueError(f'{dst_dir} is not a folder.')

    # 入力フォルダの確認
    src_type = hpath.get_path_type(src_abs)

    if src_type == 'file':
        shutil.copy2(src_abs, dst_dir)
        print(f'copied file "{src_abs}" to "{dst_dir}".')
    elif src_type == 'dir':
        shutil.copytree(src_abs, dst_dir)
        print(f'copied dir "{src_abs}" to "{dst_dir}".')
    else:
        raise ValueError(f'f"{src_abs}" is neither file or folder.')


class Cli:
    # ---------------------------------------------------------------
    # パスの設定関数
    # - 現在の設定に関わらず設定を強行できる。
    # - ユーザーから直接実行してもらう。
    # ユーザーに入力パス(ファイル or フォルダ)を設定させる。
    def set_path_in(self):
        """Set input as either a file or a folder"""
        ret = hpath.Prompt.get_file_or_dir(msg='Input File/Folder: ')
        self.path_in = ret
        self.path_in_type = hpath.get_path_type(ret)

    # ユーザーに入力パス(フォルダ)を設定させる。
    def set_dir_in(self):
        """Set input as a folder"""
        ret = hpath.Prompt.get_dir(msg='Input Folder: ')
        self.path_in = ret
        self.path_in_type = hpath.get_path_type(ret)

    # ユーザーに入力パス(ファイル)を設定させる。
    def set_file_in(self):
        """Set input as a file"""
        ret = hpath.Prompt.get_filer(msg='Input File: ')
        self.path_in = ret
        self.path_in_type = hpath.get_path_type(ret)

    # ユーザーに出力フォルダを設定させる。
    def set_dir_out(self):
        """Set an output folder"""
        ret = hpath.Prompt.get_dir(msg='Output Folder: ')
        self.dir_out = ret
        self.dir_out_type = hpath.get_path_type(ret)

    # ---------------------------------------------------------------
    # パスの設定関数
    # - 未設定の場合のみ設定を促す
    # - ユーザーからは直接は実行できない。
    def _set_path_in(self):
        if not (self.path_in_type in ['dir', 'file']):
            self.set_path_in()

    def _set_dir_in(self):
        if self.path_in_type != 'dir':
            self.set_dir_in()

    def _set_file_in(self):
        if self.path_in_type != 'file':
            self.set_file_in()

    def _set_dir_out(self):
        if self.dir_out_type != 'dir':
            self.set_dir_out()

    def path(self):
        """Set paths..."""

        # 「...」は、「新しいループに突入しますよ」という意味。

        def print_paths():
            """Print current path settings """
            print(f"""=== Path ===
\tpath in      :   {self.path_in}
\tpath in type :   {self.path_in_type}
\tdir out      :   {self.dir_out}
\tdir out type :   {self.dir_out_type}
""")

        cmd_fnc = {'set path in': self.set_path_in,
                   'set dir in': self.set_dir_in,
                   'set file in': self.set_file_in,
                   'set dir out': self.set_dir_out,
                   'print paths': print_paths}

        hcli.launch_prompt_loop(cmd_fnc=cmd_fnc, title='Path')

    # ---------------------------------------------------------------
    # 実用関数：ここから

    def zip(self):
        """Zip commands..."""
        # 入力がフォルダでない場合は、入力フォルダを設定してもらう。
        # 仮定：ファイルを圧縮するならスクリプト処理は必要ないだろう。
        self._set_dir_in()

        def archive_child_dirs():
            """archive each child folder"""
            # 同じパスに保存
            if hcli.get_yes_no('Save to the same location?'):
                # ループ
                for dir_child in hpath.Dir(self.path_in).mapper(target='dir', recursive=False):
                    ret = shutil.make_archive(base_name=dir_child,
                                              format='zip',
                                              root_dir=dir_child)
                    print(f'Created "{ret}".')
            # 別のパスに保存
            else:
                # 未設定の場合は出力フォルダを設定してもらう。
                self._set_dir_out()
                # ループ
                rel_obj = hpath.Rel(self.path_in, dir_out=self.dir_out, target='dir', recursive=False)
                for rel_tpl in rel_obj.yield_rel_tpl():
                    ret = shutil.make_archive(base_name=rel_tpl.dst_abs,
                                              format='zip',
                                              root_dir=rel_tpl.src_abs)
                    print(f'Created "{ret}".')

        # ユーザーが選択するコマンドの辞書
        cmd_fnc = {'archive child dirs': archive_child_dirs,
                   }

        # ループを開始
        hcli.launch_prompt_loop(cmd_fnc=cmd_fnc, title='ZIP')

    def xml(self):
        """XML commands..."""
        # 「...」は、「新しいループに突入しますよ」という意味。

        # まずは、入力パスを設定する。
        self._set_path_in()

        # XMLファイルの破損を確認する。
        def check_corruption():
            """Check if each XML file can be parsed as XML successfully"""
            # 読み込み失敗したファイルのリスト
            fp_err_lst = []

            # ループ
            for i, fp in enumerate(hxml.yield_fp(self.path_in)):
                print(f'\r{i} {fp}', end='')
                obj = hxml.Xml(fp)
                if obj.err:
                    fp_err_lst.append(fp)

            # 結果を表示する。
            print(f'\n=== Result Count=({len(fp_err_lst)})===')
            for i, fp_err in enumerate(fp_err_lst):
                print(f'{i}: {fp_err}')

        # ファイル書き込み機能にエラー処理を付けたラッパー
        # 内部関数なのでユーザーから直接は実行されない。
        def _prettify_sub(fp_in, fp_out):
            # 現在読み込んでいるファイルを表示する。
            print(f'\rReading {fp_in}', end='')
            # ファイルを読み込む。
            obj = hxml.Xml(fp_in)
            # 成功した場合はファイルに書き込む。
            if obj.err is None:
                obj.pretty_write_utf8(fp_out)
            # エラーが発生したら、ループを止める。
            else:
                print(f'\nERROR! Failed to parse{fp_in}.')
                print(obj.err)
                input(f'Press enter to continue...')

        # XMLファイルをフォーマットする。
        def prettify_utf8():
            """Format XML files in UT-8 Encoding"""
            # 上書き
            if hcli.get_yes_no('Overwrite?'):
                # ループ
                for fp_in in hxml.yield_fp(self.path_in):
                    _prettify_sub(fp_in=fp_in, fp_out=fp_in)
                # ループ終了
                print('\ncompleted.')

            # 新規ファイルに出力
            else:
                # 出力フォルダを確保する。
                self._set_dir_out()

                # 入力がフォルダの場合
                if self.path_in_type == 'dir':
                    rel_obj = hpath.Rel(path=self.path_in, dir_out=self.dir_out)
                    # ループ
                    for rel_tpl in rel_obj.yield_rel_tpl():
                        # 'src_abs', 'src_rel', 'dst_abs', 'dst_dir'
                        # 拡張子がＸＭＬの場合
                        if hpath.File(rel_tpl.src_abs).ext_upper == '.XML':
                            # 中間フォルダを作成する。
                            _wrap_make_dirs(rel_tpl.dst_dir)
                            # ファイルに書き込む
                            _prettify_sub(fp_in=rel_tpl.src_abs, fp_out=rel_tpl.dst_abs)
                    # ループ終了
                    print('\ncompleted.')

                # 入力がファイルの場合
                elif self.path_in_type == 'file':
                    fp_out = os.path.join(self.dir_out + hpath.File(self.path_in).base_name)
                    # ファイルに書き込む
                    _prettify_sub(fp_in=self.path_in, fp_out=fp_out)

        # データ集計関数を受けて、データを集計して結果をYAMLに出力する関数。
        # 渡す関数によって、任意のデータ解析が可能になる。
        # 内部関数なのでユーザーから直接は実行されない。
        def _get_data(fnc_get_data, fn_out='count.yml'):
            # 出力フォルダを確保する。
            self._set_dir_out()

            # 出力リスト
            result = []

            # 出力リストにデータを加える。
            # 簡単な処理だけど、複数の箇所で使われているので、
            # DictionaryのKeyをTypoしてKeyが不整合を起こさないようにFunctionにしておく。
            def append_result(file, data):
                result.append({'file': file, 'data': data})

            # 入力がフォルダの場合
            if self.path_in_type == 'dir':
                rel_obj = hpath.Rel(path=self.path_in, dir_out=self.dir_out)
                # ループ
                for rel_tpl in rel_obj.yield_rel_tpl():
                    # 'src_abs', 'src_rel', 'dst_abs', 'dst_dir'
                    # 拡張子がＸＭＬの場合
                    if hpath.File(rel_tpl.src_abs).ext_upper == '.XML':
                        # カウントする
                        # ファイルは相対パス
                        append_result(file=rel_tpl.src_rel, data=fnc_get_data(rel_tpl.src_abs))
                # ループ終了
                print('\nloop completed.')

            # 入力がファイルの場合
            elif self.path_in_type == 'file':
                fp_out = os.path.join(self.dir_out + hpath.File(self.path_in).base_name)
                # カウントする
                # ファイルはファイル名称
                append_result(file=hpath.File(self.path_in).base_name, data=fnc_get_data(self.path_in))

            # YAMLファイル出力
            fp_out = os.path.join(self.dir_out, fn_out)
            with open(fp_out, 'w') as f:
                yaml.dump(result, f, default_flow_style=False)
            print(f'{fp_out} was created.')

        def count_tags():
            """Count element names per file."""

            def get_tag_count(fp_in):
                return dict(hxml.Xml(fp_in).count_tag_names())

            _get_data(get_tag_count, fn_out='tag_count.yml')

        def count_xpath():
            """Count items based on XPath expression"""
            xpath = hxml.get_xpath()

            def get_xpath_count(fp_in):
                return hxml.Xml(fp_in).count_by_xpath(xpath=xpath)

            _get_data(get_xpath_count, fn_out='xpath_count.yml')

        # ユーザーが選択するコマンドの辞書
        cmd_fnc = {'check corruption': check_corruption,
                   'pretty utf8': prettify_utf8,
                   'count tags': count_tags,
                   'count xpath': count_xpath}

        # ループを開始
        hcli.launch_prompt_loop(cmd_fnc=cmd_fnc, title='XML')

    def seven(self):
        """7z commands..."""

        def archive_child_dirs():
            """archive each child folder"""
            # 入力フォルダ設定する
            self._set_dir_in()

            # 同じパスに保存
            if hcli.get_yes_no('Save to the same location?'):
                # ループ
                for dir_child in hpath.Dir(self.path_in).mapper(target='dir', recursive=False):
                    p = hpath.Path(dir_child)
                    # パスワードはフォルダの名称にする。
                    obj = h7z.Add(dir_in=dir_child, dir_out=p.parent, fn_out_wo_ext=p.base_name, pwd=p.base_name)
                    stmt = obj.construct_statement()
                    h7z.execute_statement(stmt)
            # 別のパスに保存
            else:
                # 未設定の場合は出力フォルダを設定してもらう。
                self._set_dir_out()
                # ループ
                rel_obj = hpath.Rel(self.path_in, dir_out=self.dir_out, target='dir', recursive=False)
                for rel_tpl in rel_obj.yield_rel_tpl():
                    p = hpath.Path(rel_tpl.src_abs)
                    obj = h7z.Add(dir_in=rel_tpl.src_abs, dir_out=rel_tpl.dst_dir,
                                  fn_out_wo_ext=p.base_name, pwd=p.base_name)
                    stmt = obj.construct_statement()
                    h7z.execute_statement(stmt)

        # ユーザーが選択するコマンドの辞書
        cmd_fnc = {'archive child dirs': archive_child_dirs,
                   }

        # ループを開始
        hcli.launch_prompt_loop(cmd_fnc=cmd_fnc, title='7zip')

    def grep(self):
        """Grep commands..."""
        # 入力ファイル・フォルダ設定する
        self._set_path_in()

        # ファイルパスをyield するジェネレータ関数
        def _get_fp_itr():
            # 入力がファイルの場合は、そのまま返す。
            if self.path_in_type == 'file':
                yield self.path_in
            # 入力がフォルダの場合：
            elif self.path_in_type == 'dir':
                # まず、フィルタ関数を作る
                is_passed = _create_filter_function()
                # ファイルをループしつつ、合致条件のファイルパスを返す。
                for fp in hpath.Dir(path=self.path_in).mapper():
                    if is_passed(hpath.Path(fp)):
                        yield fp

        # 正規表現を作る。
        def create_rgx_from_sample():
            """Create regular expression based on a sample line"""
            hrgx.create_regex_from_sample()

        def count_matches():
            """Count the matching lines, and get the total match count"""
            hrgx.count_match(fp_itr=_get_fp_itr(),
                             enc_read=hrgx.Prompt.get_encoding(),
                             rgx_ptn=hrgx.Prompt.get_pattern_inline_flag())

        def df_to_csv():
            """Extract matching items to CSV as DataFrame"""
            # 出力パスの設定
            self._set_dir_out()
            fp_out = os.path.join(self.dir_out, 'grep.csv')

            # データフレームの作成
            df = hrgx.to_df(fp_itr=_get_fp_itr(),
                            enc_read=hrgx.Prompt.get_encoding(),
                            rgx_ptn=hrgx.Prompt.get_pattern_inline_flag())

            # ファイルへの書き込み
            df.to_csv(fp_out)
            print(f'{fp_out} was created.')

        # ユーザーが選択するコマンドの辞書
        cmd_fnc = {'create rgx from sample': create_rgx_from_sample,
                   'count matches': count_matches,
                   'df to csv': df_to_csv,
                   }

        # ループを開始
        hcli.launch_prompt_loop(cmd_fnc=cmd_fnc, title='Grep')

    # コピーする。
    def copy(self):
        """Copy files or folders maintaining relative folder structure"""
        # 入出力フォルダ設定する。
        self._set_dir_in()
        self._set_dir_out()

        # ファイルをコピーしたいのか、それとも、フォルダをコピーしたいのか？
        target = hpath.Prompt.get_target()

        # 再帰検索するか？
        recursive = hcli.get_yes_no('Recursively?')

        # フィルタ関数
        is_passed = _create_filter_function()

        # ループ
        rel_obj = hpath.Rel(path=self.path_in, dir_out=self.dir_out, target=target, recursive=recursive)
        # rel_tplは、collections.namedtuple
        # member は ['src_abs', 'src_rel', 'dst_abs', 'dst_dir']
        for rel_tpl in rel_obj.yield_rel_tpl():
            # Pathオブジェクトを作成し、フィルタする
            pat_obj = hpath.Path(rel_tpl.src_abs)
            if is_passed(pat_obj):
                # 中間フォルダを構築
                _wrap_make_dirs(rel_tpl.dst_dir)
                # ターゲットのコピー
                _wrap_copy(rel_tpl.src_abs, rel_tpl.dst_dir)

    # コンストラクタ
    def __init__(self):
        self.path_in = None
        self.path_in_type = 'err'
        self.dir_out = None
        self.dir_out_type = 'err'

        # SendToで入力パスが渡されている場合、入力パスとタイプを設定する。
        if len(sys.argv) == 2:
            self.path_in = sys.argv[1]
            self.path_in_type = hpath.get_path_type(sys.argv[1])

        # ユーザーが実行できるコマンドを辞書に登録する。
        self.cmd_fnc = {
            # 基本的に必要ないけど、パスを設定するコマンド
            'path': self.path,
            # 目的に応じたコマンド
            'copy': self.copy,
            'zip': self.zip,
            '7z': self.seven,
            'xml': self.xml,
            'grep': self.grep,
            # 一度しか使わない設定コマンド
            'setup sendto batch': setup_sendto_batch
        }

    # メインループの起動。
    def launch(self):
        hcli.launch_prompt_loop(cmd_fnc=self.cmd_fnc)


if __name__ == '__main__':
    Cli().launch()
