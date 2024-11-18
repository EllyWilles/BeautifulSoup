import requests
from bs4 import BeautifulSoup
import json

# Базовый URL сайта
base_url = "http://books.toscrape.com/"
catalogue_url = "http://books.toscrape.com/catalogue/"

def scrape_books():
    all_books = []

    page = 1
    while True:
        # Формируем URL для текущей страницы
        url = f"{catalogue_url}page-{page}.html" if page > 1 else base_url
        print(f"Скачиваем страницу: {url}")
        
        response = requests.get(url)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим все книги на странице
        books = soup.find_all('article', class_='product_pod')

        if not books:
            break

        for book in books:
            title = book.find('h3').find('a')['title']
            price = book.find('p', class_='price_color').text
            relative_book_url = book.find('h3').find('a')['href']
            
            # Преобразуем относительный URL в полный URL
            book_url = (
                f"{catalogue_url}{relative_book_url}" 
                if "catalogue" not in relative_book_url 
                else f"{base_url}{relative_book_url}"
            ).replace('../../../', '')

            price = float(price.replace('£', '').strip())

            # Переходим на страницу книги
            response = requests.get(book_url)
            response.encoding = 'utf-8'
            book_soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем количество товара
            stock_text_element = book_soup.find('p', class_='instock availability')
            stock = "в наличии"
            if stock_text_element:
                stock_text = stock_text_element.text.strip()
                if 'available' in stock_text:
                    try:
                        stock = int(stock_text.split('(')[-1].split()[0])
                    except ValueError:
                        stock = "в наличии"

            # Извлекаем описание книги
            description_tag = book_soup.find('meta', {'name': 'description'})
            description = description_tag['content'].strip() if description_tag else "Описание недоступно"

            # Добавляем книгу в список
            all_books.append({
                'title': title,
                'price': price,
                'stock': stock,
                'description': description
            })

        # Переход к следующей странице
        page += 1

    return all_books

def save_to_json(data, filename='books_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

books = scrape_books()

save_to_json(books)
print("Данные успешно сохранены в 'books_data.json'.")
