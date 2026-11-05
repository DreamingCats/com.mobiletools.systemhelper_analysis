"""Create narrowly selected, redacted SystemHelper log excerpts. WTFPL-2.0."""
import argparse
import json
import re
from pathlib import Path

PACKAGE = 'com.mobiletools.systemhelper'

def redact(text, uid):
    text = re.sub(r'(?<!\d)' + re.escape(uid) + r'(?!\d)', '<APP_UID>', text)
    text = re.sub(r'\bu0a\d+\b', '<APP_USER>', text)
    text = re.sub(r'subscriberId=[^,}\]]+', 'subscriberId=<REDACTED>', text)
    text = re.sub(r'wifiNetworkKey=.*?(?=, metered=)', 'wifiNetworkKey=<REDACTED>', text)
    text = re.sub(r'\b(?:ceDataInode|deDataInode)=\d+', '<INODE_REDACTED>', text)
    text = re.sub(r'(?i)\b(time|rejectTime)=[^;]+', r'\1=<RELATIVE_TIME_REDACTED>', text)
    text = re.sub(r'\bst=\d+', 'st=<BUCKET_TIME_REDACTED>', text)
    text = re.sub(r'\blast -\S+', 'last <RELATIVE_TIME_REDACTED>', text)
    text = re.sub(r'(?<=\{)[0-9a-f]{5,}(?=\s)', '<OBJECT>', text)
    text = re.sub(r'(?<=\()[0-9a-f]{5,}(?=\))', '<OBJECT>', text)
    text = re.sub(r'\b(?:origWhen|whenElapsed|maxWhenElapsed) \d+', '<ELAPSED_TIME_REDACTED>', text)
    return text

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Private evidence directory')
    parser.add_argument('--output', type=Path, required=True, help='New public excerpts directory')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    package_lines = (args.input/'package.txt').read_text(encoding='utf-8-sig').splitlines()
    uid = re.search(r'^\s+appId=(\d+)', '\n'.join(package_lines), re.M).group(1)
    manifest = {'kind': 'selected_and_redacted_real_device_logs', 'collection_phase': 'before_owner_uninstall',
                'model': 'realme GT5 Pro (RMX3888)', 'date': '2026-11-05',
                'omissions': ['other-package sections', 'application inventory and usage item details',
                              'device and SIM identifiers', 'location coordinates', 'SSID/BSSID',
                              'client IP addresses', 'exact activity timestamps', 'object and user identifiers'], 'files': {}}
    def write(name, source, selected):
        value='\n'.join(redact(line, uid) for number, line in selected)
        if value:
            value += '\n'
        (args.output/name).write_text(value, encoding='utf-8', newline='\n')
        manifest['files'][name] = {'source_basename': source, 'source_line_numbers': [number for number, line in selected]}

    selected=[]
    section=''
    runtime_seen=False
    for number,line in enumerate(package_lines,1):
        if line == 'Packages:': section='package'
        elif line == 'Queries:': section='skip'
        elif line == 'Shared users:': section='shared'
        elif line == 'Dexopt state:': section='skip'
        if section == 'package':
            if re.match(r'^\s+(Package \[|appId=|sharedUser=|codePath=|versionCode=|versionName=|apkSigningVersion=|flags=|privateFlags=|requested permissions:|install permissions:|User 0:|android\.permission\.)',line):
                selected.append((number,line))
        elif section == 'shared':
            if 'User 999:' in line: section='skip'
            elif 'runtime permissions:' in line: runtime_seen=True; selected.append((number,line))
            elif runtime_seen and 'android.permission.' in line: selected.append((number,line))
    write('package.redacted.txt','package.txt',selected)

    lines=(args.input/'appops.txt').read_text(encoding='utf-8-sig').splitlines()
    ops=('COARSE_LOCATION:', 'FINE_LOCATION:', 'WIFI_SCAN:', 'GET_USAGE_STATS:', 'USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER:')
    write('appops.redacted.txt','appops.txt',[(i,l) for i,l in enumerate(lines,1) if l.startswith(ops)])

    lines=(args.input/'alarms.txt').read_text(encoding='utf-8-sig').splitlines()
    selected=[]
    stats=False
    for i,line in enumerate(lines,1):
        if PACKAGE in line and ('Alarm{' in line or 'tag=*' in line): selected.append((i,line))
        if re.match(r'^  u0a\d+:'+re.escape(PACKAGE)+r' ',line): stats=True
        elif stats and re.match(r'^  \S',line): stats=False
        if stats: selected.append((i,line))
    write('alarms.redacted.txt','alarms.txt',selected)

    lines=(args.input/'netstats.txt').read_text(encoding='utf-8-sig').splitlines()
    selected=[]
    active=False
    total={'rx_bytes':0,'tx_bytes':0,'buckets':0}
    for i,line in enumerate(lines,1):
        if line.startswith('  ident='):
            active=bool(re.search(r'\buid='+re.escape(uid)+r'\b',line)) and 'tag=0x0' in line
            if active: selected.append((i,line))
        elif active:
            if 'NetworkStatsHistory:' in line: selected.append((i,line))
            elif re.match(r'^\s+st=\d+',line):
                selected.append((i,line))
                values=dict(re.findall(r'\b(rb|tb)=(\d+)',line))
                total['rx_bytes']+=int(values['rb'])
                total['tx_bytes']+=int(values['tb'])
                total['buckets']+=1
            elif line.strip(): active=False
    write('netstats.redacted.txt','netstats.txt',selected)
    manifest['network_untagged_totals']=total

    lines=(args.input/'rom_references.txt').read_text(encoding='utf-8-sig').splitlines()
    write('rom-references.redacted.txt','rom_references.txt',[(i,l) for i,l in enumerate(lines,1) if PACKAGE in l])
    logcat=args.input/'app_logcat_root.txt'
    if logcat.stat().st_size == 0:
        (args.output/'app-logcat-root.empty.txt').write_bytes(b'')
        manifest['files']['app-logcat-root.empty.txt']={'source_basename':logcat.name,'source_line_numbers':[],'source_bytes':0}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'files':len(manifest['files']),'network_totals':total},ensure_ascii=False))

if __name__ == '__main__':
    main()
