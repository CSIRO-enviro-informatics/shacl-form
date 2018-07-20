# shacl-form
This repository contains a Python package that generates HTML + JS
webforms from given [W3C](https://www.w3.org/)
[Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/)
"shapes". The intention is to allow for the auto-generation of web UIs,
given only a logical expression of the required data that the UI is to
facilitate the input of. Additionally, this can convert submitted form
data back into RDF format.

## License
This work is licensed using the GPL v3 license. See [LICENSE](LICENSE)
for the deed.

## Contacts
This work is being conducted by a
[Griffith University](https://griffith.edu.au) Industrial Placement
student at the [CSIRO](https://www.csiro.au).

**Laura Guillory**  
*Lead Developer*  
Griffith University Industrial Placement Student at CSIRO Land & Water  
<laura.guillory@griffithuni.edu.au>

**Nicholas Car**  
*Product Owner*  
Senior Experimental Scientist  
CSIRO Land & Water  
<nicholas.car@csiro.au>

## How to use

This package is intended to fulfil two main functions - to convert a
SHACL Shapes file into a HTML + JS webform, and to convert form data
back into RDF format.

Please see the example at
[shacl-form-example](https://github.com/Laura-Guillory/shacl-form-example).

**Supplying a SHACL shapes file**  
A SHACL Shapes file must be supplied to define the data that the form
accommodates. While optional, it is ideal to use the SHACL constraints
sh:name, sh:description and sh:order. These are non-validating SHACL
properties that will improve the appearance of the form.

This tool is intended to generate a form for only one Shape at a time, 
though a Shape may consist of multiple NodeShapes. If multiple 
NodeShapes are present in the file, this tool will attempt to determine 
which NodeShape is the 'root' Shape. If two unrelated NodeShapes are 
present, only one will be present in the form and results may be
inconsistent.

**Generating the webform**  
Use generate_form(). You must supply a Shapes Graph or a file-like
object containing a SHACL Shape in RDF Turtle format. You must also
supply the desired destination for of the HTML form and the RDF map
file.

It will generate two files:
* `view/templates/form_contents.html` is a Jinja2 template which extends
`form.html.` You will want to edit form.html to control where the form
appears on your site.
* `map.ttl` is a Turtle RDF file which is used to convert information
submitted to the form back into RDF.

These two files are a pair and can't be interchanged with files
generated for another shape.

If you want to run this tool from the command line, use:

    python generate_form.py <SHACL file path> <optional: HTML form destination> <optional: RDF map destination>

**Converting form data**  
Use Form2RDFController, supplying the base_uri (which determines the URI
that will be generated for the entries submitted by the form), the
request received from the form, and the path of `map.ttl`.

It will return an RDF graph containing the data that was submitted to
the form.

## Supported constraints

These constraints are optional unless stated otherwise.

Each property in a supplied SHACL Shapes file corresponds to one input
field in the resulting webform. Each constraint applied to a property
affects the corresponding input field in the following ways:

**sh:path**  
Determines the HTML name of the input field, and if there is no sh:name,
determines the user-readable label that accompanies the input field. A
required constraint, since the sh:path defines its property in a Shape.

**sh:nodeKind**  
Determines what kind of node the property refers to. Options for 
sh:NodeKind are: sh:Literal, sh:IRI, sh:BlankNode, sh:BlankNodeOrIRI, 
sh:IRIOrLiteral, sh:BlankNodeOrLiteral 

1. Literal - Entered as a plain value (for example, a string, number or
date) with constraints applying as normal
2. IRI - A pattern is applied to ensure the value entered looks like an 
IRI, but the validity of the IRI is not checked. An IRI should refer to 
a node that already exists. For example, you might want a person to be a
supervisor of another person, so you would enter the IRI of the other
person.
3. BlankNode - The property will consist of other properties. For
example, an address will be made up of a street name, postcode, country,
etc.
4. BlankNodeOrIRI - The user can pick between entering a BlankNode or 
IRI
5. IRIOrLiteral - The user can pick between entering an IRI or Literal
6. BlankNodeOrLiteral - The user can pick between entering a Blank Node
or Literal.

If the property doesn't fit the specified nodeKind, shacl-form will
provide a warning and the property will look odd/empty.

**sh:name**  
Determines the user-readable label that accompanies the input field.

**sh:description**  
Determines the user-readable description that accompanies the input
field.

**sh:defaultValue**  
Determines the default value of the input field.

**sh:group**  
Determines the group that the input field belongs to. All input fields
belonging to a group will appear together. The group must refer to an
existing Property Group in the SHACL Shapes file. The Property Group may
use rdfs:label to specify the label for the group of properties, and may
use sh:order to specify the order in which groups appear (if there are
multiple groups).

**sh:order**  
Determines the order in which the input fields appear. Also used in
Property Groups to determine the order in which
groups appear. The order is as follows:

1. All ordered groups in ascending order
    * (Within each group) All ordered properties in ascending order
    * (Within each group) All unordered properties

2. All unordered groups
    * (Within each group) All ordered properties in ascending order
    * (Within each group) All unordered properties

3. All ungrouped ordered properties in ascending order
4. All ungrouped unordered properties

**sh:minCount**  
Determines the minimum number of input fields that may be present for
each property.

**sh:maxCount**  
Determines the maximum number of input fields that may be present for
each property.

**sh:in**  
Should supply a list of options. The input field will be a dropdown
containing all the options.

**sh:datatype**  
The datatype will determine the input field type.

| Datatype                           | Input Type |
|------------------------------------|------------|
| xsd:integer, xsd:float, xsd:double | number     |
| xsd:date                           | date       |
| xsd:time                           | time       |
| xsd:boolean                        | checkbox   |

Otherwise, it will be of type `text`.

**sh:minInclusive**  
Will set the minimum accepted value of the input field, including the
value provided. The user will not be able to submit values outside the
accepted range.

**sh:maxExclusive**  
Will set the maximum accepted value of the input field, excluding the
value provided. The user will not be able to submit values outside the
accepted range.

**sh:maxInclusive**  
Will set the maximum accepted value of the input field, including the
value provided. The user will not be able to submit values outside the
accepted range.

**sh:minExclusive**  
Will set the minimum accepted value of the input field, excluding the
value provided. The user will not be able to submit values outside the
accepted range.

**sh:maxlength**  
Will set the maximum length of the input field.

**sh:minLength**
Will set the minimum length of the input field.

**sh:pattern**  
Will set the regex pattern of the input field. Note that a blank field
will still be accepted unless the field is also required. ^ and $ will
be added around the pattern provided.

**sh:flags**  
For use with sh:pattern. The flags set the modifier to be used with the 
regex expression. Available flags: m, i

**sh:hasValue**  
This input field will be present when the form is submitted, but will be
hidden from the user.

**sh:equals**  
This input field will be required to equal the referenced property. Note
that unless the field is required, an empty field will be valid.

**sh:disjoint**  
This input field will not be permitted to equal the referenced property.

**sh:lessThan**  
This input field must have a value that is less than the referenced
property.

**sh:lessThanOrEquals**  
This input field must have a value that is less than or equal to the
referenced property.

**Other**  
*foaf:mbox*  
If a property requires a foaf:mbox predicate, the corresponding input
field will have input type `email`.

*foaf:phone*  
If a property requires a foaf:phone predicate, the corresponding input
field will have input type `tel`.

## Other Features

**Open/Closed Shapes**  
Shapes may have a property of sh:closed.  
If sh:closed is True, only properties that are explicitly defined will
be present in the form.  
If sh:closed is False, the user will be able to add custom properties in
addition to properties that have been explicitly defined  
If sh:closed is absent, it will be assumed that it is equal to False.

If a Shape is closed, its form will also contain input fields for
properties specified in sh:ignoredProperties.