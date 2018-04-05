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
minCount >= 1: The input field will be a required field.
minCount < 1 or no minCount constraint: The input field will be optional.

**sh:maxCount**
No current support

**sh:in**  
Should supply a list of options. The input field will be a dropdown containing all the options.

**sh:datatype**
If the datatype is xsd:integer, xsd:float or xsd:double, the input field will be of type 'number'. Otherwise, it will be
of type 'text'.

**Other**  
*foaf:mbox*  
If a property requires a foaf:mbox, the corresponding input field will have input type `email`.
