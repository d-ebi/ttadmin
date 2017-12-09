# -*- coding: utf-8 -*-

import copy
import logging
import logging.config
import os
import subprocess
import sys

sys.path.append('..')
import settings

class ConnectionInfoCreator():
    def __init__(self, server, user=None):
        '''
        コンストラクタ.
        settings.pyの内容をロードする.

        @param server 対象サーバ名
        @param user ログインユーザ名
        '''

        self.add_args = str()
        self.create_server_info(server, user)
        self.create_user_info()

    def get_server_infos(self):
        '''
        サーバ情報をsettings.pyから取得する.
        グルーピング部分を除外する.

        @return 除外したdict()
        '''

        server_infos = dict()
        [ server_infos.update(value) for value in settings.infos.values() ]

        return server_infos

    def get_server_info(self, server):
        '''
        サーバ各々の情報を取得する.

        @param server サーバ名
        @return 取得したサーバ情報
        '''

        server_info = self.get_server_infos()[server]
        if 'extends' in server_info:
            not_extends_values = copy.deepcopy(server_info)
            server_info = self.get_server_infos()[not_extends_values['extends']]
            del not_extends_values['extends']
            server_info.update(not_extends_values)

        return server_info

    def create_server_info(self, server, user):
        '''
        接続に必要な情報を作成する.
        踏み台サーバがある場合,それらを経由してログインするように
        情報を構築する.

        @param server サーバ名
        @param user ユーザ名
        '''

        server_info = self.get_server_info(server)
        user = user if user else server_info['default_user']
        if 'bastion' in server_info:
            user_info = server_info['users'][user]
            login_user = user if not 'bastion' in user_info else user_info['bastion']
            self.add_args = self.get_ssh_command(
                server_info['host'],
                login_user,
                server_info['port'],
                server_info['users'][login_user]['password'])
            self.add_args += self.get_add_command(server_info)
            self.server = server
            self.user = user
            self.create_user_info()
            user = server_info['bastion']['user']
            server = self.get_server_info(server)['bastion']['server']
            server_info = self.get_server_info(server)
        self.add_args += self.get_add_command(server_info)
        self.server = server
        self.user = user if user else server_info['default_user']
        self.host = server_info['host']
        self.port = server_info['port']

    def get_add_command(self, server_info):
        '''
        追加コマンドがある場合,コマンドを構築する.

        @param server_info 対象サーバの情報群
        @return 追加コマンド文字列
        '''

        if not 'command' in server_info:
            return ''
        command = ' ' if self.add_args else ''
        command += '"{0}"'.format(server_info['command'])

        return command

    def create_user_info(self):
        '''
        接続に必要なユーザ情報を作成する.
        踏み台ユーザがある場合,それらを経由してログインするように
        情報を構築する.
        '''

        server_info = self.get_server_info(self.server)
        user_info = server_info['users'][self.user]
        if 'bastion' in user_info:
            self.add_args = self.add_args + ' ' if self.add_args else ''
            self.add_args = self.add_args + self.get_su_command(self.user, user_info['password'])
            self.user = server_info['users'][self.user]['bastion']
            user_info = server_info['users'][self.user]
        self.authentication = user_info['authentication']
        self.password_or_key = user_info[self.authentication]

    def get_ssh_command(self, host, user=None, port=None, password=None):
        '''
        踏み台サーバがある場合,踏み台ログイン後に別サーバにログインするため,
        それ用のsshコマンドを構築する.

        @param host 対象サーバのIPアドレスないしホスト名
        @param user ユーザ名
        @param port ポート番号
        @param password ログインパスワード
        @return sshコマンド文字列
        '''

        ssh_command = '"ssh {host} {options}" {password}'
        user_option = '' if not user else '-l {0}'.format(user)
        port_option = '' if not port else '-p {0}'.format(port)
        password = '' if not password else password

        return ssh_command.format(host=host, password=password, options=' '.join([
            user_option,
            port_option
        ]))

    def get_su_command(self, user, password):
        '''
        踏み台ユーザがある場合,サーバログイン後にユーザを変更するため,
        それ用のsuコマンドを構築する.

        @param user ユーザ名
        @param password パスワード
        @return suコマンド文字列
        '''

        user = '' if user == 'root' else ' ' + user
        su_command = 'su{0}'.format(user)

        return ' '.join([su_command, password])

def main():
    '''
    メインロジック.
    '''

    user = None if len(sys.argv) < 3 else sys.argv[2]
    con = ConnectionInfoCreator(sys.argv[1], user)
    ttl_path = os.path.dirname(os.path.abspath(__file__)) + '/connection_macro.ttl'
    cmd = '"C:/Program Files (x86)/teraterm/ttpmacro.exe" ' + ttl_path
    execute_command = '{cmd} {host} {port} {user} {authentication} {password_or_key} {add_args}'
    execute_command = execute_command.format(
        cmd=cmd,
        host=con.host,
        port=con.port,
        user=con.user,
        authentication=con.authentication,
        password_or_key=con.password_or_key,
        add_args=con.add_args)
    try:
        returncode = subprocess.call(execute_command)
    except Exception as e:
        raise e

logging.config.fileConfig('../src/logging.conf')
try:
    main()
except Exception as e:
    logging.error(e)
