# frontend_pharmacy_with_privileges.py
# Full Pharmacy Management System with Role-Based Access Control (RBAC)
# Integrated login system with privilege management

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta

# ---------- DB CONFIG ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your password",
    "database": "PharmacyDB",
    "port": 3306
}

# ---------- HARDCODED ADMIN CREDENTIALS ----------
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# ---------- PRIVILEGE DEFINITIONS ----------
PRIVILEGES = {
    "Admin": {
        "tabs": ["Dashboard", "Employees", "Suppliers", "Medicines", "Customers", 
                 "Orders", "Ordered Drugs", "Bills", "Disposals", "Prescriptions", 
                 "Notifications", "Queries"],
        "can_add": True,
        "can_edit": True,
        "can_delete": True,
        "can_view_salary": True,
        "can_manage_employees": True
    },
    "Supervisor": {
        "tabs": ["Dashboard", "Employees", "Suppliers", "Medicines", "Customers", 
                 "Orders", "Ordered Drugs", "Bills", "Disposals", "Prescriptions", 
                 "Notifications", "Queries"],
        "can_add": True,
        "can_edit": True,
        "can_delete": True,
        "can_view_salary": True,
        "can_manage_employees": False  # Cannot manage employees
    },
    "Pharmacist": {
        "tabs": ["Dashboard", "Medicines", "Customers", "Orders", "Ordered Drugs", 
                 "Bills", "Prescriptions", "Notifications"],
        "can_add": True,
        "can_edit": True,
        "can_delete": False,
        "can_view_salary": False,
        "can_manage_employees": False
    },
    "Cashier": {
        "tabs": ["Dashboard", "Customers", "Orders", "Ordered Drugs", "Bills"],
        "can_add": True,
        "can_edit": False,
        "can_delete": False,
        "can_view_salary": False,
        "can_manage_employees": False
    },
    "Manager": {
        "tabs": ["Dashboard", "Employees", "Suppliers", "Medicines", "Customers", 
                 "Orders", "Ordered Drugs", "Bills", "Disposals", "Queries"],
        "can_add": True,
        "can_edit": True,
        "can_delete": True,
        "can_view_salary": True,
        "can_manage_employees": True
    }
}

# ---------- DB HELPERS ----------
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("DB Connection Error", f"Unable to connect to DB:\n{e}")
        return None

def run_select(query, params=()):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        rows = cur.fetchall()
        return rows
    except Error as e:
        messagebox.showerror("Query Error", str(e))
        return []
    finally:
        cur.close()
        conn.close()

def run_select_with_cols(query, params=()):
    """Return (columns, rows) for arbitrary SELECTs."""
    conn = get_connection()
    if not conn:
        return [], []
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        rows = cur.fetchall()
        cols = cur.column_names
        return cols, rows
    except Error as e:
        messagebox.showerror("Query Error", str(e))
        return [], []
    finally:
        cur.close()
        conn.close()

def run_query(query, params=()):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Query Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def call_procedure(procname, params=()):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.callproc(procname, params)
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Procedure Error", f"{procname}: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_next_nid():
    rows = run_select("SELECT NID FROM NOTIFICATION ORDER BY NID DESC LIMIT 1")
    if not rows or rows[0][0] is None:
        return "N001"
    try:
        last_nid = rows[0][0]
        num = int(last_nid[1:]) + 1
        return f"N{num:03d}"
    except:
        return "N001"

