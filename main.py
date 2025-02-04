import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, Menu
import json5
import paramiko
from tkinter import ttk
import threading
import os

def get_sftp_client(hostname, port, username, password):
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)
    return paramiko.SFTPClient.from_transport(transport)

def read_remote_file(sftp, remote_path):
    with sftp.file(remote_path, "r") as file:
        return json5.loads(file.read().decode())

def write_remote_file(sftp, remote_path, config):
    with sftp.file(remote_path, "w") as file:
        json5.dump(config, file, indent=2)

def update_modifier(modifier_index, config, modifiers, mods):
    modifier = modifiers[modifier_index]
    new_amount = simpledialog.askfloat("Input", f"Enter the new amount for {modifier['type']}:", initialvalue=modifier["amount"])
    if new_amount is not None:
        modifier["amount"] = new_amount
        threading.Thread(target=write_remote_file, args=(sftp, file_path, config)).start()
        messagebox.showinfo("Success", "Modifier updated successfully.")
    show_items_by_mod(current_category, mods[current_category], mods)

def show_items_by_mod(mod_id, items, mods):
    global current_category
    current_category = mod_id
    clear_frame()
    ttk.Button(root, text="Back", command=show_main_screen, style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    add_dropdown_menu()
    for i, item in enumerate(items):
        item_name = item.split(":")[1] if ":" in item else item
        ttk.Button(root, text=item_name, command=lambda i=item: on_edit_item(i, mods, file_path, sftp), style="Rounded.TButton").grid(row=i % 20 + 1, column=i // 20, padx=40, pady=10, sticky="ew")

def on_edit_item(item_key, mods, file_path, sftp):
    global current_category, modifiers
    config = read_remote_file(sftp, file_path)
    item = config.get("default_components", {}).get(item_key, {})
    modifiers = item.get("minecraft:attribute_modifiers", {}).get("modifiers", [])
    clear_frame()
    ttk.Button(root, text="Back", command=lambda: show_items_by_mod(current_category, mods[current_category], mods), style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    add_dropdown_menu()
    if modifiers:
        for i, modifier in enumerate(modifiers):
            label = f"{modifier['type']}: {modifier['amount']}"
            ttk.Button(root, text=label, command=lambda idx=i: update_modifier(idx, config, modifiers, mods), style="Rounded.TButton").grid(row=i + 1, column=0, padx=10, pady=5, sticky="ew")
    else:
        tk.Label(root, text="No modifiers found for this item").pack()


def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

def show_main_screen():
    clear_frame()
    config = read_remote_file(sftp, file_path)
    items = list(config.get("default_components", {}).keys())
    mods = {}
    for item in items:
        mod_id = item.split(":")[0]
        if mod_id not in mods:
            mods[mod_id] = []
        mods[mod_id].append(item)
    tk.Label(root, text="", height=4, bg=appearance_settings["background"]).grid(row=0, column=0, columnspan=4)
    for i, mod_id in enumerate(mods.keys()):
        ttk.Button(root, text=mod_id, command=lambda m=mod_id: show_items_by_mod(m, mods[m], mods), style="Rounded.TButton").grid(row=i % 20 + 1, column=i // 20, padx=5, pady=2, sticky="ew")
    add_dropdown_menu()
    ttk.Button(root, text="Add Item", command=lambda: add_item(mods), style="Rounded.TButton").grid(row=(len(mods) % 20) + 1, column=(len(mods) // 20), padx=5, pady=2, sticky="ew")

def add_item(mods):
    def save_new_item():
        mod_id = mod_id_entry.get()
        item_name = item_name_entry.get()
        if mod_id and item_name:
            item_key = f"{mod_id}:{item_name}"
            config = read_remote_file(sftp, file_path)
            if "default_components" not in config:
                config["default_components"] = {}
            config["default_components"][item_key] = {"minecraft:attribute_modifiers": {"modifiers": []}}
            threading.Thread(target=write_remote_file, args=(sftp, file_path, config)).start()
            if mod_id not in mods:
                mods[mod_id] = []
            mods[mod_id].append(item_key)
            show_items_by_mod(mod_id, mods[mod_id], mods)
            messagebox.showinfo("Success", "Item added successfully.")
        else:
            messagebox.showerror("Error", "All fields must be filled out.")

    clear_frame()
    ttk.Button(root, text="Back", command=show_main_screen, style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    tk.Label(root, text="Add New Item", font=("Arial", 16)).grid(row=1, column=0, columnspan=2, pady=20)
    tk.Label(root, text="Mod ID:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    mod_id_entry = tk.Entry(root)
    mod_id_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(root, text="Item Name:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    item_name_entry = tk.Entry(root)
    item_name_entry.grid(row=3, column=1, padx=10, pady=5)
    ttk.Button(root, text="Save", command=save_new_item, style="Rounded.TButton").grid(row=4, column=0, columnspan=2, pady=20)
    add_dropdown_menu()

def add_modifier(config, item_key, modifiers):
    def save_new_modifier():
        modifier_type = modifier_type_entry.get()
        modifier_amount = modifier_amount_entry.get()
        if modifier_type and modifier_amount:
            new_modifier = {"type": modifier_type, "amount": float(modifier_amount)}
            modifiers.append(new_modifier)
            threading.Thread(target=write_remote_file, args=(sftp, file_path, config)).start()
            messagebox.showinfo("Success", "Modifier added successfully.")
            show_items_by_mod(current_category, mods[current_category], mods)
        else:
            messagebox.showerror("Error", "All fields must be filled out.")

    clear_frame()
    ttk.Button(root, text="Back", command=lambda: on_edit_item(item_key, mods, file_path, sftp), style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    tk.Label(root, text="Add New Modifier", font=("Arial", 16)).grid(row=1, column=0, columnspan=2, pady=20)
    tk.Label(root, text="Modifier Type:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    modifier_type_entry = tk.Entry(root)
    modifier_type_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(root, text="Modifier Amount:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    modifier_amount_entry = tk.Entry(root)
    modifier_amount_entry.grid(row=3, column=1, padx=10, pady=5)
    ttk.Button(root, text="Save", command=save_new_modifier, style="Rounded.TButton").grid(row=4, column=0, columnspan=2, pady=20)
    add_dropdown_menu()

def show_settings_screen():
    clear_frame()
    ttk.Button(root, text="Back", command=show_main_screen, style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    ttk.Button(root, text="Update SFTP Credentials", command=update_credentials, style="Rounded.TButton").grid(row=2, column=0, pady=10, padx=30)
    ttk.Button(root, text="Update Appearance", command=update_appearance, style="Rounded.TButton").grid(row=3, column=0, pady=10, padx=30)
    ttk.Button(root, text="Update File Path", command=update_path, style="Rounded.TButton").grid(row=4, column=0, pady=10, padx=30)
    add_dropdown_menu()
def update_path():
    def save_new_path():
        file_path = file_path_entry.get()
        if file_path:
            save_path(file_path)
            messagebox.showinfo("Success", "Path updated successfully.")
        else:
            messagebox.showerror("Error", "All fields must be filled out.")
    clear_frame()
    ttk.Button(root, text="Back", command=show_settings_screen, style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    tk.Label(root, text="Update File Path", font=("Arial", 16)).grid(row=1, column=0, pady=20)
    tk.Label(root, text="File Path:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    file_path_entry = tk.Entry(root)
    file_path_entry.insert(0, file_path)
    file_path_entry.grid(row=2, column=1, padx=10, pady=5)
    ttk.Button(root, text="Save", command=save_new_path, style="Rounded.TButton").grid(row=3, column=0, pady=10, padx=10, sticky="e")
    add_dropdown_menu()
    def save_path(path):
        global sftp, file_path
        file_path = path
        if sftp:
            sftp.close()
        cached_credentials = load_credentials()
        if cached_credentials:
            sftp = get_sftp_client(cached_credentials["hostname"], int(cached_credentials["port"]), cached_credentials["username"], cached_credentials["password"])
        
        
        
def update_credentials():
    clear_frame()
    ttk.Button(root, text="Back", command=show_settings_screen, style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    tk.Label(root, text="Update SFTP Credentials", font=("Arial", 16)).grid(row=1, column=0, pady=20)
    tk.Label(root, text="Hostname:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    hostname_entry = tk.Entry(root)
    hostname_entry.insert(0, cached_credentials["hostname"])
    hostname_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(root, text="Port:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    port_entry = tk.Entry(root)
    port_entry.insert(0, cached_credentials["port"])
    port_entry.grid(row=3, column=1, padx=10, pady=5)
    tk.Label(root, text="Username:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    username_entry = tk.Entry(root)
    username_entry.insert(0, cached_credentials["username"])
    username_entry.grid(row=4, column=1, padx=10, pady=5)
    tk.Label(root, text="Password:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.insert(0, cached_credentials["password"])
    password_entry.grid(row=5, column=1, padx=10, pady=5)
    def save_new_credentials():
        hostname = hostname_entry.get()
        port = port_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        if hostname and port and username and password:
            save_credentials(hostname, port, username, password)
            messagebox.showinfo("Success", "Credentials updated successfully.")
        else:
            messagebox.showerror("Error", "All fields must be filled out.")
    ttk.Button(root, text="Save", command=save_new_credentials, style="Rounded.TButton").grid(row=6, column=0, pady=10, padx=10, sticky="e")
    add_dropdown_menu()

def update_appearance():
    def choose_color(setting):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            appearance_settings[setting] = color_code
            save_appearance_settings()
            apply_appearance_settings()
    def choose_font_size():
        font_size = simpledialog.askinteger("Input", "Enter the new font size:", initialvalue=appearance_settings["font"]["size"])
        if font_size:
            appearance_settings["font"]["size"] = font_size
            save_appearance_settings()
            apply_appearance_settings()
    clear_frame()
    ttk.Button(root, text="Back", command=show_settings_screen, style="Rounded.TButton").grid(row=0, column=0, sticky="nw", padx=10, pady=10)
    tk.Label(root, text="Update Appearance", font=("Arial", 16)).grid(row=1, column=0, pady=20)
    tk.Label(root, text="Background Color:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    ttk.Button(root, text="Choose Color", command=lambda: choose_color("background"), style="Rounded.TButton").grid(row=2, column=1, padx=10, pady=5)
    tk.Label(root, text="Foreground Color:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    ttk.Button(root, text="Choose Color", command=lambda: choose_color("foreground"), style="Rounded.TButton").grid(row=3, column=1, padx=10, pady=5)
    tk.Label(root, text="Font Color:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    ttk.Button(root, text="Choose Color", command=lambda: choose_color("font_color"), style="Rounded.TButton").grid(row=4, column=1, padx=10, pady=5)
    tk.Label(root, text="Font Size:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    ttk.Button(root, text="Choose Font Size", command=choose_font_size, style="Rounded.TButton").grid(row=5, column=1, padx=10, pady=5)
    add_dropdown_menu()

def save_appearance_settings():
    with open(".settings", "w") as file:
        json5.dump(appearance_settings, file)
    apply_appearance_settings()

def load_appearance_settings():
    if os.path.exists(".settings"):
        with open(".settings", "r") as file:
            settings = json5.load(file)
            if "font_color" not in settings:
                settings["font_color"] = "#ffffff"
            return settings
    return {"background": "#2e2e2e", "foreground": "#ffffff", "font": {"size": 10}, "font_color": "#ffffff"}

def apply_appearance_settings():
    root.tk_setPalette(background=appearance_settings["background"], foreground=appearance_settings["foreground"], activeBackground="#3e3e3e", activeForeground="#ffffff")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", background="#3e3e3e", foreground=appearance_settings["font_color"], borderwidth=0, relief="flat")
    style.configure("Rounded.TButton", background="#3e3e3e", foreground=appearance_settings["font_color"], borderwidth=0, relief="flat")
    style.map("Rounded.TButton", background=[("active", "#5e5e5e")], relief=[("pressed", "flat"), ("!pressed", "flat")])
    style.layout("Rounded.TButton", [("Button.button", {"children": [("Button.focus", {"children": [("Button.padding", {"children": [("Button.label", {"sticky": "nsew"})], "sticky": "nsew"})], "sticky": "nswe"})], "sticky": "nswe"})])
    style.configure("TLabel", background=appearance_settings["background"], foreground=appearance_settings["font_color"])
    style.configure("TFrame", background=appearance_settings["background"])
    style.configure("TScrollbar", background="#3e3e3e")
    root.option_add("*Font", ("Arial", appearance_settings["font"]["size"]))

def save_and_quit():
    if sftp:
        config = read_remote_file(sftp, file_path)
        progress_popup = tk.Toplevel(root)
        progress_popup.title("Saving")
        progress_popup.geometry("300x100")
        root_x, root_y, root_width, root_height = root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()
        popup_x, popup_y = root_x + (root_width // 2) - 150, root_y + (root_height // 2) - 50
        progress_popup.geometry(f"+{popup_x}+{popup_y}")
        tk.Label(progress_popup, text="Saving remote file...").grid(row=0, column=0, pady=10)
        progress_bar = ttk.Progressbar(progress_popup, mode='indeterminate')
        progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        progress_bar.start()
        def save_and_close():
            write_remote_file(sftp, file_path, config)
            progress_bar.stop()
            progress_popup.destroy()
            root.quit()
        threading.Thread(target=save_and_close).start()
    else:
        root.quit()

def minimize_window():
    root.iconify()

def maximize_window():
    root.state("zoomed" if root.state() == "normal" else "normal")

def add_dropdown_menu():
    menu_button = ttk.Menubutton(root, text="Menu", style="Rounded.TButton")
    menu = Menu(menu_button, tearoff=0)
    menu.add_command(label="Settings", command=show_settings_screen)
    menu.add_command(label="Minimize", command=minimize_window)
    menu.add_command(label="Maximize", command=maximize_window)
    menu.add_command(label="Exit", command=save_and_quit)
    menu_button["menu"] = menu
    menu_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

def create_gui():
    root.bind("<Configure>", lambda e: root.update_idletasks())
    def move_window(event):
        x, y = root.winfo_pointerx() - root._offset_x, root.winfo_pointery() - root._offset_y
        root.geometry(f"+{x}+{y}")
    def click_window(event):
        root._offset_x, root._offset_y = event.x, event.y
    root.bind("<Button-1>", click_window)
    root.bind("<B1-Motion>", move_window)
    root.update_idletasks()
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    window_width, window_height = root.winfo_width(), root.winfo_height()
    position_top, position_right = int(screen_height / 2 - window_height / 2), int(screen_width / 2 - window_width / 2)
    root.geometry(f"+{position_right}+{position_top}")
    apply_appearance_settings()
    root.configure(bg=appearance_settings["background"])

def prompt_for_credentials():
    def get_remote_details():
        return {
            "hostname": hostname_entry.get(),
            "port": int(port_entry.get()),
            "username": username_entry.get(),
            "password": password_entry.get(),
            "file_path": file_path_entry.get()
        }
    def save_and_connect():
        details = get_remote_details()
        global sftp, file_path
        sftp = get_sftp_client(details["hostname"], details["port"], details["username"], details["password"])
        save_credentials(details["hostname"], details["port"], details["username"], details["password"])
        file_path = details["file_path"]
        root.quit()
    clear_frame()
    tk.Label(root, text="Remote Connection Details", font=("Arial", 16), bg=appearance_settings["background"], fg=appearance_settings["font_color"]).grid(row=0, column=0, columnspan=2, pady=20)
    tk.Label(root, text="Hostname:", bg=appearance_settings["background"], fg=appearance_settings["font_color"]).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    hostname_entry = tk.Entry(root)
    hostname_entry.grid(row=1, column=1, padx=10, pady=5)
    tk.Label(root, text="Port:", bg=appearance_settings["background"], fg=appearance_settings["font_color"]).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    port_entry = tk.Entry(root)
    port_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(root, text="Username:", bg=appearance_settings["background"], fg=appearance_settings["font_color"]).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=3, column=1, padx=10, pady=5)
    tk.Label(root, text="Password:", bg=appearance_settings["background"], fg=appearance_settings["font_color"]).grid(row=4, column=0, sticky="w", padx=10, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=4, column=1, padx=10, pady=5)
    tk.Label(root, text="Remote File Path:", bg=appearance_settings["background"], fg=appearance_settings["font_color"]).grid(row=5, column=0, sticky="w", padx=10, pady=5)
    file_path_entry = tk.Entry(root)
    file_path_entry.insert(0, "config/wowid/items.json5")
    file_path_entry.grid(row=5, column=1, padx=10, pady=5)
    ttk.Button(root, text="Connect", command=save_and_connect, style="Rounded.TButton").grid(row=6, column=0, columnspan=2, pady=20)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.overrideredirect(False)
    root.title("Frostdev Item Modifier Widget")
    root.iconbitmap("frost3.ico")
    root.wm_title("Frostdev Item Modifier Widget")
    root.wm_iconbitmap("frost3.ico")
    appearance_settings = load_appearance_settings()
    def save_credentials(hostname, port, username, password):
        with open(".credentials_cache", "w") as file:
            json5.dump({"hostname": hostname, "port": port, "username": username, "password": password}, file)
    def load_credentials():
        if os.path.exists(".credentials_cache"):
            with open(".credentials_cache", "r") as file:
                return json5.load(file)
        return None
    cached_credentials = load_credentials()
    sftp = None
    create_gui()
    add_dropdown_menu()
    if cached_credentials:
        sftp = get_sftp_client(cached_credentials["hostname"], int(cached_credentials["port"]), cached_credentials["username"], cached_credentials["password"])
        file_path = "config/wowid/items.json5"
    else:
        prompt_for_credentials()
    show_main_screen()
    root.mainloop()
