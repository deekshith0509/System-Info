from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.boxlayout import MDBoxLayout  # FIX: Import MDBoxLayout
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.icon_definitions import md_icons
import os
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import ThreeLineIconListItem, IconLeftWidget
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.spinner import MDSpinner

KV = '''
#:import md_icons kivymd.icon_definitions.md_icons

MDBoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: 'System Insights Pro'
        right_action_items: [["refresh", app.update_system_data],["theme-light-dark", app.toggle_theme_style],["cog", app.show_settings], ["information", app.show_app_info]]
        elevation: 4

    MDTabs:
        id: tabs
        on_tab_switch: app.on_tab_switch(*args)
        allow_stretch: True
        background_color: app.theme_cls.primary_color

<Tab>:
    MDScrollViewRefreshLayout:
        id: refresh_layout
        refresh_callback: app.refresh_callback
        root_layout: root

        MDList:
            id: container
            padding: dp(10)
            spacing: dp(5)
            adaptive_height: True

<SystemInfoItem>:
    orientation: "horizontal"
    size_hint_y: None
    adaptive_height: True
    padding: dp(8)

    IconLeftWidget:
        icon: root.icon

    MDBoxLayout:
        orientation: "vertical"
        size_hint_y: None
        adaptive_height: True
        spacing: dp(4)

        MDLabel:
            text: root.text
            font_style: "Subtitle1"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            adaptive_height: True
            halign: "left"

        MDLabel:
            text: root.secondary_text
            font_style: "Body2"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_light
            adaptive_height: True
            halign: "left"

        MDLabel:
            text: root.tertiary_text
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: app.theme_cls.disabled_hint_text_color
            adaptive_height: True
            halign: "left"



<LoadingSpinner>:
    size_hint: None, None
    size: dp(46), dp(46)
    pos_hint: {'center_x': .5, 'center_y': .5}
'''

class SystemInfoItem(MDBoxLayout):
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    icon = StringProperty()


class LoadingSpinner(MDSpinner):
    pass




import os
import subprocess
import stat
import logging
import shutil

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path

