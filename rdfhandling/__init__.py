import rdflib

g = rdflib.Graph()
g.parse('relatives.ttl', format='turtle')

q = ''' SELECT DISTINCT ?s 
        WHERE {
            [] <http://example.org/relatives#hasChild> ?s .
        }'''

for r in g.query(q):
    print(r.s)
