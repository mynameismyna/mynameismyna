- 👋 Hi, I’m @mynameismyna
- 👀 I’m interested in everything that I want to know... For now, I try to distribute my version of Linux.
- 🌱 I’m currently learning programming.
- 💞️ I’m looking to collaborate on anything :)
- 📫 How to reach me? You can try mynameismyna@protonmail.com

<!---
mynameismyna/mynameismyna is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

## Stock and Receivable CLI

This repository includes a small console application `stock_cari.py` which queries a SQL Server for stock and receivable information. The program prompts for connection details at startup and executes queries asynchronously so it does not freeze during database operations.

Run the script with Python and ensure `pyodbc` is installed:

```bash
python stock_cari.py
```

## Windows-like GUI

If you prefer a simple graphical interface, run `stock_cari_gui.py`. It uses
`tkinter` and keeps the UI responsive by executing database queries in a
background thread.

```bash
python stock_cari_gui.py
```
