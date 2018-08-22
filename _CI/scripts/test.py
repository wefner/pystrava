#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
#
# Copyright 2018 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
import logging
import os
from time import sleep

# this needs to be imported first as it manipulates the path
from bootstrap import bootstrap
from library import (open_file,
                     clean_up,
                     execute_command,
                     save_requirements)

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.test'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def test():
    emojize = bootstrap()
    clean_up('test-output')
    os.mkdir('test-output')
    # exit_code = execute_command('pipenv lock')
    # success = not exit_code
    # if success:
    #     LOGGER.info('Successfully created lock file %s',
    #                  emojize(':white_heavy_check_mark:'),
    #                  emojize(':thumbs_up:'))
    # else:
    #     LOGGER.error('%s Errors creating lock file! %s',
    #                   emojize(':cross_mark:'),
    #                   emojize(':crying_face:'))
    #     raise SystemExit(1)
    save_requirements()
    exit_code = execute_command('tox')
    success = not exit_code
    if success:
        open_file(os.path.join('test-output', 'coverage', 'index.html'))
        sleep(0.5)
        open_file(os.path.join('test-output', 'nosetests.html'))
        LOGGER.info('%s No testing errors found! %s',
                    emojize(':white_heavy_check_mark:'),
                    emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Testing errors found! %s',
                     emojize(':cross_mark:'),
                     emojize(':crying_face:'))
    raise SystemExit(exit_code)


if __name__ == '__main__':
    test()
