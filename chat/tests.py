from django.test import TestCase
from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By, Keys
from selenium.webdriver.support.wait import WebDriverWait

class ChatTests(ChannelsLiveServerTestCase):
    serve_static = True  # emulate StaticLiveServerTestCase

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_same_room_message(self):
        self._enter_chat_room("room_1")
        self._open_new_window()
        self._enter_chat_room("room_1")

        self._switch_to_window(0)
        self._post_message("hello")
        WebDriverWait(self.driver, 2).until(
            lambda _: "hello" in self._chat_log_value
        )

        self._switch_to_window(1)
        WebDriverWait(self.driver, 2).until(
            lambda _: "hello" in self._chat_log_value
        )

    def test_isolated_rooms(self):
        self._enter_chat_room("room_1")
        self._open_new_window()
        self._enter_chat_room("room_2")

        self._switch_to_window(0); self._post_message("hello")
        WebDriverWait(self.driver, 2).until(
            lambda _: "hello" in self._chat_log_value
        )

        self._switch_to_window(1); self._post_message("world")
        WebDriverWait(self.driver, 2).until(
            lambda _: "world" in self._chat_log_value
        )

        self.assertNotIn("hello", self._chat_log_value)
