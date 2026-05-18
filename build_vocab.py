#!/usr/bin/env python3
"""
build_vocab.py — строит словарь из папки с книгами (fb2, txt, epub)

Использование:
    python build_vocab.py books/          # папка с книгами
    python build_vocab.py books/ --min-count 5 --top 50000
    python build_vocab.py books/ --format hunspell --output mydict.dic

Опции:
    --min-count   минимальная частота леммы (по умолчанию: 3)
    --top         оставить только N самых частых слов (по умолчанию: все)
    --format      txt | tsv | hunspell (по умолчанию: tsv)
    --output      имя выходного файла (по умолчанию: vocab.tsv)
    --lang        ru | en (по умолчанию: ru)
    --no-lemma    не лемматизировать, работать с сырыми словоформами
"""

import re
import sys
import argparse
import zipfile
from pathlib import Path
from collections import Counter

# ── зависимости ──────────────────────────────────────────────────────────────

def check_deps(lang, lemmatize):
    missing = []
    try:
        from lxml import etree  # noqa
    except ImportError:
        missing.append("lxml")
    if lemmatize and lang == "ru":
        try:
            import pymorphy3  # noqa
        except ImportError:
            missing.append("pymorphy3")
    if missing:
        print(f"[!] Не хватает библиотек: {', '.join(missing)}")
        print(f"    Установите: pip install {' '.join(missing)}")
        sys.exit(1)

# ── парсеры форматов ──────────────────────────────────────────────────────────

def read_txt(path: Path) -> str:
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return ""

def read_fb2(path: Path) -> str:
    from lxml import etree
    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError:
        print(f"  [!] Не удалось разобрать fb2: {path.name}")
        return ""
    # fb2 может быть с пространством имён или без
    root = tree.getroot()
    texts = []
    for el in root.iter():
        if el.text:
            texts.append(el.text)
        if el.tail:
            texts.append(el.tail)
    return " ".join(texts)

def read_epub(path: Path) -> str:
    from lxml import etree
    texts = []
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.endswith((".html", ".xhtml", ".htm")):
                    raw = z.read(name)
                    try:
                        tree = etree.fromstring(raw)
                        texts.append(" ".join(tree.itertext()))
                    except Exception:
                        # fallback: убрать теги регуляркой
                        texts.append(re.sub(r"<[^>]+>", " ", raw.decode("utf-8", errors="ignore")))
    except zipfile.BadZipFile:
        print(f"  [!] Плохой epub: {path.name}")
    return " ".join(texts)

READERS = {
    ".txt": read_txt,
    ".fb2": read_fb2,
    ".epub": read_epub,
}

def read_file(path: Path) -> str:
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        return ""
    print(f"  Читаю: {path.name}")
    return reader(path)

# ── обработка текста ──────────────────────────────────────────────────────────

RU_PATTERN = re.compile(r"[а-яёa-z]+", re.IGNORECASE)

def tokenize(text: str, lang: str) -> list[str]:
    tokens = RU_PATTERN.findall(text.lower())
    if lang == "ru":
        # оставляем только русские слова
        return [t for t in tokens if re.fullmatch(r"[а-яё]+", t)]
    else:
        return [t for t in tokens if re.fullmatch(r"[a-z]+", t)]

def build_freq(paths: list[Path], lang: str) -> Counter:
    freq: Counter = Counter()
    for path in paths:
        text = read_file(path)
        if not text:
            continue
        tokens = tokenize(text, lang)
        freq.update(tokens)
        print(f"    → {len(tokens):,} токенов, уникальных форм: {len(freq):,}")
    return freq

def lemmatize_ru(freq: Counter) -> Counter:
    import pymorphy3
    morph = pymorphy3.MorphAnalyzer()
    lemma_freq: Counter = Counter()
    total = len(freq)
    for i, (word, count) in enumerate(freq.items(), 1):
        if i % 10000 == 0:
            print(f"  Лемматизация: {i:,}/{total:,}...")
        lemma = morph.parse(word)[0].normal_form
        lemma_freq[lemma] += count
    return lemma_freq

# ── фильтрация ────────────────────────────────────────────────────────────────

