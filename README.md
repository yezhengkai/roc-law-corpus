# roc-law-corpus

## Install dependencies and current project, but not development dependencies
### Use poetry
```bash
poetry install --without dev
roc-law-corpus jl-instantiate
```

### Use pip
```bash
pip install -r requirements.txt
pip install -e .
roc-law-corpus jl-instantiate
```

## Install dependencies and current project
### Use poetry
```bash
poetry install
roc-law-corpus jl-instantiate
```
### Use pip
```bash
pip install -r requirements_dev.txt
pip install -e .
roc-law-corpus jl-instantiate
```

## Operating on corpus of Judicial Yuan QA
### Scraping corpus
```bash
roc-law-corpus judicial-yuan-qa scraping data/judicial_yuan_qa_raw.json
```
### Clean corpus
```bash
roc-law-corpus judicial-yuan-qa clean data/judicial_yuan_qa_raw.json data/judicial_yuan_qa.json
```

## Operating on corpus of moex exam
### Scraping pdfs
```bash
roc-law-corpus moex scraping data/moex/ data/moex.json
```
### Extract pdf content
```bash
roc-law-corpus moex extract data/moex/ data/moex.json
```