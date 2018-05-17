# shacl-form
This repository contains a Python application that generates HTML + JS webforms from given [W3C](https://www.w3.org/) [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/) "shapes". The intention is to allow for the auto-generation of web UIs, given only a logical expression of the required data that the UI is to facilitate the input of.

## License
This work is licensed using the GPL v3 license. See [LICENSE](LICENSE) for the deed.

## Contacts
This work is being conducted by a [Griffith University](https://griffith.edu.au) Industrial Placement student at the [CSIRO](https://www.csiro.au).

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

**1. Supplying a SHACL shapes file**  
A SHACL shapes file must be supplied to define the data that the form accommodates. While optional, it is ideal to use the SHACL constraints sh:name, sh:description and sh:order. These are non-validating SHACL properties that will improve the appearance of the form. Examples can be found in the 'examples' directory.

**2. Generating the webform**  
Run main.py in the 'form-generator' directory to generate the webform. The path to a SHACL shapes file must be supplied. The files generated will be automatically placed in Flask ready to work, but an alternate destination can optionally be provided.

Usage:

    python main.py <SHACL file path> <optional: destination>

**3. Start Flask**  
Run app.py in the 'miniflask' directory

Your webform can now be accessed at `localhost:5000/form` in your browser. Any information entered into the form will be stored in `miniflask/result.ttl`.

## Supported constraints

These constraints are optional unless stated otherwise.

Each property in a supplied SHACL Shapes file corresponds to one input field in the resulting webform. Each constraint 
applied to a property affects the corresponding input field in the following ways:

**sh:path**  
Determines the HTML name of the input field, and if there is no sh:name, determines the user-readable label that 
accompanies the input field. A required constraint, since the sh:path defines its property in a Shape.

**sh:name**  
Determines the user-readable label that accompanies the input field.

**sh:description**  
Determines the user-readable description that accompanies the input field.

**sh:defaultValue**  
Determines the default value of the input field.

**sh:group**  
Determines the group that the input field belongs to. All input fields belonging to a group will appear together. The 
group must refer to an existing Property Group in the SHACL Shapes file. The Property Group may use rdfs:label to 
specify the label for the group of properties, and may use sh:order to specify the order in which groups appear (if 
there are multiple groups).

**sh:order**  
Determines the order in which the input fields appear. Also used in Property Groups to determine the order in which
groups appear. The order is as follows:

1. All ordered groups in ascending order
    * (Within each group) All ordered properties in ascending order
    * (Within each group) All unordered properties in ascending order

2. All unordered groups
    * (Within each group) All ordered properties in ascending order
    * (Within each group) All unordered properties in ascending order

3. All ungrouped ordered properties in ascending order  
4. All ungrouped unordered properties

**sh:minCount**
Determines the minimum number of input fields that may be present for each property.

**sh:maxCount**
Determines the maximum number of input fields that may be present for each property.

**sh:in**  
Should supply a list of options. The input field will be a dropdown containing all the options.

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
Will set the minimum accepted value of the input field, including the value provided. The user will not be able to
submit values outside the accepted range.

**sh:maxExclusive**
Will set the maximum accepted value of the input field, excluding the value provided. The user will not be able to
submit values outside the accepted range.

**sh:maxInclusive**
Will set the maximum accepted value of the input field, including the value provided. The user will not be able to
submit values outside the accepted range.

**sh:minExclusive**
Will set the minimum accepted value of the input field, excluding the value provided. The user will not be able to
submit values outside the accepted range.

**sh:maxlength**
Will set the maximum length of the input field.

**sh:pattern**
Will set the regex pattern of the input field. Note that a blank field will still be accepted unless the field is also
required. ^ and $ are assumed to encapsulate the pattern.

**sh:hasValue**
This input field will be displayed to the user and submitted with the form, but they will be unable to change it. The
value of this input field will be pre-filled and it will be disabled and set to readonly. This field will also be
excluded from form validation.

**sh:equals**
This input field will be required to equal the referenced property. Note that unless the field is required, an empty
field will be valid.

**sh:disjoint**
This input field will not be permitted to equal the referenced property.

**sh:lessThan**
This input field must have a value that is less than the referenced property.

**sh:lessThanOrEquals**
This input field must have a value that is less than or equal to the referenced property.

**Other**  
*foaf:mbox*  
If a property requires a foaf:mbox predicate, the corresponding input field will have input type `email`.

*foaf:phone*
If a property requires a foaf:phone predicate, the corresponding input field will have input type `tel`.
