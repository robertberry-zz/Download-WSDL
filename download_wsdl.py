#!/usr/bin/env python

import argparse
import urllib2
import xml.dom.minidom as minidom
import sys

from urlparse import urljoin

class Definition(object):
    """Represents a WSDL or XSD definition file.
    """
    def __init__(self, url):
        self.url = url
        self.doc = minidom.parse(urllib2.urlopen(url))

    @property
    def imports(self):
        """All imported files.
        """
        return self.wsdl_imports + self.xsd_imports

    @property
    def wsdl_imports(self):
        """All imported WSDL definitions.
        """
        nodes = self.doc.getElementsByTagName("wsdl:import")
        paths = [node.attributes.getNamedItem("location").value for node in \
                     nodes]
        return [urljoin(self.url, path) for path in paths]

    @property
    def xsd_imports(self):
        """All imported XSD definitions.
        """
        nodes = self.doc.getElementsByTagName("xsd:import")
        paths = [node.attributes.getNamedItem("schemaLocation").value for node in \
                     nodes]
        return [urljoin(self.url, path) for path in paths]        

    def __repr__(self):
        """Prints out url of the definition.
        """
        return "<Definition url='%s'>" % self.url

def all_definitions(definition, seen=None, callback=None):
    """Recursive function for determining all related definitions for a WSDL
    file. Seen may be passed as a set of urls to ignore definitions
    for. Callback may be passed to be invoked every time a new definition is loaded.
    """
    definition = Definition(definition)
    if callback and callable(callback):
        callback(definition)
    
    if seen is None:
        seen = {definition.url}

    imports = set(definition.imports) - seen

    for i in imports:
        seen.add(i)
        seen = all_definitions(i, seen, callback)

    return seen
    
def main():
    parser = argparse.ArgumentParser(description="Download WSDL definitions.")
    parser.add_argument("url", help="WSDL definition file.")

    args = parser.parse_args()

    print "loading definitions",
    
    def load_file(definition):
        print ".",
        sys.stdout.flush()

    definitions = all_definitions(args.url, callback=load_file)
    print

    for definition in definitions:
        print definition



if __name__ == '__main__':
    main()
    
