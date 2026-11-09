"""Compare two locally supplied APK archives without distributing their contents.

Original code, WTFPL Version 2. Standard library only; no device or network calls.
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

def compare(left, right):
    with zipfile.ZipFile(left) as old, zipfile.ZipFile(right) as new:
        old_items={item.filename:item.file_size for item in old.infolist() if not item.is_dir()}
        new_items={item.filename:item.file_size for item in new.infolist() if not item.is_dir()}
        identical=[]
        changed=[]
        for name in sorted(old_items.keys() & new_items.keys()):
            if old.read(name)==new.read(name):
                identical.append(name)
            else:
                changed.append({'path':name,'left_uncompressed_bytes':old_items[name],'right_uncompressed_bytes':new_items[name]})
        return {
            'left':{'bytes':left.stat().st_size,'sha256':hashlib.sha256(left.read_bytes()).hexdigest(),'entry_count':len(old_items)},
            'right':{'bytes':right.stat().st_size,'sha256':hashlib.sha256(right.read_bytes()).hexdigest(),'entry_count':len(new_items)},
            'added':sorted(new_items.keys()-old_items.keys()),
            'removed':sorted(old_items.keys()-new_items.keys()),
            'changed':changed,
            'byte_identical':identical,
            'note':'Archive comparison only; equality does not prove runtime behavior. No entry contents emitted.'
        }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('left',type=Path)
    parser.add_argument('right',type=Path)
    args=parser.parse_args()
    print(json.dumps(compare(args.left,args.right),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