class SystemCommands:
    @classmethod
    def initialize_environment(cls):
        """
        Initialize the environment including Kivy setup and permissions
        """
        try:
            # Request Android permissions
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

            # Get app's private directory
            app_dir = app_storage_path()+"/files/app/"

            # Set up logging first
            log_dir = os.path.join(app_dir, '.kivy', 'logs')
            os.makedirs(log_dir, mode=0o755, exist_ok=True)

            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(os.path.join(log_dir, 'system_info.log')),
                    logging.StreamHandler()
                ]
            )

            # Define and create necessary directories
            directories = {
                '.kivy': ['logs', 'icon', 'cache'],
                'bin': [],
                'tmp': []
            }

            for dir_name, subdirs in directories.items():
                base_dir = os.path.join(app_dir, dir_name)
                os.makedirs(base_dir, mode=0o755, exist_ok=True)
                for subdir in subdirs:
                    subdir_path = os.path.join(base_dir, subdir)
                    os.makedirs(subdir_path, mode=0o755, exist_ok=True)

            # Copy Kivy logo files
            bundle_path = os.path.join(app_dir, '_python_bundle/site-packages/kivy/data/logo')
            icon_dir = os.path.join(app_dir, '.kivy/icon')

            if os.path.exists(bundle_path):
                os.makedirs(icon_dir, mode=0o755, exist_ok=True)
                for filename in os.listdir(bundle_path):
                    src = os.path.join(bundle_path, filename)
                    dst = os.path.join(icon_dir, filename)
                    try:
                        shutil.copy2(src, dst)
                        os.chmod(dst, 0o644)
                    except Exception as e:
                        logging.warning(f"Failed to copy icon {filename}: {str(e)}")

            # Set Kivy environment variables
            os.environ['KIVY_HOME'] = os.path.join(app_dir, '.kivy')
            os.environ['KIVY_NO_ARGS'] = '1'
            os.environ['KIVY_NO_CONSOLELOG'] = '1'

            # Set up system command environment
            cls._setup_private_environment()

            return True

        except Exception as e:
            logging.error(f"Failed to initialize environment: {str(e)}")
            return False

    @staticmethod
    def _get_binary_path(binary_name):
        """
        Ensure that the binary is executed from the app's bin directory if it exists.
        """
        try:
            app_bin_path = os.path.join(app_storage_path(), 'bin', binary_name)

            # Ensure the binary exists
            if os.path.isfile(app_bin_path):
                # Set execute permissions if necessary
                current_mode = os.stat(app_bin_path).st_mode
                new_mode = current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                os.chmod(app_bin_path, new_mode)

                # Check if it is executable
                if os.access(app_bin_path, os.X_OK):
                    return app_bin_path  # Always return the full path!

            return binary_name  # Default to system binary
        except Exception as e:
            logging.error(f"Error in _get_binary_path: {str(e)}")
            return binary_name  # Fallback to system binary if an error occurs

    @staticmethod
    def _setup_private_environment():
        """
        Set up a private environment for the app with proper error handling.
        """
        try:
            app_dir = app_storage_path()
            app_bin_dir = os.path.join(app_dir, 'bin')
            app_tmp_dir = os.path.join(app_dir, 'tmp')

            # Ensure directories exist with proper permissions
            for directory in [app_bin_dir, app_tmp_dir]:
                os.makedirs(directory, mode=0o755, exist_ok=True)

            # Set environment variables
            os.environ['PATH'] = f"{app_bin_dir}:{os.environ.get('PATH', '')}"
            os.environ['HOME'] = app_dir
            os.environ['TMPDIR'] = app_tmp_dir

        except Exception as e:
            logging.error(f"Error in _setup_private_environment: {str(e)}")

    @staticmethod
    def run_command(command, timeout=2):
        """
        Execute a system command with proper environment handling.
        """
        try:
            cmd_parts = command.split()
            if not cmd_parts:
                return "Error: Empty command"

            binary_name = cmd_parts[0]
            binary_path = SystemCommands._get_binary_path(binary_name)

            # Ensure we execute the full path to avoid using system binaries
            if binary_path != binary_name:
                cmd_parts[0] = binary_path

            logging.debug(f"Executing command: {' '.join(cmd_parts)}")

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logging.error(f"Command failed: {result.stderr}")
                return f"Error: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except FileNotFoundError:
            return f"Error: Command '{command}' not found"
        except PermissionError as e:
            logging.error(f"Permission error: {str(e)}")
            return f"Error: Permission denied - {str(e)}"
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return f"Error: {str(e)}"

    @staticmethod
    def get_getprop_info():
        """Fetch the output of the `getprop` command and format it properly."""
        try:
            binary_path = SystemCommands._get_binary_path("getprop")
            output = subprocess.check_output([binary_path]).decode("utf-8")
            properties = []
            for line in output.splitlines():
                if line.startswith('[') and ']' in line:
                    key, value = line.split(']: [', 1)
                    key = key[1:]
                    value = value[:-1]
                    properties.append({key: value})
            return properties
        except Exception as e:
            logging.error(f"Error in get_getprop_info: {str(e)}")
            return []


    @staticmethod
    def get_system_info():
        commands = {
            "OS": {
                "cmd": "getprop ro.build.version.release",
                "icon": "android",
                "parse": lambda x: f"Android {x}"
            },
            "Released with":{
                "cmd": "getprop ro.product.first_api_level",
                "icon": "android",
                "parse": lambda x: f"Android {x}"
            },
            "Device": {
                "cmd": "getprop ro.product.model",
                "icon": "cellphone",
                "parse": lambda x: x
            },
            "CPU Architecture": {
                "cmd": "uname -m",
                "icon": "chip",
                "parse": lambda x: x
            },
            "Kernel": {
                "cmd": "uname -r",
                "icon": "linux",
                "parse": lambda x: x
            },
            "Build Number": {
                "cmd": "getprop ro.build.display.id",
                "icon": "information-variant",
                "parse": lambda x: x
            },
            "Security Patch": {
                "cmd": "getprop ro.build.version.security_patch",
                "icon": "security",
                "parse": lambda x: x
            }
        }
        return SystemCommands._execute_commands(commands)

    @staticmethod
    def get_cpu_info():
        commands = {
            "CPU Info": {
                "cmd": "lscpu",
                "icon": "memory",
                "parse": lambda x: x.replace('\n', '\n\n')
            },
            "CPU Cores": {
                "cmd": "nproc",
                "icon": "cpu-64-bit" if "64" in subprocess.check_output(['uname', '-m']).decode() else "cpu-32-bit",
                "parse": lambda x: x
            },
            "CPU Governor": {
                "cmd": "cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
                "icon": "speedometer",
                "parse": lambda x: f"Governor: {x}"
            },
            "CPU Frequency": {
                "cmd": "cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq",  # Correct path to the frequency file
                "icon": "chart-line",
                "parse": lambda x: '\n'.join([f"cpu{i}: {int(freq)/1000:.0f} MHz" for i, freq in enumerate(x.split()) if freq.isdigit()])
            }

        }
        return SystemCommands._execute_commands(commands)

    @staticmethod
    def get_memory_info():
        commands = {
            "RAM Usage": {
                "cmd": "free -m",
                "icon": "memory",
                "parse": lambda x: SystemCommands._parse_memory_output(x)
            },
            "Swap Usage": {
                "cmd": "cat /proc/swaps",
                "icon": "swap-horizontal",
                "parse": lambda x: SystemCommands._parse_swap_output(x)
            },
            "Memory Details": {
                "cmd": "cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree'",
                "icon": "database",
                "parse": lambda x: x.replace(':', ': ').replace('kB', ' KB')
            }
        }
        return SystemCommands._execute_commands(commands)

    @staticmethod
    def get_disk_info():
        commands = {
            "Storage": {
                "cmd": "df -h /data /storage/emulated/0 2>/dev/null || df -h /",
                "icon": "harddisk",
                "parse": lambda x: SystemCommands._parse_disk_output(x)
            },
            "I/O Stats": {
                "cmd": "cat /proc/diskstats | grep -E 'mmcblk0|dm-|sd[a-z]' 2>/dev/null",
                "icon": "database-marker",
                "parse": lambda x: SystemCommands._parse_io_stats(x)
            },
            "Mount Points": {
                "cmd": "mount | grep -E '/storage/|/data/|/system/'",
                "icon": "folder-network",
                "parse": lambda x: x.replace('\n', '\n\n')
            }
        }
        return SystemCommands._execute_commands(commands)

    @staticmethod
    def get_network_info():
        commands = {
            "Network Interfaces": {
                "cmd": "ifconfig",
                "icon": "access-point-network",
                "parse": lambda x: x.replace('\n', '\n\n')
            },
            "WiFi Info": {
                "cmd": "ifconfig 2>/dev/null | grep -oP 'inet \K[\d.]+'",
                "icon": "wifi",
                "parse": lambda x: SystemCommands._parse_wifi_output(x)
            },
            "Mobile Data": {
                "cmd": "getprop gsm.operator.alpha && getprop gsm.network.type",
                "icon": "cellphone-wireless",
                "parse": lambda x: SystemCommands._parse_mobile_data(x)
            },
            "DNS Servers": {
                "cmd": "grep -oP '(?<=nameserver )\S+' /etc/resolv.conf",
                "icon": "dns",
                "parse": lambda x: f"Primary DNS: {x.split()[0]}\nSecondary DNS: {x.split()[1] if len(x.split()) > 1 else 'N/A'}"
            }
        }
        return SystemCommands._execute_commands(commands)

    @staticmethod
    def get_processes_info():
        commands = {
            "Process Stats": {
                "cmd": "ps -A | head -n 20",
                "icon": "order-numeric-ascending",
                "parse": lambda x: x.replace('\n', '\n\n')
            },
            "Top Processes": {
                "cmd": "top -b -n 1 | head -n 15",
                "icon": "chart-bar",
                "parse": lambda x: x.replace('\n', '\n\n')
            },
            "System Load": {
                "cmd": "cat /proc/loadavg",
                "icon": "chart-line-variant",
                "parse": lambda x: f"Load Average (1/5/15 min):\n{x}"
            }
        }
        return SystemCommands._execute_commands(commands)

    @staticmethod
    def _execute_commands(commands):
        results = []
        for label, cmd_info in commands.items():
            value = SystemCommands.run_command(cmd_info["cmd"])
            parsed_value = cmd_info["parse"](value) if value else "N/A"
            results.append({
                "title": label,
                "content": parsed_value,
                "icon": cmd_info["icon"]
            })
        return results

    @staticmethod
    def _parse_memory_output(output):
        lines = output.split('\n')
        if len(lines) < 2:
            return "Memory information unavailable"

        headers = lines[0].split()
        values = lines[1].split()

        total = int(values[1]) if len(values) > 1 else 0
        used = int(values[2]) if len(values) > 2 else 0
        free = int(values[3]) if len(values) > 3 else 0

        return (f"Total: {total:,} MB\n"
                f"Used: {used:,} MB ({used/total*100:.1f}%)\n"
                f"Free: {free:,} MB ({free/total*100:.1f}%)")

    @staticmethod
    def _parse_swap_output(output):
        if not output or "Filename" not in output:
            return "No swap configured"

        lines = output.split('\n')[1:]
        total_swap = 0
        used_swap = 0

        for line in lines:
            if line:
                parts = line.split()
                if len(parts) >= 3:
                    total_swap += int(parts[2])
                    used_swap += int(parts[3]) if len(parts) > 3 else 0

        return (f"Total Swap: {total_swap/1024:.1f} MB\n"
                f"Used Swap: {used_swap/1024:.1f} MB\n"
                f"Free Swap: {(total_swap-used_swap)/1024:.1f} MB")

    @staticmethod
    def _parse_disk_output(output):
        result = []
        lines = output.split('\n')

        for line in lines[1:]:  # Skip header
            if line:
                parts = line.split()
                if len(parts) >= 6:
                    filesystem = parts[0]
                    size = parts[1]
                    used = parts[2]
                    avail = parts[3]
                    use_percent = parts[4]
                    mount = parts[5]

                    result.append(f"Mount: {mount}\n"
                                f"Size: {size}\n"
                                f"Used: {used} ({use_percent})\n"
                                f"Available: {avail}\n")

        return '\n'.join(result) if result else "No storage information available"

    @staticmethod
    def _parse_io_stats(output):
        if not output:
            return "No I/O statistics available"

        result = []
        for line in output.split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 14:
                    device = parts[2]
                    reads = int(parts[3])
                    writes = int(parts[7])
                    result.append(f"Device: {device}\n"
                                f"Reads: {reads:,}\n"
                                f"Writes: {writes:,}\n")

        return '\n'.join(result)

    @staticmethod
    def _parse_wifi_output(output):
        if not output:
            return "WiFi information unavailable"

        lines = output.split('\n')
        interface = lines[0] if lines else "unknown"

        status = "Disconnected"
        ip_addr = "N/A"

        for line in lines:
            if "inet " in line:
                ip_addr = line.split()[1].split('/')[0]
                status = "Connected"
                break

        return (f"Interface: {interface}\n"
                f"Status: {status}\n"
                f"IP Address: {ip_addr}")

    @staticmethod
    def _parse_mobile_data(output):
        lines = output.split('\n')
        operator = lines[0] if lines else "Unknown"
        network_type = lines[1] if len(lines) > 1 else "Unknown"

        return (f"Operator: {operator}\n"
                f"Network Type: {network_type}")

