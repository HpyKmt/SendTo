"""
DateTime
"""
import datetime


class DateTime:
    # テキスト入力フォーマットの定義
    # 使いそうなフォーマットを列挙しておく。
    # %d/%m/%Yは、%m/%d/%Yと競合するので定義しない。
    # 沢山のパターンをループしてtryするので処理は遅い。
    # Prompt用の単発の変換に使用するので、遅くても問題ない。
    FORMATS = [
        # with / and :
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S.%f',

        # with - and :
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',

        # with / and :
        # %y (2 digit year)
        '%y/%m/%d %H:%M:%S',
        '%y/%m/%d %H:%M:%S.%f',

        # what shows on computer
        '%m/%d/%Y %I:%M %p',
        '%Y/%m/%d %I:%M %p',
        '%Y/%m/%d %H:%M',

        # date only
        '%m/%d/%Y',
        '%Y/%m/%d',

        # without
        '%Y%m%d%H%M%S',
        '%Y%m%d%H%M%S%f']

    # 文字列をDateTimeオブジェクトに変換を試みる。
    # 成功したら、datetime objectを返し、何もヒットしなかったら、Noneを返す。
    @classmethod
    def str_to_dt(cls, s):
        """ convert string to datetime object """
        for fmt in cls.FORMATS:
            try:
                dt = datetime.datetime.strptime(s, fmt)
            except ValueError:
                pass
            else:
                # ファイルも更新日時はfloatのtimestampなので
                # タイムスタンプにしたい場合は、dt.timestamp()とする。、
                return dt
        else:
            print(f'ERROR: {s} did not get parsed within specified formats!')
            return None

    @classmethod
    def print_supported_formats(cls):
        print('=== supported datetime format ===========')
        for fmt in cls.FORMATS:
            print(f'\t{fmt}')
        print('=========================================')

    @classmethod
    def prompt_datetime(cls, msg='DateTime: '):
        while True:
            s = input(msg)
            dt = cls.str_to_dt(s)
            if dt is None:
                cls.print_supported_formats()
            else:
                return dt


def _test():
    DateTime.print_supported_formats()
    while True:
        dt = DateTime.prompt_datetime(msg='Input the limit datetime: ')
        print(dt, dt.timestamp())


if __name__ == '__main__':
    _test()
