from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os


class GenericMethods:
    def __init__(self):
        self.amenities = [
            "Popular amenities",
            "Parking and transportation",
            "Food and drink",
            "Internet",
            "Things to do",
            "Family friendly",
            "Conveniences",
            "Guest services",
            "Outdoors",
            "Accessibility",
            "More",
            "Languages spoken",
            "Activities nearby",
            "Restaurants on site",
            "Top family-friendly amenities"
        ]
        self.hotel_policies = [
            "Check-in",
            "Check-out",
            "Special check-in instructions",
            "Access methods",
            "Pets",
            "Children and extra beds"
        ]
        self.extra_info = [
            "Optional extras",
            "You need to know",
            "We should mention",
            "Property is also known as"
        ]
        self.room_features = [
            "Bathroom",
            "Bedroom",
            "Family friendly",
            "Food and drink",
            "Internet",
            "More",
            "Outdoor space",
            "Safety",
            "Entertainment",
            "Accessibility"
        ]
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=["--incognito", "--ignore-certificate-errors", "--disable-blink-features=AutomationControlled"])
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def get_element(self, selector, attribute="text", timeout=500):
        try:
            element = self.page.locator(selector)
            if attribute == "text":
                return element.inner_text()
            elif attribute == "value":
                return element.get_attribute("value")
            elif attribute == "href":
                return element.get_attribute("href")
            elif attribute == "src":
                return element.get_attribute("src")
            else:
                return ""
        except:
            return ""

    def get_elements(self, selector, attribute="text", timeout=500):
        try:
            elements = self.page.locator(selector).all()
            if attribute == "text":
                return [element.inner_text(timeout=500) for element in elements]
            elif attribute == "value":
                return [element.get_attribute("value", timeout=500) for element in elements]
            elif attribute == "href":
                return [element.get_attribute("href", timeout=500) for element in elements]
            elif attribute == "src":
                return [element.get_attribute("src", timeout=500) for element in elements]
            else:
                return []
        except:
            return []

    def click_on_button(self, selector, timeout=500):
        try:
            button = self.page.locator(selector)
            button.wait_for(timeout=timeout)
            button.click()
        except:
            pass