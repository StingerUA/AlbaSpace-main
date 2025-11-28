#!/usr/bin/env python3
import re, os, shutil, sys, datetime

root='.'
pattern = re.compile(r'(<img\b(?![^>]*\bloading=)([^>]*?))(\s*/?)>', re.IGNORECASE|re.DOTALL)

changed_files = []

for dirpath, dirs, files in os.walk(root):
    # skip asset folders that usually end with "_files"
    if any(p.endswith('_files') for p in dirpath.split(os.sep)):
        continue
    for name in files:
        if not name.lower().endswith('.html'):
            continue
        filepath = os.path.join(dirpath, name)
        if filepath.endswith('.bak'):
            continue
        with open(filepath, 'rb') as fh:
            try:
                raw = fh.read().decode('utf-8')
            except Exception:
                # fallback to latin-1 if not utf-8
                raw = fh.read().decode('latin-1')
        matches = list(pattern.finditer(raw))
        if not matches:
            continue
        # prepare backup, don't overwrite existing .bak
        bakpath = filepath + '.bak'
        if os.path.exists(bakpath):
            now = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
            bakpath = filepath + '.bak.' + now
        shutil.copy2(filepath, bakpath)
        # produce modified content
        def repl(m):
            # m.group(1) is <img ... (without trailing slash/>)
            prefix = m.group(1)
            slash = m.group(3) or ''
            return f"{prefix} loading=\"lazy\"{slash}>"
        new_raw = pattern.sub(repl, raw)

        # write file only if content changes
        if new_raw != raw:
            with open(filepath, 'wb') as fh:
                try:
                    fh.write(new_raw.encode('utf-8'))
                except Exception:
                    fh.write(new_raw.encode('latin-1'))
            # collect before/after snippets for reporting
            before_lines = [m.group(0).strip().replace('\n',' ') for m in matches]
            after_lines = [repl(m).strip().replace('\n',' ') for m in matches]
            changed_files.append((filepath, bakpath, list(zip(before_lines, after_lines))))

# print concise report
if not changed_files:
    print('No files required modification.')
    sys.exit(0)

print('Modified files:')
for filepath, bakpath, diffs in changed_files:
    print('\n-- ' + filepath)
    print('  bak:', bakpath)
    for bef, aft in diffs[:20]:
        print('  - BEFORE: ' + bef)
        print('    AFTER : ' + aft)

print('\nTotal modified files:', len(changed_files))
