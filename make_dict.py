#!/usr/bin/env python3
"""
make_dict.py — собирает толковый словарь из Викисловаря для твоих слов
и сохраняет в формат StarDict (для GoldenDict и других программ)

Использование:
    python make_dict.py vocab.tsv

Что делает:
    1. Читает твой vocab.tsv
    2. Скачивает дамп русского Викисловаря (~300 МБ, один раз)
    3. Парсит определения
    4. Сохраняет совпавшие слова в StarDict (.ifo / .idx / .dict)

Зависимости:
    pip install requests
"""

import re
import sys
import bz2
import struct
import struct
import requests
from pathlib import Path
from xml.etree import ElementTree as ET

# ── настройки ─────────────────────────────────────────────────────────────────

DUMP_URL = "https://dumps.wikimedia.org/ruwiktionary/latest/ruwiktionary-latest-pages-articles.xml.bz2"
DUMP_FILE = Path("ruwiktionary.xml.bz2")
OUT_NAME  = "my_dictionary"  # имя выходных файлов StarDict

# ── шаг 1: загрузить дамп ─────────────────────────────────────────────────────

def download_dump():
    if DUMP_FILE.exists():
        print(f"✓ Дамп уже скачан: {DUMP_FILE} ({DUMP_FILE.stat().st_size // 1_000_000} МБ)")
        return
    print("Скачиваю дамп Викисловаря (~300 МБ)...")
    print("  Это займёт несколько минут, только один раз.\n")
    with requests.get(DUMP_URL, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(DUMP_FILE, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    mb  = downloaded // 1_000_000
                    print(f"\r  {mb} МБ / {total // 1_000_000} МБ  ({pct}%)", end="", flush=True)
    print(f"\n✓ Скачано: {DUMP_FILE}")

# ── шаг 2: парсить викисловарь ────────────────────────────────────────────────

# Секции которые нас интересуют
SECTION_RE = re.compile(r"^={2,4}\s*(.+?)\s*={2,4}$", re.MULTILINE)
MEANING_RE  = re.compile(r"^#\s*(.+)$", re.MULTILINE)

SKIP_SECTIONS = {
    "Морфологические и синтаксические свойства",
    "Произношение", "Семантические свойства",
    "Синонимы", "Антонимы", "Гиперонимы", "Гипонимы",
    "Родственные слова", "Этимология", "Библиография",
    "Фразеологизмы и устойчивые сочетания",
    "Переводы", "Анаграммы", "Примечания", "Ссылки",
    "Метаграммы", "Паронимы",
}

def clean_wikitext(text: str) -> str:
    """Убирает вики-разметку из текста определения."""
    # [[ссылка|текст]] → текст, [[слово]] → слово
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    # {{шаблон|...}} → убрать
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    # ''курсив'' и '''жирный'''
    text = re.sub(r"'{2,3}", "", text)
    # HTML теги
    text = re.sub(r"<[^>]+>", "", text)
    # множественные пробелы
    text = re.sub(r"  +", " ", text)
    return text.strip()

def extract_definitions(wikitext: str) -> list[str]:
    """Вытаскивает значения (строки начинающиеся с #) из статьи."""
    definitions = []
    # Найти секцию "Значение" или "Значения"
    sections = SECTION_RE.split(wikitext)
    in_meaning = False
    for part in sections:
        if re.match(r"Значени[ея]", part):
            in_meaning = True
            continue
        if in_meaning:
            # Вытащить строки с #
            for m in MEANING_RE.finditer(part):
                line = clean_wikitext(m.group(1))
                # Убрать служебные пометки типа [устар.] [разг.]
                line = re.sub(r"^\[.*?\]\s*", "", line)
                if line and len(line) > 3:
                    definitions.append(line)
            in_meaning = False
    return definitions

def parse_wiktionary(vocab: set[str]) -> dict[str, str]:
    """Парсит дамп и возвращает {слово: определение} для слов из vocab."""
    print("\nПарсю дамп Викисловаря...")
    found: dict[str, str] = {}
    ns_wiki = "http://www.mediawiki.org/xml/DTD/mediawiki"

    def strip_ns(tag):
        return tag.split("}")[-1] if "}" in tag else tag

    with bz2.open(DUMP_FILE, "rb") as f:
        page_title = None
        page_text  = None
        count = 0
        found_count = 0
        context = ET.iterparse(f, events=("start", "end"))
        root = None

        for event, elem in context:
            tag = strip_ns(elem.tag)

            if event == "start" and tag == "mediawiki":
                root = elem

            elif event == "end" and tag == "title":
                page_title = elem.text

            elif event == "end" and tag == "text":
                page_text = elem.text

            elif event == "end" and tag == "page":
                if page_title and page_text:
                    title_lower = page_title.lower()
                    if title_lower in vocab:
                        defs = extract_definitions(page_text)
                        if defs:
                            entry = "\n".join(f"{i+1}. {d}" for i, d in enumerate(defs[:3]))
                            found[title_lower] = entry
                            found_count += 1

                count += 1
                if count % 50000 == 0:
                    print(f"  Обработано страниц: {count:,}  |  Найдено: {found_count:,}")

                # Освобождаем память — ключевое исправление
                elem.clear()
                if root is not None:
                    del root[:]

    print(f"\n✓ Обработано страниц: {count:,}")
    print(f"✓ Найдено определений: {found_count:,} из {len(vocab):,} слов")
    return found

# ── шаг 3: сохранить StarDict ─────────────────────────────────────────────────

def save_stardict(entries: dict[str, str], name: str):
    """
    StarDict состоит из трёх файлов:
      .idx  — индекс: слово\0 + offset(4б) + size(4б)
      .dict — тело: определения подряд
      .ifo  — метаданные
    """
    print(f"\nСохраняю StarDict: {name}.*")

    words = sorted(entries.keys())

    idx_data  = b""
    dict_data = b""
    offset = 0

    for word in words:
        definition = entries[word].encode("utf-8")
        size = len(definition)

        # idx запись: слово + \0 + offset (big-endian uint32) + size (big-endian uint32)
        idx_data  += word.encode("utf-8") + b"\x00" + struct.pack(">II", offset, size)
        dict_data += definition
        offset    += size

    # Записать файлы
    idx_path  = Path(f"{name}.idx")
    dict_path = Path(f"{name}.dict")
    ifo_path  = Path(f"{name}.ifo")

    idx_path.write_bytes(idx_data)
    dict_path.write_bytes(dict_data)

    ifo_content = (
        "StarDict's dict ifo file\n"
        "version=2.4.2\n"
        f"wordcount={len(words)}\n"
        f"idxfilesize={len(idx_data)}\n"
        f"bookname=Мой словарь (Викисловарь)\n"
        "sametypesequence=m\n"
    )
    ifo_path.write_text(ifo_content, encoding="utf-8")

    print(f"✓ {ifo_path}  ({len(words):,} слов)")
    print(f"✓ {idx_path}  ({len(idx_data):,} байт)")
    print(f"✓ {dict_path} ({len(dict_data):,} байт)")

# ── шаг 4: отчёт о ненайденных ───────────────────────────────────────────────

def save_missing(vocab: set[str], found: dict[str, str]):
    missing = sorted(vocab - set(found.keys()))
    if not missing:
        return
    path = Path("missing_words.txt")
    path.write_text("\n".join(missing), encoding="utf-8")
    print(f"\n  Не найдено в Викисловаре: {len(missing):,} слов → {path}")
    print("  (обычно это имена собственные, опечатки, редкие слова)")

# ── main ──────────────────────────────────────────────────────────────────────

def load_vocab(path: str) -> set[str]:
    vocab = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.strip().split("\t")
        if parts:
            vocab.add(parts[0].lower())
    return vocab

def main():
    if len(sys.argv) < 2:
        print("Использование: python make_dict.py vocab.tsv")
        sys.exit(1)

    vocab_path = sys.argv[1]
    print(f"Читаю словарь: {vocab_path}")
    vocab = load_vocab(vocab_path)
    print(f"✓ Слов в словаре: {len(vocab):,}")

    # 1. Скачать дамп
    download_dump()

    # 2. Распарсить
    found = parse_wiktionary(vocab)

    # 3. Сохранить StarDict
    save_stardict(found, OUT_NAME)

    # 4. Отчёт о ненайденных
    save_missing(vocab, found)

    print("\n═══════════════════════════════════════")
    print("  Готово! Открой GoldenDict и добавь папку")
    print(f"  с файлами {OUT_NAME}.ifo/.idx/.dict")
    print("═══════════════════════════════════════")

if __name__ == "__main__":
    main()
