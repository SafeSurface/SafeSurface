import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

@tool
def fetch_webpage_title(url: str) -> str:
    """
    抓取目标网页的标题与其主要表单信息。
    对于探测 Web 边界靶场非常有帮助。
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        forms = soup.find_all('form')
        return f"Title: {title} | Forms found: {len(forms)} | Status: {response.status_code}"
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"
