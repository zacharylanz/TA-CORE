# main.py

import mitre_cti_pull
import enrichment_main
import os
import requests
import yaml
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
import docx
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter

def main():
    mitre_cti_pull.main()
    enrichment_main.main()

if __name__ == "__main__":
    main()
