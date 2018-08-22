#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
import sys
import logging

current_file_path = os.path.dirname(os.path.abspath(__file__))
ci_path = os.path.abspath(os.path.join(current_file_path, '..'))
if ci_path not in sys.path:
    sys.path.append(ci_path)

from configuration import LOGGING_LEVEL, ENVIRONMENT_VARIABLES, PREREQUISITES
from library import (setup_logging,
                     get_project_root_path,
                     validate_prerequisites,
                     is_venv_created,
                     execute_command,
                     load_environment_variables,
                     load_dot_env_file,
                     activate_virtual_environment,
                     get_emojize)

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.bootstrap'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def bootstrap():
    setup_logging(os.environ.get("LOGGING_LEVEL") or LOGGING_LEVEL)
    load_environment_variables(ENVIRONMENT_VARIABLES)
    load_dot_env_file()
    if not validate_prerequisites(PREREQUISITES):
        LOGGER.error('Prerequisite missing, cannot continue.')
        raise SystemExit(1)
    if not is_venv_created():
        LOGGER.debug('Trying to create virtual environment.')
        exit_code = execute_command('pipenv install --dev --ignore-pipfile')
        success = not exit_code
        if success:
            activate_virtual_environment()
            emojize = get_emojize()
            LOGGER.info('%s Successfully created virtual environment and loaded it! %s',
                        emojize(':white_heavy_check_mark:'),
                        emojize(':thumbs_up:'))
        else:
            LOGGER.error('Creation of virtual environment failed, cannot continue, '
                         'please clean up .venv directory and try again...')
            raise SystemExit(1)
    return get_emojize()


if __name__ == '__main__':
    bootstrap()
