Name
====
ttadmin

Overview

TeraTermをさらに便利にするツール.
* ファイル名を指定して実行から対象マシンへアクセス可能に
* 踏み台サーバが簡単に設定できる
* .pyファイルとしてサーバを記述できる＝接続先サーバの一元管理
* 設定のコピーが容易にできる

## Usage
```
ssh MACHINE_NAME [user_name]
```

## Install
* Windowsマシンに下記をインストール.
    * Python3.x系
    * Tera Term
* 当リポジトリのbinフォルダを環境変数のPATHに設定.
* ./bin/ディレクトリ配下にssh.batのショートカットをsshという名称で作成
* ./settings.pyを作成し,接続先サーバの情報を設定
    * 基本構造は下記

```
'mymachines': {
    'mymachine': {
        'description': '''
            please write description.
        ''',
        'host': '192.168.10.100',
        'port': '22',
        'default_user': 'd-ebi',
        'users': {
            'd-ebi': {
                'authentication': 'password',
                'password': 'password1234',
            },
            'hogefuga': {
                'authentication': 'key',
                'key': 'please write private key location path.',
            }
        }
    }
},
'othermachines': {
    'db': {
        'desctiption': '''
            DB server
        ''',
        'host': 'localhost',
        'port': '22222',
        'default_user': 'hoge',
        'bastation': {
            'server': 'mymachine',
            'user': 'hogefuga',
        },
        'users': {
            'hoge': {
                'authentication': 'password',
                'password': 'password1234',
            },
            'root': {
                'authentication': 'password',
                'password': 'root1234!',
                'bastaion': 'hoge'
            }
        },
        'command': 'su fuga'
    },
    'web': {
        'extends': 'db',
        'desctiption': '''
            Web server
        ''',
        'port': '22202'
    }
}
"""
```

* 一番外側のキー名（グルーピング名）
    * マシンをグルーピングするキー名,なんでもよい.
* 一つ下のキー名（マシン名）
    * UsageのMACHINE_NAME,このマシン名を使用して接続する.
* その下の階層
    * description
        * サーバの説明.省略可.
    * host
        * サーバのホスト名ないしIPアドレス.
    * port
        * ssh接続する際のポート番号
    * default_user
        * ssh MACHINE_NAMEなどとし,ユーザ名を省略して入力した際に,デフォルトで使うユーザ名
    * bastion
        * 踏み台サーバの設定,必要な情報は下記
        * server
            * 踏み台にするサーバ名.他で設定したマシン名を設定
        * user
            * 踏み台サーバにログインする際のユーザ名
    * users
        * 対象サーバのユーザ情報を記述.
        * USER_NAME
            * usersのすぐ下に設定するキー名.これを対象サーバにログインする際のユーザ名とする
            * authentication
                * passwordかkey(公開鍵認証方式）かを設定
            * password
                * authenticationでpasswordを選んだ場合,設定
            * key
                * authenticationでkeyを選んだ場合,秘密鍵の場所を設定
            * bastion
                * 経由するユーザ.rootユーザなど,直接ログインできないようなユーザに対して使う.
    * command
        * ログイン後に実行するコマンド
    * extends
        * ここには他で設定したマシン名を設定する.設定されたマシンの接続情報と同じものを使用する.これを設定した後に,再度設定を行なうと,再度設定した内容で上書きする.接続情報がほとんど同じだが,IPアドレスのみ異なる,といったときに便利に使える.

## Licence
MIT Licence