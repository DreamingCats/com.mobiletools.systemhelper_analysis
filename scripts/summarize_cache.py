"""Summarize a private SystemHelper SQLite copy without emitting payload values.

Original code, WTFPL Version 2. Opens the supplied database read-only.
"""
import argparse
import json
import sqlite3
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database',type=Path)
    args=parser.parse_args()
    database=sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)
    tables={row[0] for row in database.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    summary={'integrity_check':database.execute('PRAGMA integrity_check').fetchone()[0],'tables':{}}
    for name in ['dmregister','signal']:
        if name not in tables:
            continue
        payloads=[json.loads(row[0]) for row in database.execute(f'SELECT jsonString FROM {name}')]
        apps=[obj['AppInfo'] for obj in payloads if isinstance(obj.get('AppInfo'),list)]
        signals=[obj['SigInfo'] for obj in payloads if isinstance(obj.get('SigInfo'),list)]
        summary['tables'][name]={
            'rows':len(payloads),
            'top_level_keys':sorted({key for obj in payloads for key in obj}),
            'app_entry_counts':[len(items) for items in apps],
            'nonzero_foreground_counts':[sum(item.get('runTime','0min') not in ('','0min','0') for item in items) for items in apps],
            'nested_signal_counts':[len(items) for items in signals],
            'note':'No per-record values, application names, package names, identifiers, coordinates, IP addresses or timestamps emitted.'
        }
    database.close()
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
