import ebooklib
import html
from ebooklib import epub
from bs4 import BeautifulSoup, NavigableString

def return_num_of_bolded_letters(word):
	length = len(word)
	if word.endswith('.'):
		length -= 1
	elif word.endswith(','):
		length -= 1
	else:
		length = length
	if length == 0:
		return 0
	if length == 1:
		return 1
	else:
		if length % 2 == 0:
			return length // 2
		else:
			return length // 2 + 1

def chapter_to_soup(chapter):
	return BeautifulSoup(chapter.get_content(), "html.parser")

def bionic_word(word):
	# Leaves bold words alone
	if '<b>' in word:
		return word
	bold = return_num_of_bolded_letters(word)
	return '<b>' + word[:bold] + '</b>' + word[bold:]

def create_bionic_text(soup):
	for para in soup.find_all("p"):
		new_contents = []
		for content in para.contents:
			if isinstance(content, NavigableString):
				words = content.split(' ')
				bionic_words = [bionic_word(word) for word in words]
				new_contents.append(" ".join(bionic_words))
			else:
				new_contents.append(str(content))
		para.clear()
		para.append("".join(new_contents))
	return str(soup)

def create_bionic_book(file_name):
	book = epub.read_epub(file_name)
	items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
	for item in items:
		soup = chapter_to_soup(item)
		content = create_bionic_text(soup)
		unescaped_content = html.unescape(content)
		item.set_content(unescaped_content.encode())
	epub.write_epub(file_name[:-5] + '_bionic.epub', book, {})

# Error handling (comment out if not needed)
import warnings
import logging
logging.getLogger().setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", category=UserWarning)
	
if __name__ == "__main__":
	import sys
	if len(sys.argv) > 1:
		file_name = sys.argv[1]
		create_bionic_book(file_name)
	else:
		file_name = input("Drag and drop your file into the terminal: ").strip("& '\"")
	create_bionic_book(file_name)
	print("Your bionic book is ready!")
	input("Have a nice read! Press Enter to exit...")