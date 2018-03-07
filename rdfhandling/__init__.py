import rdflib

g = rdflib.Graph()
g.parse('relatives.ttl', format='turtle')

q = ''' SELECT DISTINCT ?s 
        WHERE {
            ?s rdf:type <http://example.org/relatives#Person> .
            #?s ?p ?o .
        }'''

for r in g.query(q):
    print(r)
