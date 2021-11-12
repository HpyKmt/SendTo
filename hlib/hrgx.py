"""
Regular Expression
"""
import re
import sys
import codecs

import pandas as pd

try:
    from hlib import hcli
except ImportError:
    try:
        import hcli
    except ImportError:
        print('Failed to import hcli module.')
        sys.exit()


class Prompt:
    # re.compile()で、re.Iが設定され大文字小文字を区別しない。
    # ファイルパスを検索する場合に適切。
    @staticmethod
    def get_pattern_ignore_case(msg='Regular Expression: '):
        while True:
            s = input(msg)
            try:
                pattern = re.compile(s, re.IGNORECASE)
            except re.error as e:
                print(e)
            else:
                return pattern

    # フラグが必要な場合は、正規表現に(?i)等の表現を含める。
    # re.compile()で、フラグ設定は無い。
    @staticmethod
    def get_pattern_inline_flag(msg='Regular Expression: '):
        while True:
            s = input(msg)
            try:
                pattern = re.compile(s)
            except re.error as e:
                print(e)
            else:
                return pattern

    @staticmethod
    def get_columns(msg='Column Names separated by space: '):
        while True:
            # ユーザー入力を得る
            columns = input(msg).split()

            # 入力結果を表示
            print(f'Column Count: {len(columns)}')
            for i, col in enumerate(columns):
                print(f'[{i}]: {col}')

            # 入力内容がOKか？
            if hcli.get_yes_no('Good?'):
                return columns

    @staticmethod
    def get_encoding(msg='Input encoding by name: '):
        while True:
            s = input(msg)
            try:
                result = codecs.lookup(s)
            except LookupError as e:
                print('Failed!')
                print(e)
            else:
                print('Successful.')
                print(result)
                return s


# サンプル入力を元に正規表現を作成する。
def create_regex_from_sample():
    # =============================================================================
    # グループ検索
    # 連続的にre.sub()を実行すると、先行の正規表現の表現を後続の正規表現が上書きしてしまう。
    # 想定外の上書きを防ぐために、特殊な文字列に一旦、仮変換する必要があり、変換表を辞書で確保する。
    class Group:
        # 「こんな文字列は普通は存在し名だろう!」という感じの文字列シーケンス
        # こんな文字列シーケンスで括っておけば、一次変換文字列のユニーク性を確保できる。
        ENC = '●▲■★'

        # グループを表現する文字列を括る関数う
        @classmethod
        def enclose(cls, grp_nm):
            return f'{cls.ENC}{grp_nm}{cls.ENC}'

        # Key: グループの正規表現。当然、カッコで括っていないといけない。
        # Value: グループを表現する名称。CamelCaseのAlphaNumericで表現する。記号等は使用しないこと。
        DICT = {'\[([^\]]+)\]': 'SquareBrackets',
                '\{([^\}]+)\}': 'CurlyBraces',
                '\(([^\)]+)\)': 'Parenthesis',
                '(0x[0-9a-fA-F]+)': 'HexNumbers'}

    # =============================================================================
    # 現在のサンプルを表示する関数。
    def print_sample():
        print(f'\tsample: {sample}')

    # =============================================================================
    # 特殊文字のエスケープ
    class SpecialChar:
        # 正規表現で特別な機能を持っている特殊文字のリスト
        CHAR_LIST = r'. ^ $ * + - ? ( ) [ ] { } \ | — /'.split()

        # 特殊文字をエスケープする
        @classmethod
        def escape(cls, c):
            return rf'\{c}'

        # もし特殊文字がサンプル文字列ラインに含まれていたら特殊文字を返すジェネレータ
        @classmethod
        def yield_detected_char(cls, line):
            for c in cls.CHAR_LIST:
                if c in line:
                    yield c

    # =============================================================================
    # 実処理：ここから
    # ユーザーがらサンプルデータを入力してもらう。
    sample = input('Sample Text: ')

    # ユーザーに確認しつつ、仮変換を進める。
    for regex, group_name in Group.DICT.items():
        # グループ検索に合致するか確認する。
        matches = re.findall(regex, sample)
        # 合致がヒットした場合：
        if len(matches) > 0:
            # 合致した文字列を表示する。
            for i, match in enumerate(matches):
                print(f'\t{group_name}[{i}]: {match}')
            # 変換するか？ユーザーに確認する。
            if hcli.get_yes_no(f'Replace {group_name}?'):
                sample = re.sub(regex, Group.enclose(group_name), sample)
                print_sample()

    # 特殊文字のエスケープ
    for special_char in SpecialChar.yield_detected_char(sample):
        if hcli.get_yes_no(f'Escape {special_char}?'):
            escaped_char = SpecialChar.escape(special_char)
            sample = sample.replace(special_char, escaped_char)
            print(f'\t"{special_char}" --> "{escaped_char}"')
            print_sample()

    # 仮変換を本当の正規表現に変換する。
    print('Replace placeholders...')
    for regex, group_name in Group.DICT.items():
        placeholder = Group.enclose(group_name)
        if placeholder in sample:
            sample = sample.replace(placeholder, regex)
            print_sample()

    # 変換結果を出力する。
    # この出力をNotepad＋＋等のテキストエディタで確認すること。
    # ユーザーはこの出力を必要に応じて編集し、正規表現の最適化を行う。
    # 必要ないグループが存在すれば、「.*」で表現を省略する。
    print(f'result: {sample}')


def to_df(fp_itr, enc_read='cp932', rgx_ptn=re.compile('.*')):
    # グループ数によってコラムを設定する。
    group_count = rgx_ptn.groups
    # グループ数が一つでも存在する場合はコラムを作成する。
    if group_count > 0:
        while True:
            # コラムをユーザーに設定してもらう。
            columns = Prompt.get_columns()
            # 設定したコラム数がグループ数に合致しない場合は入力し直してもらう。
            columns_count = len(columns)
            if group_count == columns_count:
                print(f'INF: Group count {group_count} matches column count {columns_count}.')
                break
            else:
                print(f'ERR: Group count {group_count} does not match column count {columns_count}!')
    # グループが存在しなければ、コラム名称はデフォルト。
    else:
        columns = ['Match']

    # データを集める。
    data = []
    for fp_abs in fp_itr:
        with open(fp_abs, encoding=enc_read, errors='ignore') as f:
            s = f.read()
        datum = rgx_ptn.findall(s)
        data.extend(datum)
        print('*', end='')
    print()

    # データフレームを返す。
    df = pd.DataFrame(data=data, columns=columns)
    return df


def count_match(fp_itr, enc_read='cp932', rgx_ptn=re.compile('.*')):
    # 合計の合致数
    count_total = 0
    # ループ
    for fp_abs in fp_itr:
        # 合致数を得る
        with open(fp_abs, encoding=enc_read, errors='ignore') as f:
            s = f.read()
        buf = rgx_ptn.findall(s)
        count_buf = len(buf)
        # 合致数を表示
        print(f'count: {count_buf}, file: {fp_abs}')
        # 合計を計算
        count_total += count_buf
    # 合計を表示する。
    print(f'total count: {count_total}')


def _test():
    create_regex_from_sample()


if __name__ == '__main__':
    _test()