# ---------- LOGIN WINDOW ----------
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacy Management System - Login")
        self.geometry("450x350")
        self.resizable(False, False)
        
        # Center the window
        self.eval('tk::PlaceWindow . center')
        
        try:
            ttk.Style(self).theme_use("clam")
        except:
            pass
        
        self.logged_in_user = None
        self.user_role = None
        
        self.create_login_ui()
        
    def create_login_ui(self):
        main_frame = ttk.Frame(self, padding="30")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🏥 Pharmacy Login", 
                         font=("Segoe UI", 20, "bold"))
        title.pack(pady=(0, 40))
        
        # Employee ID / Username
        ttk.Label(main_frame, text="Username / Employee ID:", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        self.empid_entry = ttk.Entry(main_frame, width=35, font=("Segoe UI", 10))
        self.empid_entry.pack(pady=(0, 20))
        
        # Auth Key (Password)
        ttk.Label(main_frame, text="Password:", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        self.auth_entry = ttk.Entry(main_frame, width=35, show="●", font=("Segoe UI", 10))
        self.auth_entry.pack(pady=(0, 25))
        
        # Login button
        login_btn = ttk.Button(main_frame, text="Login", command=self.attempt_login)
        login_btn.pack(pady=10, ipadx=20, ipady=5)
        
        # Bind Enter key
        self.empid_entry.bind("<Return>", lambda e: self.auth_entry.focus())
        self.auth_entry.bind("<Return>", lambda e: self.attempt_login())
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red", font=("Segoe UI", 9))
        self.status_label.pack(pady=15)
        
        # Demo credentials hint
        hint_frame = ttk.Frame(main_frame)
        hint_frame.pack(pady=5)
        
        ttk.Label(hint_frame, text="💡 Admin Login: ", foreground="gray", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        ttk.Label(hint_frame, text="Username: admin | Password: admin123", 
                 foreground="gray", font=("Segoe UI", 8)).pack(anchor="w")
        ttk.Label(hint_frame, text="(Other users: Check EMPLOYEE table)", 
                 foreground="gray", font=("Segoe UI", 8)).pack(anchor="w", pady=(5,0))
        
        self.empid_entry.focus()
        
    def attempt_login(self):
        empid = self.empid_entry.get().strip()
        auth = self.auth_entry.get().strip()
        
        if not empid or not auth:
            self.status_label.config(text="⚠ Please enter both Username and Password")
            return
        
        # Check hardcoded admin first
        if empid == ADMIN_CREDENTIALS["username"] and auth == ADMIN_CREDENTIALS["password"]:
            self.logged_in_user = "ADMIN"
            self.user_name = "System Administrator"
            self.user_role = "Admin"
            
            # Success - Admin login
            self.withdraw()
            app = PharmacyApp(self.logged_in_user, self.user_name, self.user_role)
            app.mainloop()
            self.destroy()
            return
        
        # Query database for regular users
        rows = run_select(
            "SELECT EmpID, Ename, Role FROM EMPLOYEE WHERE EmpID=%s AND AuthKey=%s",
            (empid, auth)
        )
        
        if rows:
            self.logged_in_user = rows[0][0]
            self.user_name = rows[0][1]
            self.user_role = rows[0][2]
            
            if self.user_role not in PRIVILEGES:
                self.status_label.config(
                    text=f"⚠ Role '{self.user_role}' not recognized. Contact admin."
                )
                return
            
            # Success
            self.withdraw()
            app = PharmacyApp(self.logged_in_user, self.user_name, self.user_role)
            app.mainloop()
            self.destroy()
        else:
            self.status_label.config(text="❌ Invalid Username or Password")
            self.auth_entry.delete(0, 'end')

# ---------- MAIN APPLICATION ----------
class PharmacyApp(tk.Tk):
    WARN_DAYS = 7

    def __init__(self, empid, emp_name, role):
        super().__init__()
        self.current_user = empid
        self.current_user_name = emp_name
        self.current_role = role
        self.privileges = PRIVILEGES.get(role, PRIVILEGES["Cashier"])
        
        self.title(f"Pharmacy Management System - {emp_name} ({role})")
        self.geometry("1180x720")
        
        try:
            ttk.Style(self).theme_use("clam")
        except:
            pass
        
        self.resizable(True, True)
        
        # Top bar with user info
        self.create_top_bar()
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        # Create tabs based on privileges
        self.create_tabs_based_on_role()
        
        self.refresh_all()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_top_bar(self):
        top_bar = ttk.Frame(self, style="Accent.TFrame")
        top_bar.pack(fill="x", padx=10, pady=5)
        
        user_info = ttk.Label(
            top_bar, 
            text=f"👤 Logged in: {self.current_user_name} ({self.current_user}) | Role: {self.current_role}",
            font=("Segoe UI", 10, "bold")
        )
        user_info.pack(side="left", padx=5)
        
        logout_btn = ttk.Button(top_bar, text="🚪 Logout", command=self.logout)
        logout_btn.pack(side="right", padx=5)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            login = LoginWindow()
            login.mainloop()

    def check_permission(self, action):
        """Check if current user has permission for an action"""
        if action == "add":
            return self.privileges["can_add"]
        elif action == "edit":
            return self.privileges["can_edit"]
        elif action == "delete":
            return self.privileges["can_delete"]
        return False

    def create_tabs_based_on_role(self):
        allowed_tabs = self.privileges["tabs"]
        
        if "Dashboard" in allowed_tabs:
            self.create_dashboard_tab()
        if "Employees" in allowed_tabs:
            self.create_employee_tab()
        if "Suppliers" in allowed_tabs:
            self.create_supplier_tab()
        if "Medicines" in allowed_tabs:
            self.create_medicine_tab()
        if "Customers" in allowed_tabs:
            self.create_customer_tab()
        if "Orders" in allowed_tabs:
            self.create_order_tab()
        if "Ordered Drugs" in allowed_tabs:
            self.create_ordered_drug_tab()
        if "Bills" in allowed_tabs:
            self.create_bill_tab()
        if "Disposals" in allowed_tabs:
            self.create_disposal_tab()
        if "Prescriptions" in allowed_tabs:
            self.create_prescription_tab()
        if "Notifications" in allowed_tabs:
            self.create_notifications_tab()
        if "Queries" in allowed_tabs:
            self.create_queries_tab()

    def on_exit(self):
        if messagebox.askokcancel("Quit", "Exit PharmacyApp?"):
            self.destroy()

    # ---------------- Dashboard ----------------
    def create_dashboard_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Dashboard")
        title = ttk.Label(frame, text="Dashboard", font=("Segoe UI", 16))
        title.pack(anchor="w", padx=10, pady=8)
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="w", padx=10, pady=6)
        ttk.Button(btn_frame, text="Refresh All", command=self.refresh_all).pack(side="left", padx=4)
        ttk.Button(btn_frame, text=f"Check Expiry (now + {self.WARN_DAYS} days)", command=self.check_expiry_notifications).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Show Total Stock Value", command=self.show_total_stock_value).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Show Unseen Notifications Count", command=self.show_unseen_notifications_count).pack(side="left", padx=4)
        self.log = tk.Text(frame, height=10, state="disabled")
        self.log.pack(fill="both", expand=False, padx=10, pady=8)

    def append_log(self, text):
        if hasattr(self, 'log'):
            self.log.config(state="normal")
            self.log.insert("end", f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
            self.log.see("end")
            self.log.config(state="disabled")

    def refresh_all(self):
        self.append_log("Refreshing all lists...")
        if hasattr(self, 'emp_tree'):
            self.load_employees()
        if hasattr(self, 'sup_tree'):
            self.load_suppliers()
        if hasattr(self, 'med_tree'):
            self.load_medicines()
        if hasattr(self, 'cust_tree'):
            self.load_customers()
        if hasattr(self, 'order_tree'):
            self.load_orders()
        if hasattr(self, 'od_tree'):
            self.load_ordered_drugs()
        if hasattr(self, 'bill_tree'):
            self.load_bills()
        if hasattr(self, 'disp_tree'):
            self.load_disposals()
        if hasattr(self, 'pres_tree'):
            self.load_prescriptions()
        if hasattr(self, 'notif_tree'):
            self.load_notifications()
        self.append_log("Refresh complete.")
        self.check_expiry_notifications()

    def check_expiry_notifications(self):
        rows = run_select("SELECT BatchNo, DrugName, ExpiryDate, Stock_quantity FROM MEDICINE")
        if not rows:
            self.append_log("No medicines found for expiry check.")
            return
        today = date.today()
        warn_until = today + timedelta(days=self.WARN_DAYS)
        expired = []
        expiring_soon = []
        for batch, name, exp_dt, stock in rows:
            if exp_dt is None:
                continue
            if isinstance(exp_dt, datetime):
                exp = exp_dt.date()
            elif isinstance(exp_dt, date):
                exp = exp_dt
            else:
                try:
                    exp = datetime.strptime(str(exp_dt), "%Y-%m-%d").date()
                except:
                    continue
            if exp < today:
                expired.append((batch, name, exp, stock))
            elif today <= exp <= warn_until:
                expiring_soon.append((batch, name, exp, stock))
        if expired:
            msg_lines = [f"{b} | {n} | Expired on: {e} | Qty: {s}" for b, n, e, s in expired]
            msg = "Expired medicines:\n" + "\n".join(msg_lines)
            self.append_log(f"Expired medicines detected: {len(expired)}")
            messagebox.showwarning("Expired Medicines", msg)
        else:
            self.append_log("No expired medicines found.")
        if expiring_soon:
            msg_lines = [f"{b} | {n} | Expires: {e} | Qty: {s}" for b, n, e, s in expiring_soon]
            msg = f"Medicines expiring within {self.WARN_DAYS} days:\n" + "\n".join(msg_lines)
            self.append_log(f"Expiring soon medicines detected: {len(expiring_soon)}")
            messagebox.showinfo("Expiring Soon", msg)
        else:
            self.append_log(f"No medicines expiring within {self.WARN_DAYS} days.")

    def show_total_stock_value(self):
        cols, rows = run_select_with_cols("SELECT TotalStockValue()")
        if rows:
            val = rows[0][0]
            messagebox.showinfo("Total Stock Value", f"Total stock value: {val}")
            self.append_log(f"TotalStockValue() -> {val}")
        else:
            messagebox.showinfo("Total Stock Value", "No data or error computing stock value.")

    def show_unseen_notifications_count(self):
        rows = run_select("SELECT COUNT(*) FROM NOTIFICATION n WHERE NOT EXISTS (SELECT 1 FROM IS_NOTIFIED i WHERE i.NID = n.NID)")
        if rows:
            cnt = rows[0][0]
            messagebox.showinfo("Unseen Notifications", f"Unseen notifications: {cnt}")
            self.append_log(f"Unseen notifications: {cnt}")
        else:
            messagebox.showinfo("Unseen Notifications", "0")
            self.append_log("Unseen notifications: 0")

    # ---------------- Employee ----------------
    def create_employee_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Employees")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_employees).pack(side="left", padx=4)
        
        if self.check_permission("add") and self.privileges["can_manage_employees"]:
            ttk.Button(top, text="Add Employee", command=self.add_employee_dialog).pack(side="left", padx=4)
        
        if self.check_permission("delete") and self.privileges["can_manage_employees"]:
            ttk.Button(top, text="Delete Selected", command=self.delete_employee_selected).pack(side="left", padx=4)
        
        if self.check_permission("edit") and self.privileges["can_manage_employees"]:
            ttk.Button(top, text="Update Selected", command=self.update_employee_dialog).pack(side="left", padx=4)
        
        if self.privileges["can_view_salary"]:
            cols = ("EmpID","Ename","DOB","Role","Salary","Phone","AuthKey")
        else:
            cols = ("EmpID","Ename","DOB","Role","Phone")
        
        self.emp_tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.emp_tree.heading(c, text=c)
            self.emp_tree.column(c, width=110)
        self.emp_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_employees(self):
        if self.privileges["can_view_salary"]:
            rows = run_select("SELECT EmpID, Ename, DOB, Role, Salary, Phone, AuthKey FROM EMPLOYEE")
        else:
            rows = run_select("SELECT EmpID, Ename, DOB, Role, Phone FROM EMPLOYEE")
        
        self.emp_tree.delete(*self.emp_tree.get_children())
        for r in rows:
            row = list(r)
            if row[2]:
                try:
                    row[2] = row[2].strftime("%Y-%m-%d")
                except:
                    pass
            self.emp_tree.insert("", "end", values=tuple(row))

    def add_employee_dialog(self):
        if not self.check_permission("add") or not self.privileges["can_manage_employees"]:
            messagebox.showwarning("Permission Denied", "You don't have permission to add employees")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Employee")
        labels = ["EmpID","Ename","DOB (YYYY-MM-DD)","Role","Salary","Phone","AuthKey"]
        entries = {}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            empid = entries["EmpID"].get().strip(); ename = entries["Ename"].get().strip()
            dob = entries["DOB (YYYY-MM-DD)"].get().strip() or None
            role = entries["Role"].get().strip() or None
            try:
                salary = float(entries["Salary"].get().strip() or 0)
            except:
                messagebox.showwarning("Input","Salary must be numeric"); return
            phone = entries["Phone"].get().strip() or None
            auth = entries["AuthKey"].get().strip() or None
            if not empid or not ename:
                messagebox.showwarning("Input", "EmpID and Ename required"); return
            q = "INSERT INTO EMPLOYEE (EmpID, Ename, DOB, Role, Salary, Phone, AuthKey) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            if run_query(q, (empid, ename, dob, role, salary, phone, auth)):
                messagebox.showinfo("Added","Employee added")
                dlg.destroy(); self.load_employees()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def update_employee_dialog(self):
        if not self.check_permission("edit") or not self.privileges["can_manage_employees"]:
            messagebox.showwarning("Permission Denied", "You don't have permission to update employees")
            return
        
        sel = self.emp_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select employee to update"); return
        vals = self.emp_tree.item(sel[0])['values']
        empid = vals[0]
        dlg = tk.Toplevel(self); dlg.title(f"Update Employee {empid}")
        labels = ["Ename","DOB (YYYY-MM-DD)","Role","Salary","Phone","AuthKey"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg)
            pre = vals[i+1] if i+1 < len(vals) else ""
            if pre is not None:
                e.insert(0, pre)
            e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            ename = entries["Ename"].get().strip()
            dob = entries["DOB (YYYY-MM-DD)"].get().strip() or None
            role = entries["Role"].get().strip() or None
            try:
                salary = float(entries["Salary"].get().strip() or 0)
            except:
                messagebox.showwarning("Input","Salary numeric"); return
            phone = entries["Phone"].get().strip() or None
            auth = entries["AuthKey"].get().strip() or None
            q = """UPDATE EMPLOYEE SET Ename=%s, DOB=%s, Role=%s, Salary=%s, Phone=%s, AuthKey=%s WHERE EmpID=%s"""
            if run_query(q, (ename, dob, role, salary, phone, auth, empid)):
                messagebox.showinfo("Updated","Employee updated"); dlg.destroy(); self.load_employees()
        ttk.Button(dlg, text="Update", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_employee_selected(self):
        if not self.check_permission("delete") or not self.privileges["can_manage_employees"]:
            messagebox.showwarning("Permission Denied", "You don't have permission to delete employees")
            return
        
        sel = self.emp_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select employee to delete"); return
        vals = self.emp_tree.item(sel[0])['values']
        empid = vals[0]
        if messagebox.askyesno("Confirm", f"Delete employee {empid}?"):
            if run_query("DELETE FROM EMPLOYEE WHERE EmpID=%s", (empid,)):
                messagebox.showinfo("Deleted","Employee deleted"); self.load_employees()

    # ---------------- Supplier ----------------
    def create_supplier_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Suppliers")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_suppliers).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Supplier", command=self.add_supplier_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_supplier_selected).pack(side="left", padx=4)
        if self.check_permission("edit"):
            ttk.Button(top, text="Update Selected", command=self.update_supplier_dialog).pack(side="left", padx=4)
        
        cols = ("SupID","SupName","License_no","Email","Phone","Street","City")
        self.sup_tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.sup_tree.heading(c, text=c)
            self.sup_tree.column(c, width=120)
        self.sup_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_suppliers(self):
        rows = run_select("SELECT SupID, SupName, License_no, Email, Phone, Street, City FROM SUPPLIER")
        self.sup_tree.delete(*self.sup_tree.get_children())
        for r in rows:
            self.sup_tree.insert("", "end", values=r)

    def add_supplier_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add suppliers")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Supplier")
        labels = ["SupID","SupName","License_no","Email","Phone","Street","City"]
        entries = {}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            vals = tuple(entries[l].get().strip() or None for l in labels)
            if not vals[0] or not vals[1]:
                messagebox.showwarning("Input","SupID & SupName required"); return
            q = "INSERT INTO SUPPLIER (SupID, SupName, License_no, Email, Phone, Street, City) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            if run_query(q, vals):
                messagebox.showinfo("Added","Supplier added"); dlg.destroy(); self.load_suppliers()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def update_supplier_dialog(self):
        if not self.check_permission("edit"):
            messagebox.showwarning("Permission Denied", "You don't have permission to update suppliers")
            return
        
        sel = self.sup_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select supplier to update"); return
        vals = self.sup_tree.item(sel[0])['values']
        supid = vals[0]
        dlg = tk.Toplevel(self); dlg.title(f"Update Supplier {supid}")
        labels = ["SupName","License_no","Email","Phone","Street","City"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg)
            pre = vals[i+1] if i+1 < len(vals) else ""
            if pre is not None:
                e.insert(0, pre)
            e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            sname = entries["SupName"].get().strip()
            lic = entries["License_no"].get().strip() or None
            email = entries["Email"].get().strip() or None
            phone = entries["Phone"].get().strip() or None
            street = entries["Street"].get().strip() or None
            city = entries["City"].get().strip() or None
            q = """UPDATE SUPPLIER SET SupName=%s, License_no=%s, Email=%s, Phone=%s, Street=%s, City=%s WHERE SupID=%s"""
            if run_query(q, (sname, lic, email, phone, street, city, supid)):
                messagebox.showinfo("Updated","Supplier updated"); dlg.destroy(); self.load_suppliers()
        ttk.Button(dlg, text="Update", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_supplier_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete suppliers")
            return
        
        sel = self.sup_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select supplier to delete"); return
        supid = self.sup_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete supplier {supid}?"):
            if run_query("DELETE FROM SUPPLIER WHERE SupID=%s", (supid,)):
                messagebox.showinfo("Deleted","Supplier deleted"); self.load_suppliers()

    # ---------------- Medicine ----------------
    def create_medicine_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Medicines")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_medicines).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Medicine", command=self.add_medicine_dialog).pack(side="left", padx=4)
        if self.check_permission("edit"):
            ttk.Button(top, text="Update Selected", command=self.update_medicine_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_medicine_selected).pack(side="left", padx=4)
        
        cols = ("BatchNo","DrugName","ExpiryDate","Stock_quantity","Price","SupID","Type")
        self.med_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for c in cols:
            self.med_tree.heading(c, text=c)
            self.med_tree.column(c, width=120)
        self.med_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_medicines(self):
        rows = run_select("SELECT BatchNo, DrugName, ExpiryDate, Stock_quantity, Price, SupID, Type FROM MEDICINE")
        self.med_tree.delete(*self.med_tree.get_children())
        for r in rows:
            row = list(r)
            if row[2]:
                try:
                    row[2] = row[2].strftime("%Y-%m-%d")
                except:
                    pass
            self.med_tree.insert("", "end", values=tuple(row))

    def add_medicine_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add medicines")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Medicine")
        labels = ["BatchNo","DrugName","ExpiryDate (YYYY-MM-DD)","Stock_quantity","Price","SupID","Type"]
        entries = {}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            batch = entries["BatchNo"].get().strip(); name = entries["DrugName"].get().strip()
            exp = entries["ExpiryDate (YYYY-MM-DD)"].get().strip() or None
            try:
                stock = int(entries["Stock_quantity"].get().strip() or 0)
                price = float(entries["Price"].get().strip() or 0.0)
            except:
                messagebox.showwarning("Input", "Stock must be integer, price numeric"); return
            supid = entries["SupID"].get().strip() or None
            mtype = entries["Type"].get().strip() or None
            if not batch or not name:
                messagebox.showwarning("Input","BatchNo & DrugName required"); return
            ok = call_procedure('AddMedicine', (batch, name, exp, stock, price, supid, mtype))
            if ok:
                messagebox.showinfo("Added","Medicine added via procedure"); dlg.destroy(); self.load_medicines()
            else:
                q = "INSERT INTO MEDICINE (BatchNo, DrugName, ExpiryDate, Stock_quantity, Price, SupID, Type) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                if run_query(q, (batch, name, exp, stock, price, supid, mtype)):
                    messagebox.showinfo("Added","Medicine added"); dlg.destroy(); self.load_medicines()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def update_medicine_dialog(self):
        if not self.check_permission("edit"):
            messagebox.showwarning("Permission Denied", "You don't have permission to update medicines")
            return
        
        sel = self.med_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select medicine to update"); return
        vals = self.med_tree.item(sel[0])['values']
        batch, drug = vals[0], vals[1]
        dlg = tk.Toplevel(self); dlg.title(f"Update Medicine {drug} ({batch})")
        labels = ["ExpiryDate (YYYY-MM-DD)","Stock_quantity","Price","SupID","Type"]
        entries={}
        current = {"Expiry": vals[2], "Stock": vals[3], "Price": vals[4], "SupID": vals[5], "Type": vals[6]}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg)
            if l.startswith("Expiry") and current["Expiry"]:
                e.insert(0, current["Expiry"])
            elif l.startswith("Stock"):
                e.insert(0, current["Stock"] or "")
            elif l.startswith("Price"):
                e.insert(0, current["Price"] or "")
            elif l=="SupID":
                e.insert(0, current["SupID"] or "")
            elif l=="Type":
                e.insert(0, current["Type"] or "")
            e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            exp = entries["ExpiryDate (YYYY-MM-DD)"].get().strip() or None
            try:
                stock = int(entries["Stock_quantity"].get().strip() or 0)
                price = float(entries["Price"].get().strip() or 0.0)
            except:
                messagebox.showwarning("Input","Stock int, price numeric"); return
            supid = entries["SupID"].get().strip() or None
            mtype = entries["Type"].get().strip() or None
            q = """UPDATE MEDICINE SET ExpiryDate=%s, Stock_quantity=%s, Price=%s, SupID=%s, Type=%s
                   WHERE BatchNo=%s AND DrugName=%s"""
            if run_query(q, (exp, stock, price, supid, mtype, batch, drug)):
                messagebox.showinfo("Updated","Medicine updated"); dlg.destroy(); self.load_medicines()
        ttk.Button(dlg, text="Update", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_medicine_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete medicines")
            return
        
        sel = self.med_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select medicine to delete"); return
        vals = self.med_tree.item(sel[0])['values']
        batch, drug = vals[0], vals[1]
        if messagebox.askyesno("Confirm", f"Delete {drug} ({batch})?"):
            if run_query("DELETE FROM MEDICINE WHERE BatchNo=%s AND DrugName=%s", (batch, drug)):
                messagebox.showinfo("Deleted","Medicine deleted"); self.load_medicines()

    # ---------------- Customer ----------------
    def create_customer_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Customers")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_customers).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Customer", command=self.add_customer_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_customer_selected).pack(side="left", padx=4)
        if self.check_permission("edit"):
            ttk.Button(top, text="Update Selected", command=self.update_customer_dialog).pack(side="left", padx=4)
        
        cols = ("Cid","Cname","DOB","InsuranceID","Street","DNO","City","Phone")
        self.cust_tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.cust_tree.heading(c, text=c)
            self.cust_tree.column(c, width=120)
        self.cust_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_customers(self):
        rows = run_select("SELECT Cid, Cname, DOB, InsuranceID, Street, DNO, City, Phone FROM CUSTOMER")
        self.cust_tree.delete(*self.cust_tree.get_children())
        for r in rows:
            row=list(r)
            if row[2]:
                try:
                    row[2] = row[2].strftime("%Y-%m-%d")
                except:
                    pass
            self.cust_tree.insert("", "end", values=tuple(row))

    def add_customer_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add customers")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Customer")
        labels = ["Cid","Cname","DOB (YYYY-MM-DD)","InsuranceID","Street","DNO","City","Phone"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e=ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            vals = tuple(entries[l].get().strip() or None for l in labels)
            if not vals[0] or not vals[1]:
                messagebox.showwarning("Input","Cid & Cname required"); return
            q = """INSERT INTO CUSTOMER (Cid, Cname, DOB, InsuranceID, Street, DNO, City, Phone)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            if run_query(q, vals):
                messagebox.showinfo("Added","Customer added"); dlg.destroy(); self.load_customers()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def update_customer_dialog(self):
        if not self.check_permission("edit"):
            messagebox.showwarning("Permission Denied", "You don't have permission to update customers")
            return
        
        sel = self.cust_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select customer to update"); return
        vals = self.cust_tree.item(sel[0])['values']
        cid = vals[0]
        dlg = tk.Toplevel(self); dlg.title(f"Update Customer {cid}")
        labels = ["Cname","DOB (YYYY-MM-DD)","InsuranceID","Street","DNO","City","Phone"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg)
            pre = vals[i+1] if i+1 < len(vals) else ""
            if pre is not None:
                e.insert(0, pre)
            e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            cname = entries["Cname"].get().strip()
            dob = entries["DOB (YYYY-MM-DD)"].get().strip() or None
            ins = entries["InsuranceID"].get().strip() or None
            street = entries["Street"].get().strip() or None
            dno = entries["DNO"].get().strip() or None
            city = entries["City"].get().strip() or None
            phone = entries["Phone"].get().strip() or None
            q = """UPDATE CUSTOMER SET Cname=%s, DOB=%s, InsuranceID=%s, Street=%s, DNO=%s, City=%s, Phone=%s WHERE Cid=%s"""
            if run_query(q, (cname, dob, ins, street, dno, city, phone, cid)):
                messagebox.showinfo("Updated","Customer updated"); dlg.destroy(); self.load_customers()
        ttk.Button(dlg, text="Update", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_customer_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete customers")
            return
        
        sel = self.cust_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select customer to delete"); return
        cid = self.cust_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete customer {cid}?"):
            if run_query("DELETE FROM CUSTOMER WHERE Cid=%s", (cid,)):
                messagebox.showinfo("Deleted","Customer deleted"); self.load_customers()

    # ---------------- Order ----------------
    def create_order_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Orders")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_orders).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Order", command=self.add_order_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_order_selected).pack(side="left", padx=4)
        
        cols = ("OrderID","Cid","EmpID","OrderDate")
        self.order_tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.order_tree.heading(c, text=c)
            self.order_tree.column(c, width=120)
        self.order_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_orders(self):
        rows = run_select("SELECT OrderID, Cid, EmpID, OrderDate FROM `ORDER`")
        self.order_tree.delete(*self.order_tree.get_children())
        for r in rows:
            row = list(r)
            if row[3]:
                try:
                    row[3] = row[3].strftime("%Y-%m-%d")
                except:
                    pass
            self.order_tree.insert("", "end", values=tuple(row))

    def add_order_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add orders")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Order")
        labels = ["OrderID","Cid","EmpID","OrderDate (YYYY-MM-DD)"]
        entries = {}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l] = e
        def submit():
            oid = entries["OrderID"].get().strip()
            cid = entries["Cid"].get().strip() or None
            emp = entries["EmpID"].get().strip() or None
            od = entries["OrderDate (YYYY-MM-DD)"].get().strip() or None
            if not oid or not cid:
                messagebox.showwarning("Input","OrderID and Cid required"); return
            ok = call_procedure('CreateOrder', (oid, cid, emp, od))
            if ok:
                messagebox.showinfo("Added","Order created via procedure"); dlg.destroy(); self.load_orders()
            else:
                q = "INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate) VALUES (%s,%s,%s,%s)"
                if run_query(q, (oid, cid, emp, od)):
                    messagebox.showinfo("Added","Order added"); dlg.destroy(); self.load_orders()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_order_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete orders")
            return
        
        sel = self.order_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select order to delete"); return
        oid = self.order_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete order {oid}?"):
            if run_query("DELETE FROM `ORDER` WHERE OrderID=%s", (oid,)):
                messagebox.showinfo("Deleted","Order deleted"); self.load_orders()

    # ---------------- Ordered Drug ----------------
    def create_ordered_drug_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Ordered Drugs")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_ordered_drugs).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Ordered Drug", command=self.add_ordered_drug_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_ordered_drug_selected).pack(side="left", padx=4)
        
        cols = ("DrugName","OrderID","BatchNo","Ordered_quantity","Price")
        self.od_tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.od_tree.heading(c, text=c)
            self.od_tree.column(c, width=120)
        self.od_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_ordered_drugs(self):
        rows = run_select("SELECT DrugName, OrderID, BatchNo, Ordered_quantity, Price FROM ORDERED_DRUG")
        self.od_tree.delete(*self.od_tree.get_children())
        for r in rows:
            self.od_tree.insert("", "end", values=r)

    def add_ordered_drug_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add ordered drugs")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Ordered Drug")
        labels = ["DrugName","OrderID","BatchNo","Ordered_quantity","Price"]
        entries = {}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l] = e
        def submit():
            drug = entries["DrugName"].get().strip()
            oid = entries["OrderID"].get().strip()
            batch = entries["BatchNo"].get().strip()
            try:
                qty = int(entries["Ordered_quantity"].get().strip() or 0)
                price = float(entries["Price"].get().strip() or 0.0)
            except:
                messagebox.showwarning("Input","Quantity int, price numeric"); return
            if not drug or not oid or not batch:
                messagebox.showwarning("Input","DrugName, OrderID and BatchNo required"); return
            ok = run_query("INSERT INTO ORDERED_DRUG (DrugName, OrderID, BatchNo, Ordered_quantity, Price) VALUES (%s,%s,%s,%s,%s)",
                           (drug, oid, batch, qty, price))
            if ok:
                messagebox.showinfo("Added","Ordered drug added (triggers updated stock if ok)"); dlg.destroy(); self.load_ordered_drugs(); self.load_medicines()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_ordered_drug_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete ordered drugs")
            return
        
        sel = self.od_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select ordered drug to delete"); return
        vals = self.od_tree.item(sel[0])['values']
        drug, oid, batch = vals[0], vals[1], vals[2]
        if messagebox.askyesno("Confirm", f"Delete ordered drug {drug} in order {oid}?"):
            if run_query("DELETE FROM ORDERED_DRUG WHERE DrugName=%s AND OrderID=%s AND BatchNo=%s", (drug, oid, batch)):
                messagebox.showinfo("Deleted","Ordered drug deleted"); self.load_ordered_drugs(); self.load_medicines()

    # ---------------- Bill ----------------
    def create_bill_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Bills")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_bills).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Generate Bill (call proc)", command=self.generate_bill_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_bill_selected).pack(side="left", padx=4)
        
        cols = ("BillID","Cid","OrderID","Total_amt","Custpay","Inspay")
        self.bill_tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.bill_tree.heading(c, text=c)
            self.bill_tree.column(c, width=110)
        self.bill_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_bills(self):
        rows = run_select("SELECT BillID, Cid, OrderID, Total_amt, Custpay, Inspay FROM BILL")
        self.bill_tree.delete(*self.bill_tree.get_children())
        for r in rows:
            self.bill_tree.insert("", "end", values=r)

    def generate_bill_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to generate bills")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Generate Bill")
        labels = ["BillID (int)","Cid","OrderID"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e=ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            try:
                bid = int(entries["BillID (int)"].get().strip())
            except:
                messagebox.showwarning("Input","BillID must be integer"); return
            cid = entries["Cid"].get().strip() or None
            oid = entries["OrderID"].get().strip() or None
            if not cid or not oid:
                messagebox.showwarning("Input","Cid and OrderID required"); return
            ok = call_procedure('GenerateBill', (bid, cid, oid))
            if ok:
                messagebox.showinfo("Bill Generated","Bill generated via procedure"); dlg.destroy(); self.load_bills()
        ttk.Button(dlg, text="Generate", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_bill_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete bills")
            return
        
        sel = self.bill_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select bill to delete"); return
        bid = self.bill_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete bill {bid}?"):
            if run_query("DELETE FROM BILL WHERE BillID=%s", (bid,)):
                messagebox.showinfo("Deleted","Bill deleted"); self.load_bills()

    # ---------------- Disposal ----------------
    def create_disposal_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Disposals")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_disposals).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Disposal", command=self.add_disposal_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_disposal_selected).pack(side="left", padx=4)
        
        cols = ("BatchNo","DrugName","Dis_Qty","Company","Emp_ID","Expired","Damaged","Trial_Batch","Contaminated")
        self.disp_tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.disp_tree.heading(c, text=c)
            self.disp_tree.column(c, width=110)
        self.disp_tree.pack(fill="both", expand=True, padx=8, pady=6)

    def load_disposals(self):
        rows = run_select("SELECT BatchNo, DrugName, Dis_Qty, Company, Emp_ID, Expired, Damaged, Trial_Batch, Contaminated FROM DISPOSAL")
        self.disp_tree.delete(*self.disp_tree.get_children())
        for r in rows:
            self.disp_tree.insert("", "end", values=r)

    def add_disposal_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add disposals")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Disposal")
        labels = ["BatchNo","DrugName","Dis_Qty","Company","Emp_ID","Expired (0/1)","Damaged (0/1)","Trial_Batch (0/1)","Contaminated (0/1)"]
        entries = {}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = ttk.Entry(dlg); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        def submit():
            batch = entries["BatchNo"].get().strip()
            drug = entries["DrugName"].get().strip()
            try:
                qty = int(entries["Dis_Qty"].get().strip() or 0)
            except:
                messagebox.showwarning("Input","Dis_Qty must be integer"); return
            comp = entries["Company"].get().strip() or None
            emp = entries["Emp_ID"].get().strip() or None
            try:
                expired = bool(int(entries["Expired (0/1)"].get().strip() or 0))
                damaged = bool(int(entries["Damaged (0/1)"].get().strip() or 0))
                trial = bool(int(entries["Trial_Batch (0/1)"].get().strip() or 0))
                cont = bool(int(entries["Contaminated (0/1)"].get().strip() or 0))
            except:
                messagebox.showwarning("Input","Flags must be 0 or 1"); return
            if not batch or not drug:
                messagebox.showwarning("Input","BatchNo & DrugName required"); return
            q = """INSERT INTO DISPOSAL (BatchNo, DrugName, Dis_Qty, Company, Emp_ID, Expired, Damaged, Trial_Batch, Contaminated)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            if run_query(q, (batch, drug, qty, comp, emp, expired, damaged, trial, cont)):
                messagebox.showinfo("Added","Disposal recorded"); dlg.destroy(); self.load_disposals()
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_disposal_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete disposals")
            return
        
        sel = self.disp_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select disposal to delete"); return
        batch, drug = self.disp_tree.item(sel[0])['values'][0], self.disp_tree.item(sel[0])['values'][1]
        if messagebox.askyesno("Confirm", f"Delete disposal record {drug} ({batch})?"):
            if run_query("DELETE FROM DISPOSAL WHERE BatchNo=%s AND DrugName=%s", (batch, drug)):
                messagebox.showinfo("Deleted","Disposal deleted"); self.load_disposals()

    # ---------------- Prescription ----------------
    def create_prescription_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Prescriptions")

        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_prescriptions).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Prescription", command=self.add_prescription_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_prescription_selected).pack(side="left", padx=4)
        if self.check_permission("add"):
            ttk.Button(top, text="Add Drug to Prescription", command=self.add_prescribed_drug_dialog).pack(side="left", padx=4)

        cols = ("PresID","Cid","DocID","PresDate","OrderID")
        self.pres_tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.pres_tree.heading(c, text=c)
            self.pres_tree.column(c, width=120)
        self.pres_tree.pack(fill="both", expand=True, padx=8, pady=6)

        ttk.Label(frame, text="Drugs in Selected Prescription:").pack(pady=(10,2))
        cols2 = ("DrugID","PresID","Quantity")
        self.pd_tree = ttk.Treeview(frame, columns=cols2, show="headings", height=8)
        for c in cols2:
            self.pd_tree.heading(c, text=c)
            self.pd_tree.column(c, width=120)
        self.pd_tree.pack(fill="both", expand=True, padx=8, pady=6)

        self.pres_tree.bind("<<TreeviewSelect>>", self.load_prescribed_drugs_for_selected)
        self.load_prescriptions()

    def load_prescriptions(self):
        rows = run_select("SELECT PresID, Cid, DocID, PresDate, OrderID FROM PRESCRIPTION")
        self.pres_tree.delete(*self.pres_tree.get_children())
        for r in rows:
            row = list(r)
            if row[3]:
                try:
                    if isinstance(row[3], datetime):
                        row[3] = row[3].strftime("%Y-%m-%d")
                    elif isinstance(row[3], date):
                        row[3] = row[3].strftime("%Y-%m-%d")
                except:
                    pass
            self.pres_tree.insert("", "end", values=tuple(row))

    def load_prescribed_drugs_for_selected(self, event=None):
        sel = self.pres_tree.selection()
        if not sel:
            return
        pres_id = self.pres_tree.item(sel[0])['values'][0]
        rows = run_select("SELECT DrugID, PresID, Quantity FROM PRESCRIBED_DRUG WHERE PresID=%s", (pres_id,))
        self.pd_tree.delete(*self.pd_tree.get_children())
        for r in rows:
            self.pd_tree.insert("", "end", values=r)

    def add_prescription_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add prescriptions")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Prescription")
        dlg.geometry("500x300")
        
        cust_rows = run_select("SELECT Cid, Cname FROM CUSTOMER")
        available_customers = [f"{row[0]} - {row[1]}" for row in cust_rows]
        customer_ids = [str(row[0]) for row in cust_rows]
        
        order_rows = run_select("SELECT OrderID FROM `ORDER`")
        available_orders = [str(row[0]) for row in order_rows]
        
        ttk.Label(dlg, text="PresID").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        presid_entry = ttk.Entry(dlg)
        presid_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        
        ttk.Label(dlg, text="Customer (Cid) *required").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        cid_combo = ttk.Combobox(dlg, values=available_customers, state="readonly", width=30)
        cid_combo.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        
        ttk.Label(dlg, text="DocID (optional)").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        docid_entry = ttk.Entry(dlg)
        docid_entry.grid(row=2, column=1, padx=6, pady=4, sticky="ew")
        
        ttk.Label(dlg, text="PresDate (YYYY-MM-DD)").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        presdate_entry = ttk.Entry(dlg)
        presdate_entry.grid(row=3, column=1, padx=6, pady=4, sticky="ew")
        
        ttk.Label(dlg, text="OrderID (optional)").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        order_combo = ttk.Combobox(dlg, values=[""] + available_orders, state="normal")
        order_combo.grid(row=4, column=1, padx=6, pady=4, sticky="ew")
        
        dlg.columnconfigure(1, weight=1)
        
        def submit():
            pid = presid_entry.get().strip()
            cid_selection = cid_combo.get().strip()
            if not cid_selection:
                messagebox.showwarning("Input","Customer (Cid) is required"); return
            cid = cid_selection.split(" - ")[0]
            doc = docid_entry.get().strip() or None
            pdate = presdate_entry.get().strip() or None
            oid = order_combo.get().strip() or None
            if not pid or not cid:
                messagebox.showwarning("Input","PresID and Cid required"); return
            check_cust = run_select("SELECT 1 FROM CUSTOMER WHERE Cid=%s", (cid,))
            if not check_cust:
                messagebox.showerror("Invalid Customer", f"Customer ID '{cid}' does not exist in CUSTOMER table.\nPlease select a valid customer.")
                return
            if oid:
                check_order = run_select("SELECT 1 FROM `ORDER` WHERE OrderID=%s", (oid,))
                if not check_order:
                    messagebox.showerror("Invalid Order", f"OrderID '{oid}' does not exist in ORDER table.\nPlease select a valid OrderID or leave empty.")
                    return
            q = "INSERT INTO PRESCRIPTION (PresID, Cid, DocID, PresDate, OrderID) VALUES (%s,%s,%s,%s,%s)"
            if run_query(q,(pid,cid,doc,pdate,oid)):
                try:
                    nid = get_next_nid()
                    msg = f"New prescription {pid} for customer {cid}"
                    run_query("INSERT INTO NOTIFICATION (NID, Type, Message) VALUES (%s,%s,%s)",
                              (nid, "Prescription", msg))
                    self.append_log(f"Notification created for prescription {pid} (NID {nid})")
                except Exception as e:
                    self.append_log(f"Failed to create notification for prescription {pid}: {e}")
                messagebox.showinfo("Added","Prescription added"); dlg.destroy(); self.load_prescriptions()
                if hasattr(self, "notif_tree"):
                    self.load_notifications()
        
        ttk.Button(dlg,text="Add Prescription",command=submit).grid(row=5,column=0,columnspan=2,pady=15)

    def add_prescribed_drug_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add prescribed drugs")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Drug to Prescription")
        labels=["DrugID","PresID","Quantity"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg,text=l).grid(row=i,column=0,sticky="w",padx=6,pady=4)
            e=ttk.Entry(dlg); e.grid(row=i,column=1,padx=6,pady=4)
            entries[l]=e

        def submit():
            did = entries["DrugID"].get().strip()
            pid = entries["PresID"].get().strip()
            try:
                qty = int(entries["Quantity"].get().strip() or 0)
            except:
                messagebox.showwarning("Input","Quantity must be integer"); return
            if not did or not pid:
                messagebox.showwarning("Input","DrugID and PresID required"); return
    
            # Add this check before INSERT
            existing = run_select("SELECT 1 FROM PRESCRIBED_DRUG WHERE DrugID=%s AND PresID=%s", (did, pid))
            if existing:
                messagebox.showwarning("Duplicate Entry", f"Drug {did} is already in prescription {pid}")
                return
    
            if run_query("INSERT INTO PRESCRIBED_DRUG (DrugID, PresID, Quantity) VALUES (%s,%s,%s)",(did,pid,qty)):
                messagebox.showinfo("Added","Drug added to prescription"); dlg.destroy()
            # Force reload by simulating selection
            if self.pres_tree.selection():
                self.load_prescribed_drugs_for_selected()
            else:
                messagebox.showinfo("Reload", "Please select the prescription again to see drugs")
        ttk.Button(dlg,text="Add",command=submit).grid(row=len(labels),column=0,columnspan=2,pady=8)

    def delete_prescription_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete prescriptions")
            return
    
        sel = self.pres_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select prescription to delete"); return
        pid = self.pres_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm",f"Delete prescription {pid}?"):
            # First delete all prescribed drugs
            run_query("DELETE FROM PRESCRIBED_DRUG WHERE PresID=%s",(pid,))
            # Then delete the prescription
            run_query("DELETE FROM PRESCRIPTION WHERE PresID=%s",(pid,))
            self.load_prescriptions()
            self.pd_tree.delete(*self.pd_tree.get_children())

    # ---------------- Notifications ----------------
    def create_notifications_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Notifications")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Button(top, text="Reload", command=self.load_notifications).pack(side="left", padx=4)
        
        if self.check_permission("add"):
            ttk.Button(top, text="Add Notification", command=self.add_notification_dialog).pack(side="left", padx=4)
        if self.check_permission("delete"):
            ttk.Button(top, text="Delete Selected", command=self.delete_notification_selected).pack(side="left", padx=4)

        cols = ("NID","Type","Message")
        self.notif_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for c in cols:
            self.notif_tree.heading(c, text=c)
            self.notif_tree.column(c, width=140)
        self.notif_tree.pack(fill="both", expand=True, padx=8, pady=6)

        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", padx=8, pady=6)
        ttk.Label(bottom, text="EmpID to mark seen:").pack(side="left", padx=(0,6))
        self.mark_emp_entry = ttk.Entry(bottom, width=10)
        self.mark_emp_entry.pack(side="left")
        ttk.Button(bottom, text="Mark Selected Seen", command=self.mark_selected_notification_seen_dialog).pack(side="left", padx=6)

        self.load_notifications()

    def load_notifications(self):
        if not hasattr(self, 'notif_tree'):
            return
        rows = run_select("SELECT NID, Type, Message FROM NOTIFICATION ORDER BY NID DESC")
        self.notif_tree.delete(*self.notif_tree.get_children())
        for r in rows:
            self.notif_tree.insert("", "end", values=r)
        self.append_log(f"Loaded {len(rows)} notifications")

    def add_notification_dialog(self):
        if not self.check_permission("add"):
            messagebox.showwarning("Permission Denied", "You don't have permission to add notifications")
            return
        
        dlg = tk.Toplevel(self); dlg.title("Add Notification")
        labels = ["Type","Message"]
        entries={}
        for i,l in enumerate(labels):
            ttk.Label(dlg, text=l).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e=ttk.Entry(dlg, width=40); e.grid(row=i, column=1, padx=6, pady=4)
            entries[l]=e
        
        def submit():
            ntype = entries["Type"].get().strip() or None
            msg = entries["Message"].get().strip() or None
            if not msg:
                messagebox.showwarning("Input","Message required"); return
            nid = get_next_nid()
            q = "INSERT INTO NOTIFICATION (NID, Type, Message) VALUES (%s,%s,%s)"
            if run_query(q, (nid, ntype, msg)):
                messagebox.showinfo("Added","Notification added"); dlg.destroy(); self.load_notifications()
                self.append_log(f"Notification {nid} created")
        ttk.Button(dlg, text="Add", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_notification_selected(self):
        if not self.check_permission("delete"):
            messagebox.showwarning("Permission Denied", "You don't have permission to delete notifications")
            return
        
        sel = self.notif_tree.selection()
        if not sel:
            messagebox.showwarning("Select","Select notification to delete"); return
        nid = self.notif_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete notification {nid}?"):
            if run_query("DELETE FROM NOTIFICATION WHERE NID=%s", (nid,)):
                messagebox.showinfo("Deleted","Notification deleted"); self.load_notifications()

    def mark_selected_notification_seen_dialog(self):
        sel = self.notif_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a notification to mark as seen")
            return
        nid = self.notif_tree.item(sel[0])['values'][0]
        empid = self.mark_emp_entry.get().strip()
        if not empid:
            messagebox.showwarning("Input", "Enter EmpID to mark as seen")
            return
        existing = run_select("SELECT 1 FROM IS_NOTIFIED WHERE NID=%s AND EmpID=%s", (nid, empid))
        if existing:
            messagebox.showinfo("Already Seen", f"Notification {nid} already marked seen by {empid}")
            return
        ok = run_query("INSERT INTO IS_NOTIFIED (EmpID, NID) VALUES (%s,%s)", (empid, nid))
        if ok:
            messagebox.showinfo("Marked", f"Notification {nid} marked seen by {empid}")
            self.append_log(f"Notification {nid} seen by EmpID {empid}")

    # ---------------- Queries ----------------
    def create_queries_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Queries")
        top = ttk.Frame(frame); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Pre-built queries:").pack(side="left", padx=6)
        self.query_combo = ttk.Combobox(top, values=[
            "All medicines expiring within WARN_DAYS",
            "Join: Orders with Customer & Total",
            "Aggregate: Stock per Supplier",
            "Nested: Customers with insurance active (nested subquery)",
            "Function: TotalStockValue()",
            "Function: IsExpired(batch, name) (example B002, Amoxicillin)",
            "IS_NOTIFIED: Who has seen which notifications",  
            "Insurance: All active insurances with customer details"  
        ], state="readonly", width=50)
        self.query_combo.pack(side="left", padx=6)
        ttk.Button(top, text="Run", command=self.run_selected_query).pack(side="left", padx=6)
        ttk.Button(top, text="Run Custom SQL", command=self.run_custom_query_dialog).pack(side="left", padx=6)

        self.query_res_tree = None
        self.query_text = tk.Text(frame, height=12, state="disabled")
        self.query_text.pack(fill="both", expand=True, padx=8, pady=8)

    def run_selected_query(self):
        qname = self.query_combo.get()
        if not qname:
            messagebox.showwarning("Select", "Select a query"); return
        self.query_text.config(state="normal"); self.query_text.delete("1.0", "end")
        if qname == "All medicines expiring within WARN_DAYS":
            q = "SELECT BatchNo, DrugName, ExpiryDate, Stock_quantity FROM MEDICINE WHERE ExpiryDate <= %s"
            warn_until = (date.today() + timedelta(days=self.WARN_DAYS)).strftime("%Y-%m-%d")
            cols, rows = run_select_with_cols(q, (warn_until,))
            self._display_query_results(cols, rows)
        elif qname == "Join: Orders with Customer & Total":
            q = """SELECT o.OrderID, o.OrderDate, c.Cname,
                          IFNULL(SUM(od.Ordered_quantity * od.Price),0) AS OrderTotal
                   FROM `ORDER` o
                   LEFT JOIN CUSTOMER c ON o.Cid = c.Cid
                   LEFT JOIN ORDERED_DRUG od ON o.OrderID = od.OrderID
                   GROUP BY o.OrderID, o.OrderDate, c.Cname"""
            cols, rows = run_select_with_cols(q)
            self._display_query_results(cols, rows)
        elif qname == "Aggregate: Stock per Supplier":
            q = """SELECT s.SupID, s.SupName, IFNULL(SUM(m.Stock_quantity),0) AS TotalStock
                   FROM SUPPLIER s
                   LEFT JOIN MEDICINE m ON s.SupID = m.SupID
                   GROUP BY s.SupID, s.SupName"""
            cols, rows = run_select_with_cols(q)
            self._display_query_results(cols, rows)
        elif qname == "Nested: Customers with insurance active (nested subquery)":
            q = """SELECT Cid, Cname FROM CUSTOMER
                   WHERE InsuranceID IN (
                        SELECT InsuranceID FROM INSURANCE WHERE EndDate >= CURDATE()
                   )"""
            cols, rows = run_select_with_cols(q)
            self._display_query_results(cols, rows)
        elif qname == "Function: TotalStockValue()":
            cols, rows = run_select_with_cols("SELECT TotalStockValue() AS TotalStockValue")
            self._display_query_results(cols, rows)
        elif qname.startswith("Function: IsExpired"):
            rows = run_select("SELECT IsExpired(%s,%s) AS IsExpired", ("B002","Amoxicillin"))
            self.query_text.insert("end", "IsExpired Result (0=Not Expired, 1=Expired)\n")
            self.query_text.insert("end", "-" * 40 + "\n")
            if rows:
                result = rows[0][0]
                status = "EXPIRED" if result == 1 else "NOT EXPIRED"
                self.query_text.insert("end", f"Medicine B002-Amoxicillin: {status} (Value: {result})\n")
            else:
                self.query_text.insert("end", "No result returned\n")
        elif qname == "IS_NOTIFIED: Who has seen which notifications":
            q = """SELECT i.EmpID, e.Ename, i.NID, n.Type, n.Message
               FROM IS_NOTIFIED i
               LEFT JOIN EMPLOYEE e ON i.EmpID = e.EmpID
               LEFT JOIN NOTIFICATION n ON i.NID = n.NID
               ORDER BY i.NID DESC"""
            cols, rows = run_select_with_cols(q)
            self._display_query_results(cols, rows)
        elif qname == "Insurance: All active insurances with customer details":
            q = """SELECT i.InsuranceID, i.StartDate, i.EndDate,
                  COUNT(c.Cid) AS CustomerCount,
                  GROUP_CONCAT(c.Cname SEPARATOR ', ') AS Customers
                FROM INSURANCE i
                LEFT JOIN CUSTOMER c ON i.InsuranceID = c.InsuranceID
                GROUP BY i.InsuranceID, i.StartDate, i.EndDate
                ORDER BY i.EndDate DESC"""
            cols, rows = run_select_with_cols(q)
            self._display_query_results(cols, rows)
        else:
            self.query_text.insert("end", "Unknown query selected.")
        self.query_text.config(state="disabled")

    def run_custom_query_dialog(self):
        dlg = tk.Toplevel(self); dlg.title("Run Custom SQL (SELECT only)")
        ttk.Label(dlg, text="Enter a SELECT query:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        txt = tk.Text(dlg, height=8, width=80)
        txt.grid(row=1, column=0, padx=6, pady=6)
        def runit():
            q = txt.get("1.0", "end").strip()
            if not q.lower().startswith("select"):
                messagebox.showwarning("Only SELECT", "Only SELECT queries are allowed here."); return
            cols, rows = run_select_with_cols(q)
            self._display_query_results(cols, rows)
            dlg.destroy()
        ttk.Button(dlg, text="Run", command=runit).grid(row=2, column=0, pady=6)

    def _display_query_results(self, cols, rows):
        self.query_text.config(state="normal")
        self.query_text.delete("1.0", "end")
        if not cols:
            self.query_text.insert("end", "No columns/rows returned or error.\n")
            return
        header = " | ".join(cols)
        self.query_text.insert("end", header + "\n")
        self.query_text.insert("end", "-" * len(header) + "\n")
        for r in rows:
            row_s = " | ".join(str(item) for item in r)
            self.query_text.insert("end", row_s + "\n")
        self.query_text.config(state="disabled")

# ---------- MAIN ENTRY POINT ----------
if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()

