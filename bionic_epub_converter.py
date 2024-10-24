import zipfile
import os
import shutil
from bs4 import BeautifulSoup, NavigableString
import html

def return_num_of_bolded_letters(word):
    length = len(word)
    if word.endswith('...'):
        length -= 3
    elif word.endswith('.') or word.endswith(','):
        length -= 1
    if length == 0:
        return 0
    if length == 1:
        return 1
    return length // 2 + (length % 2)

def bionic_word(word):
    if '<b>' in word:
        return word
    bold = return_num_of_bolded_letters(word)
    return '<b>' + word[:bold] + '</b>' + word[bold:]

def create_bionic_text(soup):
    def process_content(content):
        if isinstance(content, NavigableString):
            words = content.split(' ')
            bionic_words = [bionic_word(word) for word in words]
            return " ".join(bionic_words)
        elif hasattr(content, 'contents'):
            new_contents = [process_content(child) for child in content.contents]
            content.clear()
            content.extend(new_contents)
            return content
        else:
            return content

    for para in soup.find_all("p"):
        new_contents = []
        for content in para.contents:
            if content.name == 'span':
                span_soup = BeautifulSoup(str(content), 'html.parser')
                span_content = process_content(span_soup)
                new_contents.append(span_content)
            else:
                new_contents.append(process_content(content))
        para.clear()
        para.extend(new_contents)
    return soup

def process_XHTML_files(oebps_path):
    for root, dirs, files in os.walk(oebps_path):
        for file in files:
            if file.endswith('.xhtml') or file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                bionic_content = create_bionic_text(soup)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html.unescape(str(bionic_content)))

def clean_up(zip_file_name):
    shutil.rmtree('extracted_epub')
    os.remove(zip_file_name)


def process_epub(file_name):
    zip_file_name = file_name.replace('.epub', '.zip')
    shutil.copy(file_name, zip_file_name)

    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall('extracted_epub')

    extracted_epub_path = 'extracted_epub'
    process_XHTML_files(extracted_epub_path)

    new_epub_file_name = file_name.replace('.epub', '_bionic.epub')
    shutil.make_archive(new_epub_file_name.replace('.epub', ''), 'zip', 'extracted_epub')
    os.rename(new_epub_file_name.replace('.epub', '.zip'), new_epub_file_name)

    clean_up(zip_file_name)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        process_epub(file_name)
    else:
        file_name = input("Drag and drop your file into the terminal: ").strip("& '\"")
    process_epub(file_name)
    print("Your bionic book is ready!")
    input("Have a nice read! Press Enter to exit...")
