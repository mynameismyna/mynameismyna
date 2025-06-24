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


class ConnectionDialog(tk.Toplevel):
    """Dialog to collect connection information and attempt to connect."""

    def __init__(self, parent, info):
        super().__init__(parent)
        self.title("Connection")
        self.resizable(False, False)
        self.result = None
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        labels = ["Driver", "Server", "Database", "User ID", "Password"]
        self.entries = {}
        available_drivers = pyodbc.drivers()
        for idx, label in enumerate(labels):
            ttk.Label(self, text=label).grid(column=0, row=idx, padx=5, pady=2, sticky="e")
            if label == "Driver":
                ent = ttk.Combobox(self, values=available_drivers, width=27, state="readonly")
                if available_drivers:
                    current = 0
                    if info.get(label) in available_drivers:
                        current = available_drivers.index(info[label])
                    ent.current(current)
            else:
                ent = ttk.Entry(self, show="*" if label == "Password" else None, width=30)
                if info.get(label):
                    ent.insert(0, info[label])
            ent.grid(column=1, row=idx, padx=5, pady=2)
            self.entries[label] = ent

        btn_ok = ttk.Button(self, text="Connect", command=self.connect)
        btn_ok.grid(column=0, row=len(labels), padx=5, pady=5)
        btn_cancel = ttk.Button(self, text="Cancel", command=self.cancel)
        btn_cancel.grid(column=1, row=len(labels), padx=5, pady=5)

    def connect(self):
        info = {k: e.get() for k, e in self.entries.items()}
        try:
            conn = get_connection(info["Driver"], info["Server"], info["Database"], info["User ID"], info["Password"])
        except Exception as e:
            messagebox.showerror("Connection failed", str(e), parent=self)
            return
        self.result = (conn, info)
        self.destroy()

    def cancel(self):
        self.destroy()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock and Receivable App")
        self.conn = None
        self.connection_info = {}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.running = True
        self.executor = ThreadPoolExecutor()
        self.text_font = tkfont.Font(family="TkFixedFont", size=10)
        self.initialized = False

        self.show_connect_dialog()

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

    def show_connect_dialog(self):
        dlg = ConnectionDialog(self.root, self.connection_info)
        self.root.wait_window(dlg)
        if dlg.result is None:
            if not self.initialized:
                self.running = False
                self.root.destroy()
            return
        self.conn, self.connection_info = dlg.result
        if not self.initialized:
            self.create_widgets()
            self.initialized = True
            # The main window was hidden during startup; show it now
            self.root.deiconify()
        self.status_label.config(text="● Bağlı", foreground="green")
        self.btn_disconnect.config(state="normal")
        messagebox.showinfo("Connection", "Connected successfully")

    def create_widgets(self):
        top = ttk.Frame(self.root)
        top.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        top.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(top, text="● Bağlı", foreground="green")
        self.status_label.grid(column=0, row=0, sticky="w")

        self.btn_disconnect = ttk.Button(top, text="Disconnect", command=self.disconnect)
        self.btn_disconnect.grid(column=1, row=0, padx=5)

        self.btn_reconnect = ttk.Button(top, text="Reconnect", command=self.reconnect)
        self.btn_reconnect.grid(column=2, row=0, padx=5)

        self.btn_update = ttk.Button(top, text="Update Info", command=self.refresh_info)
        self.btn_update.grid(column=3, row=0, padx=5)

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

    def reconnect(self):
        if self.conn:
            self.disconnect(confirm=False)
        if not self.connection_info:
            self.refresh_info()
            return
        try:
            self.conn = get_connection(
                self.connection_info["Driver"],
                self.connection_info["Server"],
                self.connection_info["Database"],
                self.connection_info["User ID"],
                self.connection_info["Password"],
            )
            self.status_label.config(text="● Bağlı", foreground="green")
            self.btn_disconnect.config(state="normal")
            messagebox.showinfo("Connection", "Connected successfully")
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))

    def disconnect(self, confirm=True):
        if not self.conn:
            return
        if not confirm or messagebox.askyesno("Disconnect", "Bağlantıyı Sona Erdirmek İstiyor musunuz?"):
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
            self.status_label.config(text="● Bağlı Değil", foreground="red")
            self.btn_disconnect.config(state="disabled")
            messagebox.showinfo("Disconnect", "Bağlantı sonlandırıldı")

    def refresh_info(self):
        self.disconnect(confirm=False)
        self.show_connect_dialog()

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

    def on_close(self):
        self.running = False
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
        self.root.destroy()

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
    # Hide the main window until a connection is established
    root.withdraw()
    app = App(root)
    asyncio.ensure_future(asyncio.sleep(0), loop=app.loop)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    try:
        while app.running:
            root.update()
            app.loop.run_until_complete(asyncio.sleep(0.01))
    except tk.TclError:
        pass
    finally:
        app.loop.run_until_complete(asyncio.sleep(0))
        app.loop.close()


if __name__ == "__main__":
    main()