def filter_vocab(freq: Counter, min_count: int, top: int | None) -> list[tuple[str, int]]:
    filtered = [(w, c) for w, c in freq.items() if c >= min_count and len(w) >= 2]
    filtered.sort(key=lambda x: x[1], reverse=True)
    if top:
        filtered = filtered[:top]
    return filtered

# ── сохранение ────────────────────────────────────────────────────────────────

def save_txt(vocab: list[tuple[str, int]], path: Path):
    path.write_text("\n".join(w for w, _ in vocab), encoding="utf-8")
    print(f"\n✓ Сохранено {len(vocab):,} слов → {path}")

def save_tsv(vocab: list[tuple[str, int]], path: Path):
    lines = [f"{w}\t{c}" for w, c in vocab]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ Сохранено {len(vocab):,} слов (с частотами) → {path}")

def save_hunspell(vocab: list[tuple[str, int]], path: Path):
    lines = [str(len(vocab))] + [w for w, _ in vocab]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ Hunspell .dic: {len(vocab):,} слов → {path}")
    print("  (не забудьте парный .aff файл для проверки орфографии)")

SAVERS = {
    "txt": save_txt,
    "tsv": save_tsv,
    "hunspell": save_hunspell,
}

# ── статистика ────────────────────────────────────────────────────────────────

def print_stats(vocab: list[tuple[str, int]]):
    if not vocab:
        return
    total_tokens = sum(c for _, c in vocab)
    print(f"\n{'─'*40}")
    print(f"  Уникальных слов:  {len(vocab):>10,}")
    print(f"  Всего токенов:    {total_tokens:>10,}")
    print(f"  Топ-10 слов:")
    for word, count in vocab[:10]:
        print(f"    {word:<20} {count:,}")
    print(f"{'─'*40}")

# ── main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Строит словарь из книг")
    p.add_argument("books_dir", help="Папка с книгами (fb2/txt/epub)")
    p.add_argument("--min-count", type=int, default=3,
                   help="Минимальная частота (default: 3)")
    p.add_argument("--top", type=int, default=None,
                   help="Оставить N самых частых слов")
    p.add_argument("--format", choices=["txt", "tsv", "hunspell"], default="tsv",
                   help="Формат выходного файла (default: tsv)")
    p.add_argument("--output", default=None,
                   help="Имя выходного файла (default: vocab.<format>)")
    p.add_argument("--lang", choices=["ru", "en"], default="ru",
                   help="Язык текстов (default: ru)")
    p.add_argument("--no-lemma", action="store_true",
                   help="Не лемматизировать (быстрее, но словоформы не схлопываются)")
    return p.parse_args()

def main():
    args = parse_args()
    lemmatize = not args.no_lemma

    check_deps(args.lang, lemmatize)

    books_dir = Path(args.books_dir)
    if not books_dir.is_dir():
        print(f"[!] Папка не найдена: {books_dir}")
        sys.exit(1)

    # найти все книги
    paths = []
    for ext in READERS:
        paths.extend(books_dir.rglob(f"*{ext}"))
    paths.sort()

    if not paths:
        print(f"[!] Книги не найдены в {books_dir}")
        print(f"    Поддерживаемые форматы: {', '.join(READERS)}")
        sys.exit(1)

    print(f"Найдено книг: {len(paths)}\n")

    # построить частоты
    print("── Сбор частот ──────────────────────────────")
    freq = build_freq(paths, args.lang)
    print(f"\nВсего уникальных словоформ: {len(freq):,}")

    # лемматизация
    if lemmatize and args.lang == "ru":
        print("\n── Лемматизация ─────────────────────────────")
        freq = lemmatize_ru(freq)
        print(f"Уникальных лемм: {len(freq):,}")

    # фильтрация
    print("\n── Фильтрация ───────────────────────────────")
    vocab = filter_vocab(freq, args.min_count, args.top)
    print(f"После фильтрации (min_count={args.min_count}): {len(vocab):,} слов")

    # статистика
    print_stats(vocab)

    # сохранение
    fmt = args.format
    ext_map = {"txt": "txt", "tsv": "tsv", "hunspell": "dic"}
    out_path = Path(args.output) if args.output else Path(f"vocab.{ext_map[fmt]}")
    SAVERS[fmt](vocab, out_path)

if __name__ == "__main__":
    main()
