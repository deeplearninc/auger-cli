# -*- coding: utf-8 -*-

import unittest
import vcr
from auger_cli.commands.auth.cli import cli
from click.testing import CliRunner


class TestLogin(unittest.TestCase):

    @vcr.use_cassette(
        'tests/fixtures/cassettes/commands/login_success.yaml',
        filter_headers=['authorization']
    )
    def test_login_success(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                'login',
                '--password',
                'foo123',
                '--username',
                'valid@auger.ai',
                '--url',
                'http://localhost:5000',
            ]
        )
        print(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            'You are now logged in on localhost as valid@auger.ai.\n',
            result.output
        )


class TestLogout(unittest.TestCase):

    @vcr.use_cassette(
        'tests/fixtures/cassettes/commands/logout_success.yaml',
        filter_headers=['authorization']
    )
    def test_logout_success(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['logout'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            'You are now logged out.\n',
            result.output
        )
