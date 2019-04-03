# -*- coding: utf-8 -*-

import unittest
import vcr
from auger_cli.commands.auth import auth_group
from click.testing import CliRunner


class TestLogin(unittest.TestCase):

    @vcr.use_cassette(
        'tests/fixtures/cassettes/commands/login_success.yaml',
        filter_headers=['authorization']
    )
    def test_login_success(self):
        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            [
                'login',
                '--username',
                'her@mail.com',
                '--password',
                'password',
                '--url',
                'http://localhost:5000',
            ]
        )

        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            result.output.endswith('You are now logged in on http://localhost:5000 as her@mail.com.\n')
        )


class TestLogout(unittest.TestCase):

    def test_logout_success(self):
        runner = CliRunner()
        result = runner.invoke(auth_group, ['logout'])
        self.assertEqual(0, result.exit_code, result.output)
        self.assertTrue(
            result.output.endswith(
            'You are now logged out.\n',
            )
        )
