<p align="center">
    <img src="![Image](https://github.com/user-attachments/assets/0f9cef79-3e44-4b0e-8f8e-a2a9ada90325)" alt="CocoIndex Patient Form Extraction">
</p>

This repo shows how to use OpenAI API to extract structured data from patient intake forms with different formats, like PDF, Docx, etc. from Google Drive.

❤️ Please give [Cocoindex on Github](https://github.com/cocoindex-io/cocoindex) a star ⭐ to support us if you like our work. Thank you so much with a warm coconut hug 🥥🤗. [![GitHub](https://img.shields.io/github/stars/cocoindex-io/cocoindex?color=5B5BD6)](https://github.com/cocoindex-io/cocoindex)



## Prerequisite
- [Install Postgres](https://cocoindex.io/docs/getting_started/installation#-install-postgres) if you don't have one.

- Install CocoIndex
```bash
pip install -U cocoindex
```

-  Make sure you have specify the database URL by environment variable:
```
export COCOINDEX_DATABASE_URL="postgresql://cocoindex:cocoindex@localhost:5432/cocoindex"
```

## Run

Setup index:

```bash
python main.py cocoindex setup
```

Update index:

```bash
python main.py cocoindex update
```

Run query:

```bash
python main.py
```

Run with CocoInsight:
```bash
python3 main.py cocoindex server -c https://cocoindex.io
```

View results at https://cocoindex.io/cocoinsight