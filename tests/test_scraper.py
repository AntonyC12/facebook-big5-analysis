
# tests/test_scraper.py
import unittest
from unittest.mock import Mock, patch
from src.scraper import FacebookScraper

class TestFacebookScraper(unittest.TestCase):
    
    def setUp(self):
        self.scraper = FacebookScraper(headless=True)
        
    def test_initialization(self):
        self.assertEqual(self.scraper.headless, True)
        self.assertIsNone(self.scraper.browser)
        self.assertIsNone(self.scraper.context)
        self.assertIsNone(self.scraper.page)
        
    @patch('src.scraper.sync_playwright')
    def test_start_browser(self, mock_playwright):
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.start.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        self.scraper.start_browser()
        
        self.assertIsNotNone(self.scraper.browser)
        self.assertIsNotNone(self.scraper.context)
        self.assertIsNotNone(self.scraper.page)
        
    def test_random_wait(self):
        # This test just ensures the method doesn't crash
        try:
            self.scraper.random_wait("short")
            self.scraper.random_wait("medium")
            self.scraper.random_wait("long")
        except Exception as e:
            self.fail(f"random_wait raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()