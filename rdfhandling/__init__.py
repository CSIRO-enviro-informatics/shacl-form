import rdflib

g = rdflib.Graph()
g.parse('relatives.ttl', format='turtle')

q = ''' SELECT (COUNT(*) AS ?count) 
        WHERE {
            ?s ?p ?o .
        }'''

for r in g.query(q):
    print(int(r[0]))
