"""
XML
"""
from lxml import etree
from collections import Counter

try:
    from hlib import hpath
except ImportError:
    try:
        import hpath
    except ImportError:
        print('import hpath failed')


class Xml:
    def __init__(self, fp_in):
        # ファイルを開いてパーシングする
        try:
            f = open(fp_in, 'rb')
            t = etree.parse(f)
        # 失敗したらエラーメッセージを格納する。
        except etree.XMLSyntaxError as e:
            print(f"""ERROR: failed to parse {fp_in}.""")
            self.tree = None
            self.err = e
        # 成功したらElementオブジェクトを格納する。
        else:
            self.tree = t
            self.err = None
        # 最後にファイルを閉じる。
        finally:
            f.close()

    def pretty_write_utf8(self, fp_out):
        # UTF8でファイルに書き出す。
        if self.tree:
            # 関数の名前は、tostring()だが、返すデータタイプはバイトである。
            # ファイルに書き出す時は open(fp, 'w')ではなく、open(fp, 'w')にする必要がある。
            data = etree.tostring(self.tree, pretty_print=True, xml_declaration=True, encoding='utf-8')

            try:
                with open(fp_out, 'wb') as f:
                    f.write(data)
            except PermissionError as e:
                print(e)
                input('Permission error occurred. Press enter to continue...')
        else:
            print(f'ERROR: Cannot write file. self.tree is None.')

    def count_tag_names(self):
        # Elementの名前の数を集計する。
        tags = [i.tag for i in self.tree.xpath('//*')]
        return Counter(tags)

    def count_by_xpath(self, xpath):
        return len(self.tree.xpath(xpath))


def yield_fp(path_in):
    path_type = hpath.get_path_type(path_in)
    # 渡されたパスがファイルの場合はスルーパスする。
    # 拡張子が.xmlじゃなくてもOKとする。
    if path_type == 'file':
        yield path_in
    # 渡されたパスがフォルダの場合はファイルを再帰検索し
    # 拡張子が.XMLだったらパスを返す。
    elif path_type == 'dir':
        for fp in hpath.Dir(path=path_in).mapper():
            if hpath.File(fp).ext_upper == '.XML':
                yield fp
    # 渡されたパスが不適切な場合は例外にすｒ。
    else:
        raise ValueError('Invalid Input')


def get_xpath(msg='XPath: '):
    tree = etree.Element('Root')
    while True:
        s = input(msg)
        try:
            tree.xpath(s)
        except etree.XPathError as e:
            print(f'Xpath{s} parsing failed with error.')
            print('Exception:', e)
        else:
            print(f'Xpath{s} was parsed successfully.')
            return s


def _format_files(path_in):
    for fp in yield_fp(path_in=path_in):
        Xml(fp).pretty_write_utf8(fp)
        print('formatted:', fp)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compress files in a folder')
    parser.add_argument('-i', '--path_in', type=str, help='Input Path')
    args = parser.parse_args()
    _format_files(args.path_in)


if __name__ == '__main__':
    main()
