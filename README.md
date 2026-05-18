# 📚 Book Dictionary Builder

🇺🇸 English | [🇷🇺 Русский](#-русский) | [🇨🇳 中文](#-中文)

---

## 🇺🇸 English

Two scripts that automatically build a dictionary from any book — from a raw fb2 file to a ready-to-use file for GoldenDict.

**Tested on 4 GB RAM** — peak memory usage ~300 MB.

### What you get

Give it a book in fb2, epub, or txt format — you get a dictionary of exactly the words used in that book, with definitions from Wiktionary, in StarDict format. Opens in GoldenDict, Lingvo, and other programs.

Results on a real book (~123,000 words):
- Unique lemmas: **10,226**
- Definitions found: **~10,046**
- Processing time: ~5–10 minutes

### Requirements

- Python 3.10+ — [python.org](https://python.org)
- GoldenDict — [goldendict.org](http://goldendict.org)
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

Creates `vocab.tsv` — all unique words with frequencies. Words are lemmatized: `running`, `ran`, `runs` → one entry `run`.

**Step 2 — Build the dictionary**

```bash
python make_dict.py vocab.tsv
```

On first run, downloads the Wiktionary dump (~300 MB) — only once. Subsequent runs reuse the cached file.

Three files will appear:

```
my_dictionary.ifo
my_dictionary.idx
my_dictionary.dict
```

**Step 3 — Open in GoldenDict**

**Edit → Dictionaries → Files → Add folder** → select the `project/` folder → Apply.

### Options for build_vocab.py

| Option | Default | Description |
|---|---|---|
| `--min-count` | 3 | Minimum word frequency |
| `--top` | all | Keep only N most frequent words |
| `--format` | tsv | Output format: `txt`, `tsv`, `hunspell` |
| `--no-lemma` | off | Skip lemmatization (faster) |

### Troubleshooting

**Terminal closes immediately** — run via cmd, don't double-click the script. Open the project folder in Explorer, click the address bar, type `cmd`, press Enter.

**Word not found in dictionary** — after the script finishes, a `missing_words.txt` file will appear with all unfound words. Usually proper nouns and rare words not in Wiktionary.

### How it works

```
fb2 / epub / txt
      ↓
  text cleaning
      ↓
  tokenization
      ↓
 lemmatization (pymorphy3)
      ↓
   filtering
      ↓
   vocab.tsv
      ↓
 Wiktionary dump
      ↓
  StarDict (.ifo / .idx / .dict)
```

---

## 🇷🇺 Русский

Два скрипта которые автоматически строят толковый словарь из любой книги — от сырого fb2 до готового файла для GoldenDict.

**Проверено на 4 ГБ ОЗУ** — пик потребления памяти ~300 МБ.

### Что получится

Берёте книгу в формате fb2, epub или txt — на выходе получаете толковый словарь именно из слов этой книги, с определениями из Викисловаря, в формате StarDict. Открывается в GoldenDict, Lingvo и других программах.

На реальной книге (~123 000 слов):
- Уникальных лемм: **10 226**
- Найдено определений: **~10 046**
- Время работы: ~5–10 минут

### Что понадобится

- Python 3.10+ — [python.org](https://python.org)
- GoldenDict — [goldendict.org](http://goldendict.org)
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

В папке появится `vocab.tsv` — все уникальные слова книги с частотами. Слова лемматизированы: `бежал`, `бежала`, `бежать` → одна запись `бежать`.

**Шаг 2 — Собрать толковый словарь**

```bash
python make_dict.py vocab.tsv
```

При первом запуске скачается дамп русского Викисловаря (~300 МБ) — один раз. Повторные запуски используют уже скачанный файл.

В папке появятся три файла:

```
my_dictionary.ifo
my_dictionary.idx
my_dictionary.dict
```

**Шаг 3 — Открыть в GoldenDict**

**Правка → Словари → Файлы → Добавить папку** → указать папку `проект/` → Применить.

### Опции build_vocab.py

| Опция | По умолчанию | Описание |
|---|---|---|
| `--min-count` | 3 | Минимальная частота слова |
| `--top` | все | Оставить только N самых частых |
| `--format` | tsv | Формат: `txt`, `tsv`, `hunspell` |
| `--no-lemma` | выкл | Не лемматизировать (быстрее) |

### Как открыть терминал в нужной папке

Открыть папку `проект/` в Проводнике → кликнуть на адресную строку сверху → напечатать `cmd` → Enter.

### Возможные проблемы

**Терминал закрывается сразу** — запускайте через cmd, не двойным кликом по скрипту.

**Слово не нашлось в словаре** — после работы скрипта появится файл `missing_words.txt`. Обычно это имена собственные и редкие авторские слова которых нет в Викисловаре.

### Как это работает

```
fb2 / epub / txt
      ↓
  очистка текста
      ↓
  токенизация
      ↓
 лемматизация (pymorphy3)
      ↓
  фильтрация
      ↓
   vocab.tsv
      ↓
 Викисловарь (дамп)
      ↓
  StarDict (.ifo / .idx / .dict)
```

---

## 🇨🇳 中文

两个脚本，自动从任意书籍生成词典——从原始 fb2 文件到可直接在 GoldenDict 中使用的文件。

**已在 4 GB 内存设备上测试** — 峰值内存占用约 300 MB。

### 效果

输入 fb2、epub 或 txt 格式的书籍，输出该书专属词典，包含来自维基词典的释义，格式为 StarDict。可在 GoldenDict、Lingvo 等程序中打开。

实际测试（约 123,000 词的书籍）：
- 唯一词元数：**10,226**
- 找到释义数：**~10,046**
- 处理时间：约 5–10 分钟

### 环境要求

- Python 3.10+ — [python.org](https://python.org)
- GoldenDict — [goldendict.org](http://goldendict.org)
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

生成 `vocab.tsv`——书中所有唯一词汇及其出现频率。词汇已进行词形还原：`running`、`ran`、`runs` → 统一为 `run`。

**第二步 — 生成词典**

```bash
python make_dict.py vocab.tsv
```

首次运行时会下载维基词典数据（约 300 MB），仅需一次。后续运行直接使用已下载的文件。

运行后生成三个文件：

```
my_dictionary.ifo
my_dictionary.idx
my_dictionary.dict
```

**第三步 — 在 GoldenDict 中打开**

**编辑 → 词典 → 文件 → 添加文件夹** → 选择 `project/` 文件夹 → 应用。

### build_vocab.py 选项

| 选项 | 默认值 | 说明 |
|---|---|---|
| `--min-count` | 3 | 最低词频 |
| `--top` | 全部 | 仅保留前 N 个高频词 |
| `--format` | tsv | 输出格式：`txt`、`tsv`、`hunspell` |
| `--no-lemma` | 关闭 | 跳过词形还原（速度更快） |

### 常见问题

**终端窗口立即关闭** — 请通过 cmd 运行，不要双击脚本。在资源管理器中打开项目文件夹，点击地址栏，输入 `cmd`，按 Enter。

**词典中找不到某个词** — 脚本运行完成后会生成 `missing_words.txt`，包含所有未找到的词。通常是专有名词或维基词典中没有收录的罕见词汇。

### 工作原理

```
fb2 / epub / txt
      ↓
   文本清理
      ↓
   分词处理
      ↓
  词形还原 (pymorphy3)
      ↓
   词汇过滤
      ↓
   vocab.tsv
      ↓
  维基词典数据
      ↓
  StarDict (.ifo / .idx / .dict)
```
