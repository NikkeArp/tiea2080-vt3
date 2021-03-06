#!venv/bin/python
# -*- coding: utf-8 -*-

import sys
import linecache

def log_exception(logger=None):
    try:
        exc_obj, tb = sys.exc_info()[1:]
        f = tb.tb_frame
        line_num = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, line_num, f.f_globals)
        message = '''Exception occured in ( {0},
                            line {1}, "{2}" )
                                {3}'''.format(filename, line_num, line.strip(), exc_obj)
        if logger:
            logger.debug(message)
        return message
        
    finally:
        del tb; del exc_obj