from .api import get_tabdila_data

if __name__ == "__main__":
    data = get_tabdila_data(city="Tehran", lang="fa", text_to_translate="سلام دنیا", translate_to="en")
    print(data)









