import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langchain.tools import tool
import re
# name = "web_crawler_tool"
# description = "A tool to crawl a website and extract specific links related to user provided criteria"

class WebCrawlerTool:

    def __init__(self, initial_urls=[], filter_criteria=None):
        self.visited_urls = []
        self.urls_to_visit = initial_urls
        self.filter_criteria = filter_criteria
        self.recommended_url = []
      
    @tool("crawl_tool")
    def crawl_tool(self, link: list[str], filter_criteria: str) -> str:
        """Crawls the link and returns the links found."""
        self.urls_to_visit = link
        self.filter_criteria = filter_criteria
        return self.invokeCrawler()

    # Function to crawl a page and extract links
    def crawl_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f"Crawl Page :: Web Crawler :: Crawling URL: {url}")
            soup = BeautifulSoup(response.content, "html.parser")

            main_div = soup.find('div', class_='article-container')
            if main_div:
                heading = main_div.find('h3') 
                if heading:
                    heading_data = heading.text
                else:
                    heading_data = ""
                if heading_data == "Request Syntax":
                    print(f"Found heading: {heading_data}")
                    self.recommended_url.append(url)

                # Extract links and enqueue new URLs
                links = []
                for link in main_div.find_all("a", href=True):
                    next_url = urljoin(url, link["href"])      
                    print(f"Crawl Page :: Next URL  {next_url}")          
                    if "reference/services" in next_url and "vpc" in next_url:
                        if next_url not in str(links) and next_url not in self.visited_urls and next_url not in self.urls_to_visit:
                            links.append(next_url)
                        else:
                            try:
                                self.urls_to_visit.remove(next_url)  # Remove if already in the queue
                            except ValueError:
                                pass
                                
                return links
        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
            return []

    def invokeCrawler(self) -> str:
        # Crawl the website
        while self.urls_to_visit:
            current_url = self.urls_to_visit.pop(0)  # Dequeue the first URL
            print(f"Web Crawler :: Current URL: {current_url}")
            if current_url in self.visited_urls:
                continue
            new_links = self.crawl_page(url=current_url)
            self.visited_urls.append(current_url)
            self.urls_to_visit.extend(new_links)
        print(f'from Crawler urls to be loaded :: {str(self.visited_urls)}')
        for url in self.recommended_url:
            print(f"Crawler Recommended URL: {url}")
        return self.visited_urls

if __name__ == "__main__":
    link = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html"
    print("Starting web crawler...")
    WebCrawlerTool(initial_urls=[link], filter_criteria="Request Syntax").invokeCrawler()