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

At startup a dialog asks for your connection settings. After a successful
connection, the main window opens showing a status indicator and buttons to
**Disconnect**, **Reconnect** using the same credentials, or **Update Info** to
change the connection details.
The empty main window stays hidden until you connect, so you'll only see the
connection dialog at first.

The driver is selected from a drop-down list of installed ODBC drivers.

By default the connection dialog fills in the Server as `192.168.129.15` and
the Database as `BORAOZMAN`. Whatever values you last used are saved to
`connection.json` so they appear automatically the next time you open the
program.

The result panel now resizes with the window. Use the **A+** and **A-**
buttons to adjust text size, and toggle **Bold** or **Italic** to change
the formatting of all results.

```bash
python stock_cari_gui.py
```
