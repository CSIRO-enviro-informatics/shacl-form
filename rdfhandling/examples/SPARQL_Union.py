# Demonstrates the use of a union to access names stored with different vocabularies

import rdflib

g = rdflib.Graph()
g.parse('vc-db-3.ttl', format='turtle')

q = '''
        SELECT ?name
        WHERE
        {
            { ?person foaf:name ?name } UNION { ?person vcard:FN ?name }
        }
    '''

for result in g.query(q):
    print(result[0])
