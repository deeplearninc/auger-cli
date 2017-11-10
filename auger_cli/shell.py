# -*- coding: utf-8 -*-

import os
import subprocess


def call(args, input_string='', silent=False):
    input_bytes = (input_string.strip() + '\n').encode('utf-8')
    if silent:
        return subprocess.check_call(
            args,
            input=input_bytes,
            cwd=os.path.curdir,
            env=os.environ.copy()
        )
    else:
        return subprocess.check_output(
            args,
            input=input_bytes,
            cwd=os.path.curdir,
            env=os.environ.copy(),
            shell=True,
            stderr=subprocess.STDOUT
        )
