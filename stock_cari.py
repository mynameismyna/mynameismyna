import asyncio
import pyodbc


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

async def fetch_query_async(loop, connection, query, params=None):
    return await loop.run_in_executor(None, fetch_query, connection, query, params)

async def main_cli():
    driver = input("Driver: ")
    server = input("Server: ")
    database = input("Database: ")
    uid = input("User ID: ")
    pwd = input("Password: ")

    try:
        conn = get_connection(driver, server, database, uid, pwd)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    loop = asyncio.get_event_loop()
    while True:
        print("1. Get stock by ID")
        print("2. Get receivable balance by customer ID")
        print("3. Quit")
        choice = input("Select an option: ")

        if choice == "1":
            stock_id = input("Stock ID: ")
            query = "SELECT * FROM Stocks WHERE StockID = ?"
            rows = await fetch_query_async(loop, conn, query, (stock_id,))
            for row in rows:
                print(row)
        elif choice == "2":
            cust_id = input("Customer ID: ")
            query = "SELECT * FROM Receivables WHERE CustomerID = ?"
            rows = await fetch_query_async(loop, conn, query, (cust_id,))
            for row in rows:
                print(row)
        elif choice == "3":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv:
        asyncio.run(main_cli())
    else:
        import stock_cari_gui
        stock_cari_gui.main()
