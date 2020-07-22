# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import csv
import os
import shutil
from datetime import datetime

from cli import args

TEMP_FOLDER = '../temp'


class AmazonscraperPipeline:
    def process_item(self, item, spider):
        self.save_temp(item)
        return item

    def save_temp(self, item):
        """La funzione crea una cartela temp dove inserire le informazioni acquisite di ciascun prodotto, così come sono
        prese da Amazon.
        Se la cartella non esiste la crea.
        Se la cartella esiste, crea al suo interno un file con lo stesso nome del codice del prodotto, e inserisce la
        prima riga del csv con il nome delle colonne."""
        file_name = os.path.join(TEMP_FOLDER, item["code"])

        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)

        with open(file_name, mode='a', newline='') as file:
            file_writer = csv.writer(file, delimiter=',')
            file_writer.writerow(
                [item["time"], item["code"], item["product_price"], item["product_condition"], item["product_seller"]])

    def close_spider(self, spider):
        """Funzione che viene eseguita al termine della pipeline, quando non ci sono più item da processare.
        Per ogni file creato in precedenza mi preno una lista composta dai prodotto con i migliori prezzi.
        Al termine dell'esecuzione cancello la cartella temp e il suo contenuto."""
        products = self.enlist()
        self.save(products)
        self.del_temp()

    def enlist(self):
        """Per ogni file presente nella cartella temp, analizzo i prodotti contenuti all'interno e mi faccio
        restituire i prodotti con il prezzo più basso divisi per categoria.
        Le categorie sono:
        + Venduto da Amazon - Nuovo
        + Venduto da Amazon - Usato
        + Venduto da terzi - Nuovo
        + Venduto da terzi - Usato"""
        to_insert = []

        for file in os.listdir(TEMP_FOLDER):
            file_name = os.path.join(TEMP_FOLDER, file)

            amazon_new = None
            amazon_used = None
            other_new = None
            other_used = None

            with open(file_name, newline='') as temp_file:
                products = list(csv.reader(temp_file))
                for product in products:
                    if "Nuovo" in product[3] and "Amazon" in product[4]:
                        amazon_new = product
                        break

                for product in products:
                    if "Usato" in product[3] and "Amazon" in product[4]:
                        amazon_used = product
                        break

                for product in products:
                    if "Nuovo" in product[3] and "Amazon" not in product[4]:
                        other_new = product
                        break

                for product in products:
                    if "Usato" in product[3] and "Amazon" not in product[4]:
                        other_used = product
                        break

                to_insert.append([amazon_new, amazon_used, other_new, other_used])

        return to_insert

    def save(self, products):
        """Per ogni prodotti in arrivo, controllo il codice di prodotto e lo salvo nel giusto file della cartella
        Prodotti"""
        for product in products:
            to_save = []

            try:
                to_save.append(product[0][0])
            except TypeError:
                to_save.append(datetime.now().strftime("%Y/%m/%d %H:%M"))

            try:
                to_save.append(product[0][2])  # amazon
            except TypeError:
                to_save.append(None)

            try:
                to_save.append(product[1][2])  # amazon_warehouse
            except TypeError:
                to_save.append(None)

            try:
                to_save.append(product[2][2])  # new_ext
            except TypeError:
                to_save.append(None)

            try:
                to_save.append(product[3][2])  # used_ext
            except TypeError:
                to_save.append(None)

            self.write_csv(product, to_save)

    def write_csv(self, product, to_save):
        """
        Funzione che controlla la presenza di un product_code valido prima di salvare su file i nuovi prezzi aggiornati
        L'assenza di un product_code valido indica l'assenza dei prezzi nelle varie fascie di prezzi, quindi la
        completa assenza del prodotto su amazon con quel codice
        :param product: Array che rappresenta un prodotto con i vari prezzi (Amazon nuovo/usato, Esterno nuovo/usato)
        :param to_save: Array di soli prezzi ordinati e tempo della rilevazione
        :return: null
        """
        file_name = os.path.join(args.PRODUCT_FOLDER, self.get_code(product))

        if file_name:
            with open(file_name, mode='a', newline='') as file:
                file_writer = csv.writer(file, delimiter=',')
                file_writer.writerow(to_save)

    def get_code(self, product):
        """
        Avuta la lista di informazioni per il prodotto (Amazon nuovo/usato, Esterno nuovo/usato) mi assicuro che almeno
        uno di questi abbia le informazioni che mi servono. Nello specifico controllo il codice
        :param product:
        :return:
        """
        for product_code in product:
            try:
                if product_code[1]:
                    return product_code[1]
            except TypeError:
                continue
        return ''

    def del_temp(self):
        shutil.rmtree(TEMP_FOLDER)
