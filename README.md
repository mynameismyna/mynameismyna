- 👋 Hi, I’m @mynameismyna
- 👀 I’m interested in everything that I want to know... For now, I try to distribute my version of Linux.
- 🌱 I’m currently learning programming.
- 💞️ I’m looking to collaborate on anything :)
- 📫 How to reach me? You can try mynameismyna@protonmail.com

<!---
mynameismyna/mynameismyna is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

## Stock and Receivable Application

`stock_cari.py` starts the GUI by default so you can connect and run queries in a
window without the program freezing. Pass `--cli` if you prefer to use the
console interface. Ensure `pyodbc` is installed.

```bash
# launch the GUI
python stock_cari.py

# run in command line mode
python stock_cari.py --cli
```

The GUI itself lives in `stock_cari_gui.py` and uses `tkinter` to keep the UI
responsive by executing database queries in a background thread.

The GUI now lists available ODBC drivers in a drop-down menu so you can
select the appropriate driver without typing its name.

Once connected, the connection fields become read-only and a status
indicator shows whether the app is connected. Use the new **Disconnect**
button to close the connection safely.

The result panel now resizes with the window. Use the **A+** and **A-**
buttons to adjust text size, and toggle **Bold** or **Italic** to change
the formatting of all results.

```bash
python stock_cari_gui.py
```
