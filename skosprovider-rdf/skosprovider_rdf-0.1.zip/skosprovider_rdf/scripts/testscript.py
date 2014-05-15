from rdflib import Graph
from rdflib.namespace import RDF, SKOS
from skosprovider_rdf.providers import RDFProvider
from skosprovider_rdf import utils

graph = Graph()
graph.parse("../../tests/data/simple_turtle_products", format="turtle")
# for subject,predicate,obj in graph:
#     print subject + " &" + predicate + "&" + obj
print (SKOS)
for s, p, o in graph.triples((None, RDF.type, SKOS.Concept)):
    print (s + " is a Concept")
    for s, p, o in graph.triples((s, None, None)):
        print (p + "&" + o + " zijn de predicates en objects van dit subject")

# for x in graph.triples( (None, None, None) ):
#     print (x)

provider = RDFProvider({'id': 'SOORTEN', 'conceptscheme_id': 2}, graph)
print("All count: " , len(provider.find({'type': 'all'})))
print("Conceptcount: " , len(provider.find({'type': 'concept'})))
print("Collectioncount: " , len(provider.find({'type': 'collection'})))

graph_dump=utils.rdf_dumper(provider)

dump= graph_dump.serialize(format='xml')
print (dump)



#
# g = Graph()
# g.parse("../tests/data/demo.nt", format="nt")
#
# print(len(g))  # prints 2
#
# import pprint
#
# for stmt in g:
#     pprint.pprint(stmt)
#
# print g.serialize(format='turtle')
#
# n = Namespace("http://example.org/people/")
#
# n.bob # = rdflib.term.URIRef(u'http://example.org/people/bob')
# n.linda # = rdflib.term.URIRef(u'http://example.org/people/linda')
#
# RDF.type# = rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
#
# FOAF.knows# = rdflib.term.URIRef(u'http://xmlns.com/foaf/0.1/knows')
#
# h = Graph()
# h.add((n.bob, RDF.type, FOAF.Person))
# h.add((n.bob, FOAF.name, Literal('Name')))
# h.add((n.bob, FOAF.knows, n.linda))
# h.add((n.linda, RDF.type, FOAF.Person))
# h.add((n.linda, FOAF.name, Literal('Linda')))
#
#