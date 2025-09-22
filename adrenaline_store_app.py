# adrenaline_store_app.py
"""
Adrenaline Sports Store - PyQt5 desktop app
Single-file example UI with API integration placeholders.

Usage:
    1. Install requirements: pip install -r requirements.txt
    2. Run for dev: python adrenaline_store_app.py
    3. Build EXE: pyinstaller --onefile --noconsole adrenaline_store_app.py
"""

import sys
import threading
from functools import partial
from datetime import datetime, timedelta

import requests
from PyQt5 import QtCore, QtGui, QtWidgets

# ========== CONFIG ==========
API_BASE_URL = "http://127.0.0.1:8000"  # <<--- set to your API base
TIMEOUT = 8  # seconds for requests

# Endpoints (adjust to your API)
ENDPOINTS = {
    "products": "/products/all",
    "customers": "/customers/all",
    "customers/create": "/customers/addCustomer",
    "offers": "/events/all",
    "offers/create": "/events/create",
    "sales": "/sales/addSale",
    "sales/all": "/sales/all",
    "day/start": "/day-management/startDay",
    "day/end": "/day-management/endDay",  # Note: requires /day_id appended
    "day/active": "/day-management/activeDay",
    "categories": "/categories/all",
    "payment_types": "/paymentType/all",
    "delivery_types": "/deliveryType/all",
}

# ============================

class Worker(QtCore.QRunnable):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.signals = WorkerSignals()

    def run(self):
        result = self.fn()
        self.signals.result.emit(result)


class WorkerSignals(QtCore.QObject):
    result = QtCore.pyqtSignal(object)

def api_get(path, params=None):
    url = API_BASE_URL.rstrip("/") + path
    print(f"[API] Making GET request to: {url}")
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        print(f"[API] Response status code: {resp.status_code}")
        resp.raise_for_status()
        json_response = resp.json()
        print(f"[API] Response JSON received.")
        return json_response
    except Exception as e:
        print(f"[API] Error during GET request: {e}")
        # In a real app you'd log
        return {"error": str(e)}


def api_post(path, payload):
    url = API_BASE_URL.rstrip("/") + path
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


class LoadingOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.label = QtWidgets.QLabel("Loading...")
        self.label.setStyleSheet("font-size:18px; color: white;")
        layout.addWidget(self.label)
        self.setStyleSheet("background: rgba(0,0,0,0.5);")
        self.hide()

    def resizeEvent(self, event):
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())


class AdrenalineApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adrenaline Sports Store")
        self.resize(1050, 700)
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.layout = QtWidgets.QVBoxLayout(self.central)

        # Top header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("ADrenaline Sports Store")
        title.setStyleSheet("font-size:22px; font-weight:700;")
        header.addWidget(title)
        header.addStretch()
        self.layout.addLayout(header)

        # Main content - tabs
        self.tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tabs
        self.tab_new_sale = QtWidgets.QWidget()
        self.tab_customers = QtWidgets.QWidget()
        self.tab_products = QtWidgets.QWidget()
        self.tab_offers = QtWidgets.QWidget()
        self.tab_day = QtWidgets.QWidget()

        self.tabs.addTab(self.tab_new_sale, "New Sale")
        self.tabs.addTab(self.tab_customers, "Customers")
        self.tabs.addTab(self.tab_products, "Products")
        self.tabs.addTab(self.tab_offers, "Offers")
        self.tabs.addTab(self.tab_day, "Day Management")

        self._build_new_sale_tab()
        self._build_customers_tab()
        self._build_products_tab()
        self._build_offers_tab()
        self._build_day_tab()

        # Loading overlay
        self.loading = LoadingOverlay(self.central)

        # In-memory cart
        self.cart = []
        self.all_products_cache = []
        self.all_customers_cache = []
        self.all_categories_cache = []
        self.all_payment_types_cache = []
        self.all_delivery_types_cache = []
        self.all_offers_cache = []
        self.all_sales_cache = []


        # initial load
        self.load_products()
        self.load_customers()
        self.load_categories()
        self.load_payment_types()
        self.load_delivery_types()
        self.load_offers()
        self.load_sales()

    # ---------------- UI BUILDers ----------------
    def _build_new_sale_tab(self):
        main_layout = QtWidgets.QVBoxLayout(self.tab_new_sale)

        # Top section for sale creation
        top_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(top_widget)

        # Left: product search + list
        left = QtWidgets.QVBoxLayout()
        search_bar = QtWidgets.QHBoxLayout()
        self.input_product_search = QtWidgets.QLineEdit()
        self.input_product_search.setPlaceholderText("Enter product name")
        self.category_filter_sale = QtWidgets.QComboBox()
        self.category_filter_sale.setMinimumWidth(120)
        self.category_filter_sale.currentIndexChanged.connect(self.on_search_products)
        btn_search = QtWidgets.QPushButton("Search")
        btn_search.clicked.connect(self.on_search_products)
        self.input_product_search.returnPressed.connect(self.on_search_products)
        search_bar.addWidget(self.input_product_search)
        search_bar.addWidget(self.category_filter_sale)
        search_bar.addWidget(btn_search)
        left.addLayout(search_bar)

        self.tbl_products = QtWidgets.QTableWidget(0, 6)
        self.tbl_products.setHorizontalHeaderLabels(
            ["Name", "Category", "Size", "Available", "Price", "Add"]
        )
        self.tbl_products.horizontalHeader().setStretchLastSection(True)
        left.addWidget(self.tbl_products)

        layout.addLayout(left, 2)

        # Right: cart and customer
        right = QtWidgets.QVBoxLayout()

        # Customer group
        cust_group = QtWidgets.QGroupBox("Customer")
        cust_layout = QtWidgets.QFormLayout()
        self.cust_name = QtWidgets.QLineEdit()
        self.cust_mobile = QtWidgets.QLineEdit()
        self.cust_address = QtWidgets.QTextEdit()
        self.sale_date = QtWidgets.QDateEdit(datetime.now())
        self.sale_date.setCalendarPopup(True)
        self.payment_type_combo = QtWidgets.QComboBox()
        self.delivery_type_combo = QtWidgets.QComboBox()
        self.offer_combo = QtWidgets.QComboBox()
        btn_apply_offer = QtWidgets.QPushButton("Apply Offer")
        btn_apply_offer.clicked.connect(self.on_apply_offer)

        cust_layout.addRow("Customer Name", self.cust_name)
        cust_layout.addRow("Mobile", self.cust_mobile)
        cust_layout.addRow("Address", self.cust_address)
        cust_layout.addRow("Date", self.sale_date)
        cust_layout.addRow("Payment Type", self.payment_type_combo)
        cust_layout.addRow("Delivery Type", self.delivery_type_combo)

        offer_layout = QtWidgets.QHBoxLayout()
        offer_layout.addWidget(self.offer_combo)
        offer_layout.addWidget(btn_apply_offer)
        cust_layout.addRow("Apply Offer", offer_layout)

        cust_group.setLayout(cust_layout)
        right.addWidget(cust_group)

        # Cart table
        cart_group = QtWidgets.QGroupBox("Cart")
        cart_layout = QtWidgets.QVBoxLayout()
        self.tbl_cart = QtWidgets.QTableWidget(0, 5)
        self.tbl_cart.setHorizontalHeaderLabels(["Name", "Qty", "Price", "Discounted", "Total"])
        cart_layout.addWidget(self.tbl_cart)

        # Cart summary
        summary_layout = QtWidgets.QFormLayout()
        self.lbl_subtotal = QtWidgets.QLabel("₹0.00")
        self.lbl_total_discount = QtWidgets.QLabel("₹0.00")
        self.lbl_total_price = QtWidgets.QLabel("₹0.00")
        summary_layout.addRow("Sub Total:", self.lbl_subtotal)
        summary_layout.addRow("Total Discount:", self.lbl_total_discount)
        summary_layout.addRow("Total Price:", self.lbl_total_price)
        cart_layout.addLayout(summary_layout)

        # Buttons
        btns = QtWidgets.QHBoxLayout()
        btn_submit = QtWidgets.QPushButton("Submit")
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_print = QtWidgets.QPushButton("Print Receipt")
        btn_whatsapp = QtWidgets.QPushButton("Send via WhatsApp")
        btn_submit.clicked.connect(self.on_submit_sale)
        btn_print_courier = QtWidgets.QPushButton("Print Courier Label")
        btn_print_courier.clicked.connect(self.on_print_courier_label)
        btn_cancel.clicked.connect(self.on_clear_cart)
        btn_print.clicked.connect(self.on_print_receipt)
        btn_whatsapp.clicked.connect(self.on_send_whatsapp)
        btns.addWidget(btn_submit)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_print)
        btns.addWidget(btn_whatsapp)
        btns.addWidget(btn_print_courier)

        cart_layout.addLayout(btns)
        cart_group.setLayout(cart_layout)
        right.addWidget(cart_group, 1)

        layout.addLayout(right, 1)

        main_layout.addWidget(top_widget)

        # Bottom section for sales list
        sales_group = QtWidgets.QGroupBox("Recent Sales")
        sales_layout = QtWidgets.QVBoxLayout(sales_group)
        self.tbl_sales = QtWidgets.QTableWidget(0, 5)
        self.tbl_sales.setHorizontalHeaderLabels(["ID", "Date", "Customer", "Total Price", "Items"])
        self.tbl_sales.horizontalHeader().setStretchLastSection(True)
        sales_layout.addWidget(self.tbl_sales)
        main_layout.addWidget(sales_group)


    def _build_customers_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_customers)
        h = QtWidgets.QHBoxLayout()
        self.input_customer_search = QtWidgets.QLineEdit()
        self.input_customer_search.setPlaceholderText("Search customer by name/mobile")
        btn_cust_search = QtWidgets.QPushButton("Search")
        btn_cust_search.clicked.connect(self.on_search_customers)
        self.input_customer_search.returnPressed.connect(self.on_search_customers)
        btn_cust_reset = QtWidgets.QPushButton("Reset")
        btn_cust_reset.clicked.connect(self.on_reset_customer_search)
        h.addWidget(self.input_customer_search)
        h.addWidget(btn_cust_search)
        h.addWidget(btn_cust_reset)
        layout.addLayout(h)

        self.tbl_customers = QtWidgets.QTableWidget(0, 4)
        self.tbl_customers.setHorizontalHeaderLabels(["Name", "Address", "Mobile", "Actions"])
        layout.addWidget(self.tbl_customers)

        btn_add = QtWidgets.QPushButton("Add Customer")
        btn_add.clicked.connect(self.on_add_customer_dialog)
        layout.addWidget(btn_add)

    def _build_products_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_products)
        top = QtWidgets.QHBoxLayout()
        self.input_prodfilter = QtWidgets.QLineEdit()
        self.input_prodfilter.setPlaceholderText("Filter products by name")
        self.category_filter_products = QtWidgets.QComboBox()
        self.category_filter_products.setMinimumWidth(120)
        self.category_filter_products.currentIndexChanged.connect(self.on_search_products)
        btn_pf = QtWidgets.QPushButton("Filter")
        btn_pf.clicked.connect(self.on_search_products)
        self.input_prodfilter.returnPressed.connect(self.on_search_products)
        btn_pr = QtWidgets.QPushButton("Reset")
        btn_pr.clicked.connect(self.on_reset_product_filter)
        top.addWidget(self.input_prodfilter)
        top.addWidget(self.category_filter_products)
        top.addWidget(btn_pf)
        top.addWidget(btn_pr)
        layout.addLayout(top)

        self.tbl_products_full = QtWidgets.QTableWidget(0, 6)
        self.tbl_products_full.setHorizontalHeaderLabels(["Name", "Category", "Size", "Available", "Price", "Actions"])
        layout.addWidget(self.tbl_products_full)

    def _build_offers_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_offers)
        btn_add_offer = QtWidgets.QPushButton("Add Offer")
        btn_add_offer.clicked.connect(self.on_add_offer_dialog)
        layout.addWidget(btn_add_offer)
        self.tbl_offers = QtWidgets.QTableWidget(0, 5)
        self.tbl_offers.setHorizontalHeaderLabels(["Name", "Description", "Type", "Active", "Actions"])
        layout.addWidget(self.tbl_offers)

    def _build_day_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_day)
        # Start Day
        start_group = QtWidgets.QGroupBox("Start Day")
        sg_layout = QtWidgets.QHBoxLayout()
        self.input_opening_balance = QtWidgets.QLineEdit()
        self.input_opening_balance.setPlaceholderText("Opening Balance")
        btn_start_day = QtWidgets.QPushButton("Start Day")
        btn_start_day.clicked.connect(self.on_start_day)
        sg_layout.addWidget(self.input_opening_balance)
        sg_layout.addWidget(btn_start_day)
        start_group.setLayout(sg_layout)
        layout.addWidget(start_group)

        # End Day summary
        end_group = QtWidgets.QGroupBox("Day Summary / End Day")
        eg = QtWidgets.QVBoxLayout()
        self.lbl_day_summary = QtWidgets.QLabel("No day session yet.")
        btn_end_day = QtWidgets.QPushButton("End Day")
        btn_end_day.clicked.connect(self.on_end_day)
        eg.addWidget(self.lbl_day_summary)
        eg.addWidget(btn_end_day)
        end_group.setLayout(eg)
        layout.addWidget(end_group)

    # --------------- Data & helpers ---------------
    def show_loading(self, show=True, text="Loading..."):
        if show:
            self.loading.label.setText(text)
            self.loading.show()
            QtWidgets.QApplication.processEvents()
        else:
            self.loading.hide()

    def run_in_thread(self, fn, callback):
        worker = Worker(fn)
        worker.signals.result.connect(callback)
        QtCore.QThreadPool.globalInstance().start(worker)

    # ---------------- API loads ----------------
    def load_products(self):
        self.show_loading(True, "Loading products...")
        def fetch():
            return api_get(ENDPOINTS["products"])
        def done(res):
            self.show_loading(False)
            if isinstance(res, dict) and res.get("error"):
                QtWidgets.QMessageBox.warning(self, "Error", f"Products load error:\n{res['error']}")
                return
            # expect list of products
            self.all_products_cache = res if isinstance(res, list) else []
            self.populate_products_tables(self.all_products_cache)
        self.run_in_thread(fetch, done)

    def load_customers(self):
        self.show_loading(True, "Loading customers...")
        def fetch():
            return api_get(ENDPOINTS["customers"])
        def done(res):
            self.show_loading(False)
            if isinstance(res, dict) and res.get("error"):
                QtWidgets.QMessageBox.warning(self, "Error", f"Customers load error:\n{res['error']}")
                return
            self.all_customers_cache = res if isinstance(res, list) else []
            self.populate_customers_table(self.all_customers_cache)
        self.run_in_thread(fetch, done)

    def load_offers(self):
        def fetch():
            return api_get(ENDPOINTS["offers"])
        def done(res):
            if isinstance(res, dict) and res.get("error"):
                return
            self.all_offers_cache = res if isinstance(res, list) else []
            self.populate_offers_table(self.all_offers_cache)
        self.run_in_thread(fetch, done)

    def load_categories(self):
        def fetch():
            return api_get(ENDPOINTS["categories"])
        def done(res):
            if isinstance(res, dict) and res.get("error"):
                # Silently fail is ok for now
                return
            self.all_categories_cache = res if isinstance(res, list) else []
            self.populate_category_filters()
        self.run_in_thread(fetch, done)

    def load_payment_types(self):
        def fetch():
            return api_get(ENDPOINTS["payment_types"])
        def done(res):
            self.all_payment_types_cache = res if isinstance(res, list) else []
            self.populate_payment_types()
        self.run_in_thread(fetch, done)

    def load_delivery_types(self):
        def fetch():
            return api_get(ENDPOINTS["delivery_types"])
        def done(res):
            self.all_delivery_types_cache = res if isinstance(res, list) else []
            self.populate_delivery_types()
        self.run_in_thread(fetch, done)

    def load_sales(self):
        def fetch():
            return api_get(ENDPOINTS["sales/all"])
        def done(res):
            self.all_sales_cache = res if isinstance(res, list) else []
            self.populate_sales_table(self.all_sales_cache)
        self.run_in_thread(fetch, done)

    # ---------------- Populate UI ----------------
    def populate_products_tables(self, products):
        # small products table (search results)
        self.tbl_products.setRowCount(0)
        for p in products:
            row = self.tbl_products.rowCount()
            self.tbl_products.insertRow(row)
            self.tbl_products.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p.get("name", ""))))
            self.tbl_products.setItem(row, 1, QtWidgets.QTableWidgetItem(str(p.get("category", {}).get("name", ""))))
            self.tbl_products.setItem(row, 2, QtWidgets.QTableWidgetItem(str(p.get("size", ""))))
            self.tbl_products.setItem(row, 3, QtWidgets.QTableWidgetItem(str(p.get("available_quantity", ""))))
            self.tbl_products.setItem(row, 4, QtWidgets.QTableWidgetItem(str(p.get("selling_price", ""))))
            btn = QtWidgets.QPushButton("Add")
            btn.clicked.connect(partial(self.on_add_product_to_cart, p))
            self.tbl_products.setCellWidget(row, 5, btn)

        # full products table
        self.tbl_products_full.setRowCount(0)
        for p in products:
            row = self.tbl_products_full.rowCount()
            self.tbl_products_full.insertRow(row)
            self.tbl_products_full.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p.get("name", ""))))
            self.tbl_products_full.setItem(row, 1, QtWidgets.QTableWidgetItem(str(p.get("category", {}).get("name", ""))))
            self.tbl_products_full.setItem(row, 2, QtWidgets.QTableWidgetItem(str(p.get("size", ""))))
            self.tbl_products_full.setItem(row, 3, QtWidgets.QTableWidgetItem(str(p.get("available_quantity", ""))))
            self.tbl_products_full.setItem(row, 4, QtWidgets.QTableWidgetItem(str(p.get("selling_price", ""))))
            w = QtWidgets.QWidget()
            lay = QtWidgets.QHBoxLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            btn_edit = QtWidgets.QPushButton("Edit")
            lay.addWidget(btn_edit)
            w.setLayout(lay)
            self.tbl_products_full.setCellWidget(row, 5, w)

    def populate_customers_table(self, customers):
        self.tbl_customers.setRowCount(0)
        for c in customers:
            row = self.tbl_customers.rowCount()
            self.tbl_customers.insertRow(row)
            self.tbl_customers.setItem(row, 0, QtWidgets.QTableWidgetItem(str(c.get("name", ""))))
            self.tbl_customers.setItem(row, 1, QtWidgets.QTableWidgetItem(str(c.get("address", ""))))
            self.tbl_customers.setItem(row, 2, QtWidgets.QTableWidgetItem(str(c.get("mobile", ""))))
            btns = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            b_edit = QtWidgets.QPushButton("Edit")
            b_delete = QtWidgets.QPushButton("Delete")
            layout.addWidget(b_edit); layout.addWidget(b_delete)
            btns.setLayout(layout)
            self.tbl_customers.setCellWidget(row, 3, btns)

    def populate_offers_table(self, offers):
        self.tbl_offers.setRowCount(0)
        self.offer_combo.clear()
        self.offer_combo.addItem("Select an offer", userData=None)
        for o in offers:
            row = self.tbl_offers.rowCount()
            self.tbl_offers.insertRow(row)
            self.tbl_offers.setItem(row, 0, QtWidgets.QTableWidgetItem(str(o.get("name", ""))))
            self.tbl_offers.setItem(row, 1, QtWidgets.QTableWidgetItem(str(o.get("description", ""))))
            self.tbl_offers.setItem(row, 2, QtWidgets.QTableWidgetItem(str(o.get("type", ""))))
            self.tbl_offers.setItem(row, 3, QtWidgets.QTableWidgetItem("Yes" if o.get("is_active") else "No"))
            self.tbl_offers.setItem(row, 4, QtWidgets.QTableWidgetItem(""))
            if o.get("is_active"):
                self.offer_combo.addItem(o.get("name"), userData=o)

    def populate_payment_types(self):
        self.payment_type_combo.clear()
        self.payment_type_combo.addItem("Select Payment Type", userData=None)
        for pt in self.all_payment_types_cache:
            self.payment_type_combo.addItem(pt["name"], userData=pt["id"])

    def populate_delivery_types(self):
        self.delivery_type_combo.clear()
        self.delivery_type_combo.addItem("Select Delivery Type", userData=None)
        for dt in self.all_delivery_types_cache:
            self.delivery_type_combo.addItem(dt["name"], userData=dt["id"])

    def populate_sales_table(self, sales):
        self.tbl_sales.setRowCount(0)
        for s in sales:
            row = self.tbl_sales.rowCount()
            self.tbl_sales.insertRow(row)
            self.tbl_sales.setItem(row, 0, QtWidgets.QTableWidgetItem(str(s.get("id", ""))))
            self.tbl_sales.setItem(row, 1, QtWidgets.QTableWidgetItem(str(s.get("date", ""))))
            self.tbl_sales.setItem(row, 2, QtWidgets.QTableWidgetItem(str(s.get("customer_name", ""))))
            self.tbl_sales.setItem(row, 3, QtWidgets.QTableWidgetItem(str(s.get("total_price", ""))))
            self.tbl_sales.setItem(row, 4, QtWidgets.QTableWidgetItem(str(s.get("total_quantity", ""))))

    def populate_category_filters(self):
        # Sales tab
        self.category_filter_sale.clear()
        self.category_filter_sale.addItem("All Categories", userData=None)
        for cat in self.all_categories_cache:
            self.category_filter_sale.addItem(cat["name"], userData=cat["id"])

        # Products tab
        self.category_filter_products.clear()
        self.category_filter_products.addItem("All Categories", userData=None)
        for cat in self.all_categories_cache:
            self.category_filter_products.addItem(cat["name"], userData=cat["id"])

    # ---------------- Actions ----------------
    def on_search_products(self):
        # Determine active tab and get corresponding widgets
        active_tab_idx = self.tabs.currentIndex()
        is_sales_tab = self.tabs.tabText(active_tab_idx) == "New Sale"

        if is_sales_tab:
            term = self.input_product_search.text().strip()
            cat_id = self.category_filter_sale.currentData()
        else:
            term = self.input_prodfilter.text().strip()
            cat_id = self.category_filter_products.currentData()

        # Filter by term
        if term:
            filtered = [p for p in self.all_products_cache if term.lower() in str(p.get("name", "")).lower()]
        else:
            filtered = self.all_products_cache[:]

        # Filter by category
        if cat_id is not None:
            filtered = [p for p in filtered if p.get("category", {}).get("id") == cat_id]

        self.populate_products_tables(filtered)

    def on_reset_product_filter(self):
        self.input_prodfilter.clear()
        self.category_filter_products.setCurrentIndex(0)
        self.populate_products_tables(self.all_products_cache)

    def on_search_customers(self):
        term = self.input_customer_search.text().strip()
        if not term:
            self.populate_customers_table(self.all_customers_cache)
            return
        filtered = [c for c in self.all_customers_cache if term.lower() in str(c.get("name", "")).lower() or term in str(c.get("mobile", ""))]
        self.populate_customers_table(filtered)

    def on_reset_customer_search(self):
        self.input_customer_search.clear()
        self.populate_customers_table(self.all_customers_cache)

    def on_add_product_to_cart(self, product):
        # Add the whole product to the cart item to have access to all its details later
        # The price from the API is now 'selling_price'
        # The cart needs to be aware of the full product object to build the sale payload
        cart_item = {
            "product": product,
            "qty": 1,
            "price": float(product.get("selling_price") or 0),
            "discounted_price": float(product.get("selling_price") or 0), # Assuming no discount by default
        }
        self.cart.append(cart_item)
        self.refresh_cart_table()

    def refresh_cart_table(self):
        self.tbl_cart.setRowCount(0)
        subtotal = 0.0
        total_disc = 0.0
        for item in self.cart:
            row = self.tbl_cart.rowCount()
            self.tbl_cart.insertRow(row)
            self.tbl_cart.setItem(row, 0, QtWidgets.QTableWidgetItem(item["product"]["name"]))

            # qty widget
            spin = QtWidgets.QSpinBox()
            spin.setValue(item["qty"])
            spin.setMinimum(1)
            spin.valueChanged.connect(partial(self.on_cart_qty_changed, row))
            self.tbl_cart.setCellWidget(row, 1, spin)

            self.tbl_cart.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{item['price']:.2f}"))
            self.tbl_cart.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{item['discounted_price']:.2f}"))

            total = item["qty"] * item["discounted_price"]
            self.tbl_cart.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

            subtotal += item["qty"] * item["price"]
            total_disc += item["qty"] * (item["price"] - item["discounted_price"])

        self.lbl_subtotal.setText(f"₹{subtotal:.2f}")
        self.lbl_total_discount.setText(f"₹{total_disc:.2f}")
        self.lbl_total_price.setText(f"₹{(subtotal - total_disc):.2f}")

    def on_cart_qty_changed(self, row, value):
        if row < 0 or row >= len(self.cart):
            return
        self.cart[row]["qty"] = value
        self.refresh_cart_table()

    def on_clear_cart(self):
        self.cart = []
        self.refresh_cart_table()
        self.cust_name.clear()
        self.cust_mobile.clear()
        self.cust_address.clear()

    def on_submit_sale(self):
        if not self.cart:
            QtWidgets.QMessageBox.warning(self, "Empty cart", "Cart is empty.")
            return

        # Rebuild payload to match the new SaleCreate schema
        total_quantity = sum(item['qty'] for item in self.cart)
        total_price = float(self.lbl_total_price.text().replace("₹", ""))

        sale_items = []
        for item in self.cart:
            product = item['product']
            # The product in the cart now contains all necessary details
            sale_item_payload = {
                "product_id": product['id'],
                "product_name": product['name'],
                "product_category": product['category']['name'] if product.get('category') else 'N/A',
                "size": product.get('size', 'N/A'),
                "quantity_available": product.get('available_quantity', 0),
                "quantity": item['qty'],
                "sale_price": item['discounted_price'],
                "total_price": item['qty'] * item['discounted_price'],
            }
            sale_items.append(sale_item_payload)

        payment_type_id = self.payment_type_combo.currentData()
        delivery_type_id = self.delivery_type_combo.currentData()

        if not payment_type_id:
            QtWidgets.QMessageBox.warning(self, "Input required", "Please select a payment type.")
            return
        if not delivery_type_id:
            QtWidgets.QMessageBox.warning(self, "Input required", "Please select a delivery type.")
            return

        payload = {
            "date": self.sale_date.date().toString(QtCore.Qt.ISODate),
            "total_quantity": total_quantity,
            "total_price": total_price,
            "payment_type_id": payment_type_id,
            "delivery_type_id": delivery_type_id,
            "shop_id": 1,  # Defaulting to shop_id 1
            "customer_id": 1,  # Defaulting to a guest/default customer
            "customer_name": self.cust_name.text(),
            "customer_address": self.cust_address.toPlainText(),
            "customer_mobile": self.cust_mobile.text(),
            "sale_items": sale_items,
        }

        self.show_loading(True, "Submitting sale...")
        def do_submit():
            return api_post(ENDPOINTS["sales"], payload)
        def done(res):
            self.show_loading(False)
            if isinstance(res, dict) and res.get("error"):
                QtWidgets.QMessageBox.critical(self, "Error", f"Sale submission failed:\n{res['error']}")
                return
            QtWidgets.QMessageBox.information(self, "Success", "Sale submitted successfully.")
            self.on_clear_cart()
            self.load_sales()
        self.run_in_thread(do_submit, done)

    def on_print_receipt(self):
        # Placeholder: implement printing logic (generate PDF or system print)
        QtWidgets.QMessageBox.information(self, "Print", "Print receipt: Not implemented. Generate PDF/print here.")

    def on_print_courier_label(self):
        # Placeholder: implement printing logic (generate PDF or system print)
        QtWidgets.QMessageBox.information(self, "Print", "Print courier label: Not implemented. Generate PDF/print here.")

    def on_send_whatsapp(self):
        # Placeholder: integrate WhatsApp Business API or open web.whatsapp with prefilled message
        QtWidgets.QMessageBox.information(self, "WhatsApp", "Send via WhatsApp: Not implemented. Hook here to send message.")

    def on_apply_offer(self):
        offer = self.offer_combo.currentData()
        if not offer:
            QtWidgets.QMessageBox.warning(self, "No offer selected", "Please select an offer to apply.")
            return

        if not self.cart:
            QtWidgets.QMessageBox.warning(self, "Empty Cart", "Cannot apply offer to an empty cart.")
            return

        # Placeholder for offer logic
        QtWidgets.QMessageBox.information(self, "Apply Offer", f"Applying offer: {offer.get('name')}. Not implemented.")

    # ---------------- Customers / Offers dialogs ----------------
    def on_add_customer_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add Customer")
        layout = QtWidgets.QFormLayout(dlg)
        name = QtWidgets.QLineEdit()
        mobile = QtWidgets.QLineEdit()
        address = QtWidgets.QTextEdit()
        layout.addRow("Name", name)
        layout.addRow("Mobile", mobile)
        layout.addRow("Address", address)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            payload = {"name": name.text(), "mobile": mobile.text(), "address": address.toPlainText()}
            self.show_loading(True, "Adding customer...")
            def do_add():
                return api_post(ENDPOINTS["customers/create"], payload)
            def done(res):
                self.show_loading(False)
                if isinstance(res, dict) and res.get("error"):
                    QtWidgets.QMessageBox.critical(self, "Error", f"Add customer failed:\n{res['error']}")
                    return
                QtWidgets.QMessageBox.information(self, "Success", "Customer added.")
                self.load_customers()
            self.run_in_thread(do_add, done)

    def on_add_offer_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add Offer")
        layout = QtWidgets.QFormLayout(dlg)
        name = QtWidgets.QLineEdit()
        desc = QtWidgets.QLineEdit()
        typ = QtWidgets.QComboBox()
        typ.addItems(["percentage", "fixed"])
        active = QtWidgets.QCheckBox()
        layout.addRow("Name", name)
        layout.addRow("Description", desc)
        layout.addRow("Type", typ)
        layout.addRow("Active", active)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # Map UI type to API RateType
            rate_type_map = {"percentage": "percentage", "fixed": "flat"}
            rate_type = rate_type_map.get(typ.currentText(), "flat")

            # TODO: The following values are hardcoded because the current UI for
            # creating an offer is very simple. A full implementation would require
            # UI elements for selecting dates, rate, and associating products/categories.
            payload = {
                "name": name.text(),
                "description": desc.text(),
                "type": "offer",  # Defaulting type to 'offer'
                "is_active": bool(active.isChecked()),
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "rate_type": rate_type,
                "rate": 0,  # Defaulting rate to 0
                "product_ids": [], # Not supported in current UI
                "category_ids": [],# Not supported in current UI
            }
            self.show_loading(True, "Adding offer...")
            def do_add():
                return api_post(ENDPOINTS["offers/create"], payload)
            def done(res):
                self.show_loading(False)
                if isinstance(res, dict) and res.get("error"):
                    QtWidgets.QMessageBox.critical(self, "Error", f"Add offer failed:\n{res['error']}")
                    return
                QtWidgets.QMessageBox.information(self, "Success", "Offer added.")
                self.load_offers()
            self.run_in_thread(do_add, done)

    # ---------------- Day management ----------------
    def on_start_day(self):
        amt_text = self.input_opening_balance.text().strip()
        if not amt_text:
            QtWidgets.QMessageBox.warning(self, "Input required", "Enter opening balance amount.")
            return
        try:
            amt = float(amt_text)
        except:
            QtWidgets.QMessageBox.warning(self, "Invalid", "Opening balance must be a number.")
            return
        payload = {"opening_balance": amt}
        self.show_loading(True, "Starting day...")
        def do_start():
            return api_post(ENDPOINTS["day/start"], payload)
        def done(res):
            self.show_loading(False)
            if isinstance(res, dict) and res.get("error"):
                QtWidgets.QMessageBox.critical(self, "Error", f"Start day failed:\n{res['error']}")
                return
            self.lbl_day_summary.setText(f"Day started. Opening balance: ₹{amt:.2f}")
            QtWidgets.QMessageBox.information(self, "Day Started", "Day session started.")
        self.run_in_thread(do_start, done)

    def on_end_day(self):
        self.show_loading(True, "Ending day...")

        def get_and_end_day():
            # Step 1: Get the active day
            active_day_res = api_get(ENDPOINTS["day/active"])
            if isinstance(active_day_res, dict) and active_day_res.get("error"):
                return {"error": f"Could not get active day: {active_day_res['error']}"}
            if not active_day_res or "id" not in active_day_res:
                return {"error": "No active day found to end."}
            
            day_id = active_day_res["id"]
            
            # Step 2: End the day using the ID. The day_id is passed as a path parameter.
            # The API endpoint is defined as "/endDay/{day_id}", so we format the URL accordingly.
            # The backend service calculates the summary, so an empty payload is sufficient.
            end_day_res = api_post(f"{ENDPOINTS['day/end']}/{day_id}", {})
            return end_day_res

        def done(res):
            self.show_loading(False)
            if isinstance(res, dict) and res.get("error"):
                QtWidgets.QMessageBox.critical(self, "Error", f"End day failed:\n{res['error']}")
                return

            # Response from endDay is now DaySummary
            summary = res  # The response itself is the summary
            if summary:
                text = (
                    f"Day Ended Successfully!\n"
                    f"Opening Balance: ₹{summary.get('opening_balance', 0):.2f}\n"
                    f"Total Expenses: ₹{summary.get('total_expense', 0):.2f}\n"
                    f"Closing Balance: ₹{summary.get('closing_balance', 0):.2f}\n"
                    f"Start Time: {summary.get('start_time')}\n"
                    f"End Time: {summary.get('end_time')}\n"
                )
            else:
                text = "Day ended. (No summary returned)"
            self.lbl_day_summary.setText(text)
            QtWidgets.QMessageBox.information(self, "Day Ended", "Day ended successfully.")

        self.run_in_thread(get_and_end_day, done)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AdrenalineApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
