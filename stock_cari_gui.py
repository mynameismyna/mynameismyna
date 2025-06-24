import asyncio
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import font as tkfont
import pyodbc
from concurrent.futures import ThreadPoolExecutor


def get_connection(driver, server, database, uid, pwd):
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd}"
    )
    return pyodbc.connect(conn_str)


def fetch_query(connection, query, params=None):
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock and Receivable App")
        self.conn = None
        self.loop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor()
        self.text_font = tkfont.Font(family="TkFixedFont", size=10)
        self.create_widgets()

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

    def create_widgets(self):
        frm_conn = ttk.LabelFrame(self.root, text="Connection")
        frm_conn.grid(column=0, row=0, padx=10, pady=10, sticky="ew")

        labels = ["Driver", "Server", "Database", "User ID", "Password"]
        self.entries = {}
        available_drivers = pyodbc.drivers()
        for idx, label in enumerate(labels):
            ttk.Label(frm_conn, text=label).grid(column=0, row=idx, sticky="e", padx=5, pady=2)
            if label == "Driver":
                ent = ttk.Combobox(frm_conn, values=available_drivers, width=27, state="readonly")
                if available_drivers:
                    ent.current(0)
            else:
                ent = ttk.Entry(frm_conn, show="*" if label == "Password" else None, width=30)
            ent.grid(column=1, row=idx, padx=5, pady=2)
            self.entries[label] = ent

        # connection status indicator
        self.status_label = ttk.Label(frm_conn, text="● Bağlı Değil", foreground="red")
        self.status_label.grid(column=2, row=0, rowspan=len(labels), padx=10)

        # connect/disconnect buttons
        self.btn_connect = ttk.Button(frm_conn, text="Connect", command=self.connect)
        self.btn_connect.grid(column=0, row=len(labels), padx=5, pady=5)

        self.btn_disconnect = ttk.Button(frm_conn, text="Disconnect", command=self.disconnect, state="disabled")
        self.btn_disconnect.grid(column=1, row=len(labels), padx=5, pady=5)

        frm_query = ttk.LabelFrame(self.root, text="Query")
        frm_query.grid(column=0, row=1, padx=10, pady=10, sticky="ew")

        ttk.Label(frm_query, text="Stock ID").grid(column=0, row=0, sticky="e", padx=5, pady=2)
        self.stock_id = ttk.Entry(frm_query, width=20)
        self.stock_id.grid(column=1, row=0, padx=5, pady=2)
        btn_stock = ttk.Button(frm_query, text="Get Stock", command=self.get_stock)
        btn_stock.grid(column=2, row=0, padx=5, pady=2)

        ttk.Label(frm_query, text="Customer ID").grid(column=0, row=1, sticky="e", padx=5, pady=2)
        self.cust_id = ttk.Entry(frm_query, width=20)
        self.cust_id.grid(column=1, row=1, padx=5, pady=2)
        btn_receivable = ttk.Button(frm_query, text="Get Receivable", command=self.get_receivable)
        btn_receivable.grid(column=2, row=1, padx=5, pady=2)

        frm_output = ttk.Frame(self.root)
        frm_output.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")
        frm_output.columnconfigure(0, weight=1)
        frm_output.rowconfigure(0, weight=1)

        self.output = scrolledtext.ScrolledText(frm_output, width=60, height=15, font=self.text_font)
        self.output.grid(column=0, row=0, columnspan=4, sticky="nsew")

        btn_zoom_in = ttk.Button(frm_output, text="A+", command=lambda: self.adjust_font(1))
        btn_zoom_in.grid(column=0, row=1, sticky="w", pady=(5, 0))

        btn_zoom_out = ttk.Button(frm_output, text="A-", command=lambda: self.adjust_font(-1))
        btn_zoom_out.grid(column=1, row=1, sticky="w", pady=(5, 0))

        self.bold_var = tk.BooleanVar(value=False)
        chk_bold = ttk.Checkbutton(frm_output, text="Bold", variable=self.bold_var, command=self.update_font_style)
        chk_bold.grid(column=2, row=1, sticky="e", pady=(5, 0))

        self.italic_var = tk.BooleanVar(value=False)
        chk_italic = ttk.Checkbutton(frm_output, text="Italic", variable=self.italic_var, command=self.update_font_style)
        chk_italic.grid(column=3, row=1, sticky="e", pady=(5, 0))

    def connect(self):
        driver = self.entries["Driver"].get()
        server = self.entries["Server"].get()
        database = self.entries["Database"].get()
        uid = self.entries["User ID"].get()
        pwd = self.entries["Password"].get()
        try:
            self.conn = get_connection(driver, server, database, uid, pwd)
            self.status_label.config(text="● Bağlı", foreground="green")
            for key, ent in self.entries.items():
                ent.config(state="disabled")
            self.btn_connect.config(state="disabled")
            self.btn_disconnect.config(state="normal")
            messagebox.showinfo("Connection", "Connected successfully")
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))

    def disconnect(self):
        if not self.conn:
            return
        if messagebox.askyesno("Disconnect", "Bağlantıyı Sona Erdirmek İstiyor musunuz?"):
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
            self.status_label.config(text="● Bağlı Değil", foreground="red")
            for label, ent in self.entries.items():
                state = "readonly" if label == "Driver" else "normal"
                ent.config(state=state)
            self.btn_connect.config(state="normal")
            self.btn_disconnect.config(state="disabled")
            messagebox.showinfo("Disconnect", "Bağlantı sonlandırıldı")

    async def run_query(self, query, params=None):
        if not self.conn:
            messagebox.showwarning("Not connected", "Please connect to the database first")
            return
        rows = await self.loop.run_in_executor(self.executor, fetch_query, self.conn, query, params)
        self.output.delete("1.0", tk.END)
        for row in rows:
            self.output.insert(tk.END, f"{row}\n")

    def adjust_font(self, delta):
        size = self.text_font.cget("size") + delta
        if size < 6:
            size = 6
        self.text_font.configure(size=size)

    def update_font_style(self):
        weight = "bold" if self.bold_var.get() else "normal"
        slant = "italic" if self.italic_var.get() else "roman"
        self.text_font.configure(weight=weight, slant=slant)

    def get_stock(self):
        stock_id = self.stock_id.get()
        query = "SELECT * FROM Stocks WHERE StockID = ?"
        asyncio.ensure_future(self.run_query(query, (stock_id,)), loop=self.loop)

    def get_receivable(self):
        cust_id = self.cust_id.get()
        query = "SELECT * FROM Receivables WHERE CustomerID = ?"
        asyncio.ensure_future(self.run_query(query, (cust_id,)), loop=self.loop)


def main():
    root = tk.Tk()
    app = App(root)
    asyncio.ensure_future(asyncio.sleep(0), loop=app.loop)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    while True:
        try:
            root.update()
            app.loop.run_until_complete(asyncio.sleep(0.01))
        except tk.TclError:
            break


if __name__ == "__main__":
    main()
