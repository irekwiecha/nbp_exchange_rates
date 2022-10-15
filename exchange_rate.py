import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import Entry, ttk

from requests import get
from tkcalendar import DateEntry


class MyDateEntry(DateEntry):
    def __init__(self, master=None, **kw):
        DateEntry.__init__(self, master=None, **kw)
        # add black border around drop-down calendar
        self._top_cal.configure(bg="black", bd=1)
        # add label displaying today's date below
        tk.Label(
            self._top_cal,
            bg="gray90",
            anchor="w",
            text="Today: %s" % date.today().strftime("%Y-%m-%d"),
        ).pack(fill="x")


def clear():
    result.config(state="normal")
    result.delete(0, "end")


def exchange_rate(code, date):
    # function that checks if data is available and returns a value
    day = 0
    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{code}/{date}/"
    new_date = date
    resp = get(url)
    while not resp.ok:
        day += 1
        x = datetime.strptime(date, "%Y-%m-%d") - timedelta(day)
        new_date = datetime.strftime(x, "%Y-%m-%d")
        url = f"http://api.nbp.pl/api/exchangerates/rates/a/{code}/{new_date}/"
        resp = get(url)
    data = resp.json()
    return (data["rates"][0]["mid"], new_date)


def frame_result():
    date = pick_date.get()
    code = currency.get()
    rate, new_date = exchange_rate(code, date)
    multiple = 100 if code in ["HUF", "JPY"] else 1
    result.insert(0, f"{multiple} {code} on {new_date} = {rate * multiple} PLN")
    result.config(state="readonly")
    if new_date != date:
        info_text.config(
            text="INFO: No data for the given date.\nPrevious business day data was returned."
        )
    else:
        info_text.config(text="")


root = tk.Tk()
root.title("NBP exchange rate")
root.geometry("320x200+100-100")
root.resizable(False, False)
root.attributes("-topmost", 1)  # always on top
root.iconbitmap("./images/logo.ico")

# Transparency
# root.attributes('-alpha', 0.5)

date_text = ttk.Label(root, text="Please select a date:")
date_text.pack()
date_text.place(x=10, y=10)

# create the entry and configure the calendar colors
pick_date = MyDateEntry(
    root,
    year=datetime.now().year,
    month=datetime.now().month,
    day=datetime.now().day,
    date_pattern="y-mm-dd",
    selectbackground="gray80",
    selectforeground="black",
    normalbackground="white",
    normalforeground="black",
    background="gray90",
    foreground="black",
    bordercolor="gray90",
    othermonthforeground="gray50",
    othermonthbackground="white",
    othermonthweforeground="gray50",
    othermonthwebackground="white",
    weekendbackground="white",
    weekendforeground="black",
    headersbackground="white",
    headersforeground="gray70",
)
pick_date.pack()
pick_date.place(x=210, y=10)

currency_text = ttk.Label(root, text="Please select a currency:")
currency_text.pack()
currency_text.place(x=10, y=50)

currency_list = ["USD", "EUR", "CHF", "CAD", "GBP", "CZK", "CNY", "HUF", "JPY"]
currency = ttk.Combobox(root, values=currency_list, width=12)
currency.set("USD")
currency.pack()
currency.place(x=210, y=50)

submit_button = ttk.Button(
    root, text="Submit", command=lambda: [clear(), frame_result()], width=10
)
submit_button.pack()
submit_button.place(x=123, y=90)


result = Entry(
    root,
    width=38,
    font=("Arial", 12, "bold"),
    justify="center",
)
result.pack(side=tk.BOTTOM)

info_text = ttk.Label(root, text="", justify="center")
info_text.pack(side=tk.BOTTOM)

# keep the window displaying
root.mainloop()
