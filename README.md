# 📚 Book Dictionary Builder

🇷🇺 [Русский](#-русский) | 🇬🇧 [English](#-english) | 🇨🇳 [中文](#-中文)

---

## 🇷🇺 Русский

Два скрипта которые автоматически строят толковый словарь из любой книги на русском языке — от сырого fb2 до готового файла для GoldenDict.

**Проверено на 4 ГБ ОЗУ** — пик потребления памяти ~300 МБ.

### Что получится

Берёте книгу в формате fb2, epub или txt — на выходе получаете словарь именно из слов этой книги, с определениями из Викисловаря, в формате StarDict. Открывается в GoldenDict, Lingvo и других программах.

На реальной книге (~123 000 слов):
- Уникальных лемм: **10 226**
- Найдено определений: **~10 046**
- Время работы: ~5–10 минут

> ⚠️ **Язык:** сейчас поддерживается только **русский** (лемматизация через pymorphy3 + Викисловарь). Английские и китайские книги — в планах.

### Что понадобится

- Python 3.10+ — [python.org](https://python.org)
- GoldenDict-ng — [github.com/xiaoyifang/goldendict-ng](https://github.com/xiaoyifang/goldendict-ng/releases)
- Книга в формате `.fb2` / `.epub` / `.txt`
- ~400 МБ свободного места (дамп Викисловаря, скачается один раз)

### Установка

```bash
pip install lxml pymorphy3 requests
```

### Структура папок

```
проект/
├── build_vocab.py
├── make_dict.py
└── books/
    └── книга.fb2
```

### Использование

**Шаг 1 — Собрать слова из книги**

```bash
python build_vocab.py books/ --min-count 1
```

Появится `vocab.tsv` — все уникальные слова книги с частотами. Слова лемматизированы: `бежал`, `бежала`, `бежать` → одна запись `бежать`.

**Шаг 2 — Собрать толковый словарь**

```bash
python make_dict.py vocab.tsv
```

При первом запуске скачается дамп Викисловаря (~300 МБ) — один раз. Появятся три файла:

```
my_dictionary.ifo
my_dictionary.idx
my_dictionary.dict
```

**Шаг 3 — Открыть в GoldenDict**

Правка → Словари → Файлы → Добавить папку → указать папку → Применить.

### Сделать словарь морфологическим

Готовый словарь из книги можно прогнать через **[morph-dict-converter](https://github.com/knigaperevodchik/morph-dict-converter)** — тогда поиск будет работать по любой форме слова, не только по начальной.

```bash
python morph_dict_convert.py my_dictionary.ifo
```

### Опции build_vocab.py

| Опция | По умолчанию | Описание |
|-------|-------------|----------|
| `--min-count` | 3 | Минимальная частота слова |
| `--top` | все | Оставить только N самых частых |
| `--format` | tsv | Формат: `txt`, `tsv`, `hunspell` |
| `--no-lemma` | выкл | Не лемматизировать (быстрее) |

### Возможные проблемы

**Терминал закрывается сразу** — запускайте через cmd, не двойным кликом. Откройте папку в Проводнике → кликните адресную строку → напечатайте `cmd` → Enter.

**Слово не нашлось** — после работы появится `missing_words.txt`. Обычно это имена собственные и редкие слова которых нет в Викисловаре.

---

## 🇬🇧 English

Two scripts that automatically build a dictionary from any **Russian-language** book — from a raw fb2 file to a ready-to-use StarDict file for GoldenDict.

**Tested on 4 GB RAM** — peak memory usage ~300 MB.

### What you get

Give it a book in fb2, epub, or txt format — you get a dictionary of exactly the words used in that book, with definitions from Wiktionary, in StarDict format. Opens in GoldenDict, Lingvo, and other programs.

Results on a real book (~123,000 words):
- Unique lemmas: **10,226**
- Definitions found: **~10,046**
- Processing time: ~5–10 minutes

> ⚠️ **Language:** currently supports **Russian only** (lemmatization via pymorphy3 + Russian Wiktionary). Support for English and Chinese books is planned.

### Requirements

- Python 3.10+ — [python.org](https://python.org)
- GoldenDict-ng — [github.com/xiaoyifang/goldendict-ng](https://github.com/xiaoyifang/goldendict-ng/releases)
- A book in `.fb2` / `.epub` / `.txt` format
- ~400 MB free disk space (Wiktionary dump, downloaded once)

### Installation

```bash
pip install lxml pymorphy3 requests
```

### Folder structure

```
project/
├── build_vocab.py
├── make_dict.py
└── books/
    └── mybook.fb2
```

### Usage

**Step 1 — Extract words from the book**

```bash
python build_vocab.py books/ --min-count 1
```

Creates `vocab.tsv` — all unique words with frequencies. Words are lemmatized: `бежал`, `бежала`, `бежать` → one entry `бежать`.

**Step 2 — Build the dictionary**

```bash
python make_dict.py vocab.tsv
```

On first run, downloads the Wiktionary dump (~300 MB) — only once. Three files will appear:

```
my_dictionary.ifo
my_dictionary.idx
my_dictionary.dict
```

**Step 3 — Open in GoldenDict**

Edit → Dictionaries → Files → Add folder → select the project folder → Apply.

### Make it morphological

The output dictionary can be processed with **[morph-dict-converter](https://github.com/knigaperevodchik/morph-dict-converter)** — so search works by any word form, not just the base form.

```bash
python morph_dict_convert.py my_dictionary.ifo
```

### Options for build_vocab.py

| Option | Default | Description |
|--------|---------|-------------|
| `--min-count` | 3 | Minimum word frequency |
| `--top` | all | Keep only N most frequent words |
| `--format` | tsv | Output format: `txt`, `tsv`, `hunspell` |
| `--no-lemma` | off | Skip lemmatization (faster) |

### Troubleshooting

**Terminal closes immediately** — run via cmd, don't double-click the script. Open the project folder in Explorer, click the address bar, type `cmd`, press Enter.

**Word not found** — a `missing_words.txt` file will appear after the script finishes. Usually proper nouns and rare words not in Wiktionary.

---

## 🇨🇳 中文

两个脚本，自动从任意**俄语**书籍生成词典——从原始 fb2 文件到可直接在 GoldenDict 中使用的 StarDict 文件。

**已在 4 GB 内存设备上测试** — 峰值内存占用约 300 MB。

### 效果

输入 fb2、epub 或 txt 格式的书籍，输出该书专属词典，包含来自维基词典的释义，格式为 StarDict。可在 GoldenDict、Lingvo 等程序中打开。

实际测试（约 123,000 词的书籍）：
- 唯一词元数：**10,226**
- 找到释义数：**~10,046**
- 处理时间：约 5–10 分钟

> ⚠️ **语言：** 目前仅支持**俄语**书籍（通过 pymorphy3 进行词形还原 + 俄语维基词典）。英语和中文书籍的支持正在计划中。

### 环境要求

- Python 3.10+ — [python.org](https://python.org)
- GoldenDict-ng — [github.com/xiaoyifang/goldendict-ng](https://github.com/xiaoyifang/goldendict-ng/releases)
- `.fb2` / `.epub` / `.txt` 格式的书籍
- 约 400 MB 可用磁盘空间（维基词典数据，仅下载一次）

### 安装依赖

```bash
pip install lxml pymorphy3 requests
```

### 目录结构

```
project/
├── build_vocab.py
├── make_dict.py
└── books/
    └── mybook.fb2
```

### 使用方法

**第一步 — 从书籍提取词汇**

```bash
python build_vocab.py books/ --min-count 1
```

生成 `vocab.tsv`——书中所有唯一词汇及其频率。已进行词形还原：`бежал`、`бежала`、`бежать` → 统一为 `бежать`。

**第二步 — 生成词典**

```bash
python make_dict.py vocab.tsv
```

首次运行时会下载维基词典数据（约 300 MB），仅需一次。运行后生成三个文件：

```
my_dictionary.ifo
my_dictionary.idx
my_dictionary.dict
```

**第三步 — 在 GoldenDict 中打开**

编辑 → 词典 → 文件 → 添加文件夹 → 选择项目文件夹 → 应用。

### 转换为形态学词典

生成的词典可通过 **[morph-dict-converter](https://github.com/knigaperevodchik/morph-dict-converter)** 进行处理——使搜索支持任意词形，而不仅仅是原形。

```bash
python morph_dict_convert.py my_dictionary.ifo
```

### build_vocab.py 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--min-count` | 3 | 最低词频 |
| `--top` | 全部 | 仅保留前 N 个高频词 |
| `--format` | tsv | 输出格式：`txt`、`tsv`、`hunspell` |
| `--no-lemma` | 关闭 | 跳过词形还原（速度更快）|

### 常见问题

**终端窗口立即关闭** — 请通过 cmd 运行，不要双击脚本。在资源管理器中打开项目文件夹，点击地址栏，输入 `cmd`，按 Enter。

**词典中找不到某个词** — 脚本完成后会生成 `missing_words.txt`，包含所有未找到的词。通常是专有名词或维基词典中没有收录的罕见词汇。

---

## 💙 Donate / Донат / 捐赠

**TON (USDT)**
```
UQBWKwf2mgakNi4Ls2I6NNs1okcDyCxivdxxc22ypsMV4590
```

**TRC-20 (USDT)**
```
TDdok5FgB6fJSXZrPzxnn7hMk4qREUZPJe
```
