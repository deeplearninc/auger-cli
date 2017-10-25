# -*- coding: utf-8 -*-

import os
import subprocess


def call(*args, **kwargs):
    if kwargs.get('silent'):
        return subprocess.check_output(
            args,
            cwd=os.path.curdir,
            env=os.environ.copy(),
            shell=True,
            stderr=subprocess.STDOUT
        )
    else:
        return subprocess.check_call(
            args,
            cwd=os.path.curdir,
            env=os.environ.copy()
        )
