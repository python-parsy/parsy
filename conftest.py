import sys

collect_ignore = []

if sys.version_info < (3, 7):
    # Python 3.6 and below don't have `dataclasses`
    collect_ignore = ["examples/sql_select.py"]
