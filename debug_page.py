import requests
from bs4 import BeautifulSoup

def debug_page_structure():
    """Debug function to see the page structure"""
    url = "https://opentrackers.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("=== PAGE TITLE ===")
    print(soup.title.string if soup.title else "No title found")
    
    print("\n=== ALL CLASSES FOUND ===")
    all_classes = set()
    for tag in soup.find_all(class_=True):
        if isinstance(tag['class'], list):
            all_classes.update(tag['class'])
        else:
            all_classes.add(tag['class'])
    print(sorted(all_classes))
    
    print("\n=== ALL IDS FOUND ===")
    all_ids = set()
    for tag in soup.find_all(id=True):
        all_ids.add(tag['id'])
    print(sorted(all_ids))
    
    print("\n=== FIRST FEW PARAGRAPHS WITH SIGNUP TEXT ===")
    # Look for elements that might contain the signup text
    for i, p in enumerate(soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'article', 'section'])):
        text = p.get_text()
        if 'SIGNUP' in text.upper() and ('LIMITED' in text.upper() or 'OPEN' in text.upper()):
            print(f"Element {i+1}: {text[:200]}...")
            print("---")
    
    print("\n=== PAGINATION ELEMENTS ===")
    # Look for pagination
    pagination_selectors = ['nav', '.pagination', '.pager', '.wp-pagenavi', '.navigation']
    for selector in pagination_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"Found '{selector}' elements:")
            for elem in elements:
                print(f"  - {elem.name} with classes: {elem.get('class', [])}")
                print(f"    Content preview: {elem.get_text()[:100]}...")
                print("  ---")

if __name__ == "__main__":
    debug_page_structure()