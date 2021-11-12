"""
Command Line Interface
"""


def get_yes_no(msg='Question?'):
    while True:
        s = input(f'"{msg}" 1=Yes 0=No: ')
        if s == '1':
            return True
        elif s == '0':
            return False
        else:
            print('Invalid Input.')


def launch_prompt_loop(cmd_fnc={'hello': lambda: print('hello')},
                       prompt_symbol='>>> ',
                       err_msg='Command Not Defined...',
                       title='Top',
                       no_doc='---'):
    """
    :param cmd_fnc: dict
        key=str: コマンド文字列、ユーザーが実行するコマンドを選ぶ為に入力する。
        value=function(): 引数は受け付けない。DocStringが関数の説明文として表示される。
    :param prompt_symbol: プロンプトのシンボルで、デフォルトはPythonのプロンプトを真似する。
    :param err_msg: 定義されていないコマンドを入力した場合に表示するエラーメッセージ
    :param title: 現在のループを解説できる言葉
    :param no_doc: 実行する関数にDocStringが設定されてない時に表示する文字列
    :return: 無し
    """
    def print_commands():
        """Print the supported commands"""
        # 全コマンドの文字列長を解析して適切なPadding数宇を解析する。
        # 最大の文字列長 + 1 とする。
        pad_width = max([len(cmd) for cmd in cmd_fnc.keys()]) + 1

        # タイトルを表示する。
        print(title.center(len(title) + 20, '='))

        # 各コマンドを表示する。
        for cmd, fnc in cmd_fnc.items():
            k = cmd.ljust(pad_width)
            v = fnc.__doc__ if fnc.__doc__ else no_doc
            print(f'{k}: {v}')

    # 辞書にprint_command()を追加してから、コマンド一覧を表示する。
    cmd_fnc['print commands'] = print_commands
    print_commands()

    # ループの開始：
    while True:
        # ユーザーから入力を得る
        s = input(prompt_symbol)

        # 入力が空の場合はループを抜ける
        if s == '':
            print(f'breaking out of prompt loop "{title}"...')
            break
        # 入力が定義されている場合は実行する。
        elif s in cmd_fnc:
            cmd_fnc[s]()
        # 定義されていない場合は何もせずにループを継続する。
        else:
            print(err_msg)


def _test():
    launch_prompt_loop()


if __name__ == '__main__':
    _test()
