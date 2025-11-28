#!/usr/bin/env python3
"""Удаляет <astro-island> элементы и inline-скрипты, содержащие 'Astro',
из всех HTML файлов в рабочем каталоге. Создаёт резервные копии *.html.bak
и пишет список изменённых файлов в /tmp/removed_astro_files.txt

Использование: запустить в корне репозитория:
    python3 scripts/remove_astro_islands.py
"""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT_LIST = Path("/tmp/removed_astro_files.txt")

def process_file(p: Path):
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        text = p.read_text(encoding='latin-1', errors='replace')

    orig = text

    # 1) Удаляем все <astro-island ...>...</astro-island>, сохраняя внутреннее содержимое
    text = re.sub(r"<astro-island\b[^>]*>(.*?)</astro-island>", r"\1", text, flags=re.DOTALL|re.IGNORECASE)

    # 2) Удаляем любые <script>...</script>, которые содержат слова Astro или astro:load или self.Astro
    text = re.sub(r"<script\b[^>]*>.*?(?:Astro|astro:load|self\\.Astro).*?</script>", "", text, flags=re.DOTALL|re.IGNORECASE)

    # 3) Удаляем пустые комментарии/лишние пустые строки, если появились подряд
    text = re.sub(r"\n{3,}", "\n\n", text)

    if text != orig:
        bak = p.with_name(p.name + '.bak')
        if not bak.exists():
            shutil.copy2(p, bak)
        p.write_text(text, encoding='utf-8')
        return True
    return False

def main():
    changed = []
    html_files = [p for p in ROOT.rglob('*.html') if not p.name.endswith('.bak')]
    for p in html_files:
        # skip backup files and files in node_modules/.git etc (if any)
        if '/.git/' in str(p) or '/node_modules/' in str(p):
            continue
        try:
            if process_file(p):
                changed.append(str(p))
        except Exception as e:
            print(f'ERROR processing {p}: {e}', file=sys.stderr)

    OUT_LIST.write_text('\n'.join(changed), encoding='utf-8')
    print(f'Processed {len(html_files)} HTML files, modified {len(changed)} files.')
    print(f'List of modified files written to {OUT_LIST}')

if __name__ == '__main__':
    main()