class Tab(MDFloatLayout, MDTabsBase):
    pass

class SystemInfoApp(MDApp):
    update_interval = 60  # seconds
    _update_thread = None
    _stop_thread = False


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_commands = SystemCommands()
        self._update_thread = None
        self._stop_thread = False
        self.current_tab = None
        self.monitor_active = False

    def build(self):
        SystemCommands.initialize_environment()
        self.make_binaries_executable()
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)
    def make_binaries_executable(self):
        bin_path="bin"
        # Command to make all binaries in the bin directory executable
        chmod_command = f"chmod +x {bin_path}/*"

        try:
            # Invoke the command directly using subprocess
            subprocess.run(chmod_command, shell=True, check=True)
            print("Binaries in 'bin' directory are now executable.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to set binaries to executable: {e}")
    def on_start(self):
        tabs_data = [
            {"title": "System", "icon": "cellphone"},
            {"title": "CPU", "icon": "memory"},
            {"title": "Memory", "icon": "database"},
            {"title": "Disk", "icon": "harddisk"},
            {"title": "Network", "icon": "access-point-network"},
            {"title": "Processes", "icon": "format-list-bulleted"},
            {"title": "GetProp", "icon": "database"}  # New tab
        ]

        for tab_data in tabs_data:
            tab = Tab(title=f"[size=20]{md_icons[tab_data['icon']]}[/size] {tab_data['title']}")
            self.root.ids.tabs.add_widget(tab)

        self.start_monitoring()
        self.update_system_data()
    def on_stop(self):
        self.stop_monitoring()

    def start_monitoring(self):
        """Start the background monitoring thread"""
        if not self._update_thread:
            self._stop_thread = False
            self._update_thread = threading.Thread(target=self._monitor_system)
            self._update_thread.daemon = True
            self._update_thread.start()
            self.monitor_active = True

    def stop_monitoring(self):
        """Stop the background monitoring thread"""
        self._stop_thread = True
        if self._update_thread:
            self._update_thread.join()
            self._update_thread = None
        self.monitor_active = False

    def _monitor_system(self):
        """Background thread for system monitoring"""
        while not self._stop_thread:
            if self.monitor_active:
                Clock.schedule_once(lambda dt: self.update_system_data())
            time.sleep(self.update_interval)

    def toggle_theme_style(self, *args):
        """Toggle between light and dark theme"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        self.update_system_data()  # Refresh to apply new theme


    def show_settings(self, *args):
        """Show settings dialog"""

        dialog_content = MDBoxLayout(  # FIX: Use MDBoxLayout instead of BoxLayout
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )

        # Auto-refresh toggle
        refresh_row = MDBoxLayout(adaptive_height=True)  # FIX: Change to MDBoxLayout
        refresh_row.add_widget(
            OneLineIconListItem(text="Auto-refresh")  # Removed 'icon' because OneLineIconListItem needs a LeftIcon
        )
        refresh_switch = MDSwitch(
            active=self.monitor_active,
            on_active=lambda *x: self.toggle_monitoring()
        )
        refresh_row.add_widget(refresh_switch)
        dialog_content.add_widget(refresh_row)

        dialog = MDDialog(
            title="Settings",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda *x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def toggle_monitoring(self):
        """Toggle auto-refresh monitoring"""
        if self.monitor_active:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def show_app_info(self, *args):
        """Show application information dialog"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="System Insights Pro",
            text=(
                "Version 3.0\n\n"
                "Advanced System Monitoring for ARM64 Android\n\n"
                "Features:\n"
                "• Real-time system monitoring\n"
                "• Detailed hardware information\n"
                "• Resource usage tracking\n"
                "• Network statistics\n"
                "• Process management\n\n"
                "Optimized for ARM64 Android Systems"
            ),
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda *x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def refresh_callback(self, *args):
        """Handle pull-to-refresh callback"""
        def refresh_callback(interval):
            self.update_system_data()
            self.root.ids.tabs.get_current_tab().ids.refresh_layout.refresh_done()

        Clock.schedule_once(refresh_callback, 1)

    def update_system_data(self, *args):
        """Update the current tab's data"""
        current_tab = self.root.ids.tabs.get_current_tab()
        if current_tab:
            self.on_tab_switch(None, current_tab, None, current_tab.title)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Handle tab switching and update data"""
        if not hasattr(instance_tab, "ids") or "container" not in instance_tab.ids:
            return

        # Clear existing widgets
        instance_tab.ids.container.clear_widgets()

        # Show loading spinner
        spinner = LoadingSpinner(active=True)
        instance_tab.ids.container.add_widget(spinner)

        # Get tab name from text (remove icon)
        tab_name = tab_text.split(" ")[-1].lower()

        # Schedule data update
        Clock.schedule_once(lambda dt: self._update_tab_data(instance_tab, tab_name, spinner))

    def _update_tab_data(self, tab, tab_name, spinner):
        """Update tab data in background"""
        method_name = f"get_{tab_name}_info"

        try:
            if hasattr(SystemCommands, method_name):
                data = getattr(SystemCommands, method_name)()

                # Remove spinner
                tab.ids.container.remove_widget(spinner)

                # Add new data
                for item_data in data:
                    icon_widget = IconLeftWidget(
                        icon=item_data["icon"],
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color
                    )

                    item = SystemInfoItem(
                        text=item_data["title"],
                        secondary_text=item_data["content"].split('\n')[0] if item_data["content"] else "N/A",
                        tertiary_text='\n'.join(item_data["content"].split('\n')[1:]) if item_data["content"] and '\n' in item_data["content"] else ""
                    )
                    item.add_widget(icon_widget)
                    tab.ids.container.add_widget(item)

        except Exception as e:
            # Remove spinner and show error
            tab.ids.container.remove_widget(spinner)
            error_item = SystemInfoItem(
                text="Error",
                secondary_text=str(e),
                tertiary_text="Please try again"
            )
            tab.ids.container.add_widget(error_item)

if __name__ == '__main__':
    SystemInfoApp().run()
