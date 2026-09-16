# SXPF - Simple XML Pattern Format

## Quick Start

SXPF is a YAML format designed to facilitate the capture
and translation of XML fragments into corresponding RDF
fragments.

An example of an SXPF pattern is given below:

```YAML
- rule:
    name: 3) attribute -> DatatypeProperty
    element_type: XsdComplexType
    selector:
    - pattern: has_attribute
      attribute: All
    emit: |
      f"""
      {self.prefix}:{self.is_boolean(parts["attribute"])}{self.get_elem_name(parts["attribute"])} a owl:DatatypeProperty ;
        rdfs:label '{self.is_boolean(parts["attribute"])}{self.get_elem_name(parts["attribute"])}'@en ;
        rdfs:domain {self.prefix}:{self.get_elem_name(concept)} ;
        rdfs:range {self.check_datatype(parts["attribute"])} ;
        {prov_block}
      """
```

Each SXPF rule consists of 3-4 main parts:

- `name`: a plain text name for the rule
- `element_type`: the type of element the rule is looking for to
  begin more complex checks. Uses schema objects from the python
  xmlschema package
- `selector`: contains additional criteria to check for a match.
  Simple rule don't always need a selector
- `emit`: a python f-string to generate the RDF fragment

## Selector Patterns and Fields

- `has_child`
  - `child_type`: `xmlschema` object. For selecting parent-child
  relationships.
- `has_attribute`
  - `attribute`: `str` attribute name. Defaults to all attributes.
  For selecting element-attribute relationships.
- `has_choice`
  - child_type: `xmlschema` object. For selecting parent-child
  relationships where there are many children.

## Emit Methods

The emit field is a python f-string. This is to allow the system to
process labels correctly and format the RDF. The methods supported
are as follows:

*NOTE: where `concept` is referenced this refers to an `xmlschema` object*

- `self.get_elem_name(concept)`: Returns a string with the name of the
  element.
- `self.is_built_in(concept)`: Checks in an element is Xsd Built-in
  concept. Returns the name of element.
- `self.is_boolean(concept)`: Checks if a datatype is boolean, if yes,
  returns the string "is", if not returns the string "has". This is
  intended to allow meaningful labels to be generated for boolean
  relationships.
- `self.check_datatype(concept)`: Returns a formatted string representing
  the datatype of a concept in valid RDF.

## Emit Variables

- `prov_block`: Returns an RDF fragment containing provenance about a
  relationship. I.e. what module generated the relationship and what XML
  element does it relate to.

## Additionally Functionality

In the future, we intend to support additional methods for processing more
relationships. If you wish to contribute to this effort, we gratefully welcome
your contributions.
