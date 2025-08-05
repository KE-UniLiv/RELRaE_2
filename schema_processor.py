# Handle the input schema and create objects
from lxml import etree as ET


class Schema:

    def __init__(self, path):
        self.path = path
