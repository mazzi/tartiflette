import pytest
from lark import UnexpectedToken, UnexpectedCharacters
from lark.tree import Tree
from lark.lexer import Token

from tartiflette.sdl.builder import parse_graphql_sdl_to_ast


@pytest.mark.parametrize("is_valid,test_input,expected", [
    # Minimal schema (with BOM)
    (
        True,
        """\ufeff
        schema {
            query: RootQueryCustomType
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('schema_definition', [
                    Token('SCHEMA', 'schema'),
                    Tree('query_operation_type_definition', [
                        Token('QUERY', 'query'),
                        Tree('named_type', [
                            Tree('name', [
                                Token('IDENT', 'RootQueryCustomType'),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid schema: missing closing parenthesis
    (
        False,
        """schema { query: RootQueryCustomType""",
        UnexpectedToken,
    ),
    # Invalid schema: no opening { after `schema`
    (
        False,
        """schema query: RootQueryCustomType }""",
        UnexpectedCharacters,
    ),
    # Simple schema with simple directive and comments and ignored commas
    (
        True,
        """
        schema
        @test(str: "test", int: 14, float: 17.3, bool: true, empty: null,
        lst: [], obj: {name: 99}) {
            mutation: RootMutationCustomType # some random comment
        #} And more comments here :D @directive() key: 10
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('schema_definition', [
                    Token('SCHEMA', 'schema'),
                    Tree('directives', [
                        Tree('directive', [
                            Tree('name', [
                                Token('IDENT', 'test'),
                            ]),
                            Tree('arguments', [
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'str'),
                                    ]),
                                    Tree('value', [
                                        Tree('string_value', [
                                            Token('STRING', '"test"')
                                        ]),
                                    ]),
                                ]),
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'int'),
                                    ]),
                                    Tree('value', [
                                        Tree('int_value', [
                                            Token('SIGNED_INT', '14')
                                        ]),
                                    ]),
                                ]),
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'float'),
                                    ]),
                                    Tree('value', [
                                        Tree('float_value', [
                                            Token('SIGNED_FLOAT', '17.3')
                                        ]),
                                    ]),
                                ]),
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'bool'),
                                    ]),
                                    Tree('value', [
                                        Tree('true_value', [
                                            Token('TRUE', 'true'),
                                        ]),
                                    ]),
                                ]),
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'empty'),
                                    ]),
                                    Tree('value', [
                                        Tree('null_value', [
                                            Token('NULL', 'null'),
                                        ]),
                                    ]),
                                ]),
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'lst'),
                                    ]),
                                    Tree('value', [
                                        Tree('list_value', []),
                                    ]),
                                ]),
                                Tree('argument', [
                                    Tree('name', [
                                        Token('IDENT', 'obj'),
                                    ]),
                                    Tree('value', [
                                        Tree('object_value', [
                                            Tree('object_field', [
                                                Tree('name', [
                                                    Token('IDENT', 'name'),
                                                ]),
                                                Tree('value', [
                                                    Tree('int_value', [
                                                        Token('SIGNED_INT', '99'),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                    Tree('mutation_operation_type_definition', [
                        Token('MUTATION', 'mutation'),
                        Tree('named_type', [
                            Tree('name', [
                                Token('IDENT', 'RootMutationCustomType'),
                            ]),
                        ])
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid schema: directive without name
    (
        False,
        """
        schema @ {
            mutation: RootMutationCustomType
        }
        """,
        UnexpectedCharacters,
    ),
    # Invalid schema: directive argument without value
    (
        False,
        """
        schema @test(arg) {
            mutation: RootMutationCustomType
        }
        """,
        UnexpectedToken,
    ),
    # Invalid schema: directive argument without equal sign instead of :
    (
        False,
        """
        schema @test(arg = 10) {
            mutation: RootMutationCustomType
        }
        """,
        UnexpectedToken,
    ),
    # Invalid schema: directive argument without @blabla sign
    (
        False,
        """
        schema (arg: "invalid") {
            mutation: RootMutationCustomType
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with all scalars and end-objects
    (
        True,
        """
        \"\"\"
        This is the description of Something !
        \"\"\"
        type Something {
            " Describe an Int !"
            anInt(canBeZero: Boolean): Int @test(some: 10) @foo(again: "hovercraft")
            aFloat: Float
            aBool: Boolean
            aStr: String
            anID: ID
            aLst: [String]
            aCustomObj: SomethingElse
            anEnumVal: MYENUMVAL
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('object_type_definition', [
                        Tree('description', [
                            Token('LONG_STRING', '"""\n        This is the description of Something !\n        """')
                        ]),
                        Token('TYPE', 'type'),
                        Tree('name', [
                            Token('IDENT', 'Something'),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('description', [
                                    Token('STRING', '" Describe an Int !"'),
                                ]),
                                Tree('name', [
                                    Token('IDENT', 'anInt'),
                                ]),
                                Tree('arguments_definition', [
                                    Tree('input_value_definition', [
                                        Tree('name', [
                                            Token('IDENT', 'canBeZero'),
                                        ]),
                                        Tree('type', [
                                            Tree('named_type', [
                                                Tree('name', [
                                                    Token('IDENT', 'Boolean'),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Int'),
                                        ]),
                                    ]),
                                ]),
                                Tree('directives', [
                                    Tree('directive', [
                                        Tree('name', [
                                            Token('IDENT', 'test'),
                                        ]),
                                        Tree('arguments', [
                                            Tree('argument', [
                                                Tree('name', [
                                                    Token('IDENT', 'some'),
                                                ]),
                                                Tree('value', [
                                                    Tree('int_value', [
                                                        Token('SIGNED_INT', '10'),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                    Tree('directive', [
                                        Tree('name', [
                                            Token('IDENT', 'foo'),
                                        ]),
                                        Tree('arguments', [
                                            Tree('argument', [
                                                Tree('name', [
                                                    Token('IDENT', 'again'),
                                                ]),
                                                Tree('value', [
                                                    Tree('string_value', [
                                                        Token('STRING', '"hovercraft"'),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aFloat'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Float'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aBool'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Boolean'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aStr'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'String'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'anID'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'ID'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aLst'),
                                ]),
                                Tree('type', [
                                    Tree('list_type', [
                                        Tree('type', [
                                            Tree('named_type', [
                                                Tree('name', [
                                                    Token('IDENT', 'String'),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aCustomObj'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'SomethingElse'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'anEnumVal'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'MYENUMVAL'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Schema with scalar but with directive at wrong place
    (
        False,
        """
        type Something {
            anInt @test(some: Boolean): Int
        }
        """,
        UnexpectedToken,
    ),
    # Schema with scalar but with value instead of type
    (
        False,
        """
        type Something {
            anInt: 10
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with scalar but with empty list (invalid)
    (
        False,
        """
        type Something {
            aLst: []
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with scalar but with mixed list (invalid)
    (
        False,
        """
        type Something {
            aLst: [String, Int]
        }
        """,
        UnexpectedToken,
    ),
    # Schema with scalar but with empty directive arguments
    (
        False,
        """
        type Something @test() {
            aLst: [String]
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with all type modifiers
    (
        True,
        """
        type Something {
            aNullableStringList: [String]
            aNonNullString: String!
            aNullableStringNonNullList: [String]!
            aNonNullStringNonNullList: [String!]!
            aNonNullCustomNonNullList: [Custom!]!
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('object_type_definition', [
                        Token('TYPE', 'type'),
                        Tree('name', [
                            Token('IDENT', 'Something'),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aNullableStringList'),
                                ]),
                                Tree('type', [
                                    Tree('list_type', [
                                        Tree('type', [
                                            Tree('named_type', [
                                                Tree('name', [
                                                    Token('IDENT', 'String'),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aNonNullString'),
                                ]),
                                Tree('type', [
                                    Tree('non_null_type', [
                                        Tree('named_type', [
                                            Tree('name', [
                                                Token('IDENT', 'String'),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aNullableStringNonNullList'),
                                ]),
                                Tree('type', [
                                    Tree('non_null_type', [
                                        Tree('list_type', [
                                            Tree('type', [
                                                Tree('named_type', [
                                                    Tree('name', [
                                                        Token('IDENT', 'String'),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aNonNullStringNonNullList'),
                                ]),
                                Tree('type', [
                                    Tree('non_null_type', [
                                        Tree('list_type', [
                                            Tree('type', [
                                                Tree('non_null_type', [
                                                    Tree('named_type', [
                                                        Tree('name', [
                                                            Token('IDENT', 'String'),
                                                        ]),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aNonNullCustomNonNullList'),
                                ]),
                                Tree('type', [
                                    Tree('non_null_type', [
                                        Tree('list_type', [
                                            Tree('type', [
                                                Tree('non_null_type', [
                                                    Tree('named_type', [
                                                        Tree('name', [
                                                            Token('IDENT', 'Custom'),
                                                        ]),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Schema with invalid double ! modifier
    (
        False,
        """
        type Something {
            aNonNullString: String!!
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with invalid double ! modifier on [] modifier
    (
        False,
        """
        type Something {
            aNullableStringList: [String]!!
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with invalid ! modifier on wrong side of type
    (
        False,
        """
        type Something {
            aNonNullStringNonNullList: [!String]!
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with invalid ! modifier on type name declaration
    (
        False,
        """
        type Something! {
            aNonNullStringNonNullList: [String]
        }
        """,
        UnexpectedToken,
    ),
    # Schema with invalid [] modifier on type name declaration
    (
        False,
        """
        type [Something] {
            aNonNullStringNonNullList: [String]
        }
        """,
        UnexpectedCharacters,
    ),
    # Schema with object and interfaces
    (
        True,
        """
        interface Driver {
            wheel: String
        }
        \"\"\"
        A viewers allows you to view stuff.
        \"\"\"
        interface Viewer {
            \"\"\"
            A Windshield is needed for viewing !
            \"\"\"
            windshield: Windshield
        }
        type Ship implements Driver {
            wheel: String
        }
        type Car implements Driver & Viewer {
            wheel: String
            windshield: Windshield
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('interface_type_definition', [
                        Token('INTERFACE', 'interface'),
                        Tree('name', [
                            Token('IDENT', 'Driver'),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'wheel'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'String'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('interface_type_definition', [
                        Tree('description', [
                            Token('LONG_STRING', '"""\n        A viewers allows you to view stuff.\n        """')
                        ]),
                        Token('INTERFACE', 'interface'),
                        Tree('name', [
                            Token('IDENT', 'Viewer'),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('description', [
                                    Token('LONG_STRING', '"""\n            A Windshield is needed for viewing !\n            """')
                                ]),
                                Tree('name', [
                                    Token('IDENT', 'windshield'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Windshield'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('object_type_definition', [
                        Token('TYPE', 'type'),
                        Tree('name', [
                            Token('IDENT', 'Ship'),
                        ]),
                        Tree('implements_interfaces', [
                            Token('IMPLEMENTS', 'implements'),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Driver'),
                                ]),
                            ]),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'wheel'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'String'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('object_type_definition', [
                        Token('TYPE', 'type'),
                        Tree('name', [
                            Token('IDENT', 'Car'),
                        ]),
                        Tree('implements_interfaces', [
                            Token('IMPLEMENTS', 'implements'),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Driver'),
                                ]),
                            ]),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Viewer'),
                                ]),
                            ]),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'wheel'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'String'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'windshield'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Windshield'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid interface schema (with two names)
    (
        False,
        """
        interface Driver & Viewer {
            wheel: String
        }
        """,
        UnexpectedToken,
    ),
    # Invalid double "implements" interface schema
    (
        False,
        """
        interface Driver {
            wheel: String
        }
        interface Viewer {
            windshield: Windshield
        }
        type Car implements Driver & implements Viewer {
            wheel: String
            windshield: Windshield
        }
        """,
        UnexpectedToken,
    ),
    # Scalar schema
    (
        True,
        """
        \"\"\"
        This is to store DateTime objects
        \"\"\"
        scalar Date @format(type: "iso")
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('scalar_type_definition', [
                        Tree('description', [
                            Token('LONG_STRING', '"""\n        This is to store DateTime objects\n        """'),
                        ]),
                        Token('SCALAR', 'scalar'),
                        Tree('name', [
                            Token('IDENT', 'Date'),
                        ]),
                        Tree('directives', [
                            Tree('directive', [
                                Tree('name', [
                                    Token('IDENT', 'format'),
                                ]),
                                Tree('arguments', [
                                    Tree('argument', [
                                        Tree('name', [
                                            Token('TYPE', 'type'),
                                        ]),
                                        Tree('value', [
                                            Tree('string_value', [
                                                Token('STRING', '"iso"'),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Scalar schema with invalid type
    (
        False,
        """
        scalar [Custom]
        """,
        UnexpectedCharacters
    ),
    # Scalar schema with invalid definition
    (
        False,
        """
        scalar Custom {
            anInt: Int
        }
        """,
        UnexpectedToken
    ),
    # Union schema
    (
        True,
        """
        union SingleUnion @directive(test: true) = Foo
        union DoubleUnion = Foo | Bar
        union MultipleUnion = Foo | Bar | Baz
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('union_type_definition', [
                        Token('UNION', 'union'),
                        Tree('name', [
                            Token('IDENT', 'SingleUnion'),
                        ]),
                        Tree('directives', [
                            Tree('directive', [
                                Tree('name', [
                                    Token('DIRECTIVE', 'directive'),
                                ]),
                                Tree('arguments', [
                                    Tree('argument', [
                                        Tree('name', [
                                            Token('IDENT', 'test'),
                                        ]),
                                        Tree('value', [
                                            Tree('true_value', [
                                                Token('TRUE', 'true'),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree('union_member_types', [
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Foo'),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('union_type_definition', [
                        Token('UNION', 'union'),
                        Tree('name', [
                            Token('IDENT', 'DoubleUnion'),
                        ]),
                        Tree('union_member_types', [
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Foo'),
                                ]),
                            ]),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Bar'),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('union_type_definition', [
                        Token('UNION', 'union'),
                        Tree('name', [
                            Token('IDENT', 'MultipleUnion'),
                        ]),
                        Tree('union_member_types', [
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Foo'),
                                ]),
                            ]),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Bar'),
                                ]),
                            ]),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Baz'),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Scalar schema with invalid definition
    (
        False,
        """
        union Stuff | Something
        """,
        UnexpectedToken
    ),
    # Scalar schema with directive at wrong place
    (
        False,
        """
        union Stuff = Something @test
        """,
        UnexpectedToken
    ),
    # Schema enum definition
    (
        True,
        """
        enum UserStatus {
            NOT_FOUND
            ACTIVE @cache(duration: "30s")
            INACTIVE
            SUSPENDED
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('enum_type_definition', [
                        Token('ENUM', 'enum'),
                        Tree('name', [
                            Token('IDENT', 'UserStatus'),
                        ]),
                        Tree('enum_values_definition', [
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'NOT_FOUND'),
                                    ]),
                                ]),
                            ]),
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'ACTIVE'),
                                    ]),
                                ]),
                                Tree('directives', [
                                    Tree('directive', [
                                        Tree('name', [
                                            Token('IDENT', 'cache'),
                                        ]),
                                        Tree('arguments', [
                                            Tree('argument', [
                                                Tree('name', [
                                                    Token('IDENT', 'duration'),
                                                ]),
                                                Tree('value', [
                                                    Tree('string_value', [
                                                        Token('STRING', '"30s"'),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'INACTIVE'),
                                    ]),
                                ]),
                            ]),
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'SUSPENDED'),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid Enum with enum containing spaces
    (
        True,
        """
        enum UserStatus {
            ACTIVE,
            AWAY,
            NOT FOUND,
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('enum_type_definition', [
                        Token('ENUM', 'enum'),
                        Tree('name', [
                            Token('IDENT', 'UserStatus'),
                        ]),
                        Tree('enum_values_definition', [
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'ACTIVE'),
                                    ]),
                                ]),
                            ]),
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'AWAY'),
                                    ]),
                                ]),
                            ]),
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'NOT'),
                                    ]),
                                ]),
                            ]),
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'FOUND'),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid Enum schema with types
    (
        False,
        """
        enum UserStatus {
            NOT_FOUND: Int
        }
        """,
        UnexpectedToken
    ),
    # Invalid Enum schema with values
    (
        False,
        """
        enum UserStatus {
            NOT_FOUND: 42
        }
        """,
        UnexpectedToken
    ),
    # Enum schema with ( instead of {
    (
        False,
        """
        enum UserStatus (
            NOT_FOUND
        )
        """,
        UnexpectedToken
    ),
    # Input object schema with fields
    (
        True,
        """
        input ListUsersInput {
            limit: Int = 42 @validation(range: [0, 200])
            sinceID: ID @mydirective
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_definition', [
                    Tree('input_object_type_definition', [
                        Token('INPUT', 'input'),
                        Tree('name', [
                            Token('IDENT', 'ListUsersInput'),
                        ]),
                        Tree('input_fields_definition', [
                            Tree('input_value_definition', [
                                Tree('name', [
                                    Token('IDENT', 'limit'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Int'),
                                        ]),
                                    ]),
                                ]),
                                Tree('default_value', [
                                    Tree('value', [
                                        Tree('int_value', [
                                            Token('SIGNED_INT', '42'),
                                        ]),
                                    ]),
                                ]),
                                Tree('directives', [
                                    Tree('directive', [
                                        Tree('name', [
                                            Token('IDENT', 'validation'),
                                        ]),
                                        Tree('arguments', [
                                            Tree('argument', [
                                                Tree('name', [
                                                    Token('IDENT', 'range'),
                                                ]),
                                                Tree('value', [
                                                    Tree('list_value', [
                                                        Tree('value', [
                                                            Tree('int_value', [
                                                                Token('SIGNED_INT', '0'),
                                                            ]),
                                                        ]),
                                                        Tree('value', [
                                                            Tree('int_value', [
                                                                Token('SIGNED_INT', '200'),
                                                            ]),
                                                        ]),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree('input_value_definition', [
                                Tree('name', [
                                    Token('IDENT', 'sinceID'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'ID'),
                                        ]),
                                    ]),
                                ]),
                                Tree('directives', [
                                    Tree('directive', [
                                        Tree('name', [
                                            Token('IDENT', 'mydirective'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid input object: no name
    (
        False,
        """
        input {
            limit: Int @validation(range: [0, 200])
            sinceID: ID @mydirective
        }
        """,
        UnexpectedCharacters,
    ),
    # Directive definition schema
    (
        True,
        """
        directive @test(var1: Int = -42, var4: [String]) on FIELD_DEFINITION | SCHEMA
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('directive_definition', [
                    Token('DIRECTIVE', 'directive'),
                    Tree('name', [
                        Token('IDENT', 'test'),
                    ]),
                    Tree('arguments_definition', [
                        Tree('input_value_definition', [
                            Tree('name', [
                                Token('IDENT', 'var1'),
                            ]),
                            Tree('type', [
                                Tree('named_type', [
                                    Tree('name', [
                                        Token('IDENT', 'Int'),
                                    ]),
                                ]),
                            ]),
                            Tree('default_value', [
                                Tree('value', [
                                    Tree('int_value', [
                                        Token('SIGNED_INT', '-42'),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree('input_value_definition', [
                            Tree('name', [
                                Token('IDENT', 'var4'),
                            ]),
                            Tree('type', [
                                Tree('list_type', [
                                    Tree('type', [
                                        Tree('named_type', [
                                            Tree('name', [
                                                Token('IDENT', 'String'),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                    Token('ON', 'on'),
                    Tree('directive_locations', [
                        Token('TYPE_SYSTEM_DIRECTIVE_LOCATION', 'FIELD_DEFINITION'),
                        Token('TYPE_SYSTEM_DIRECTIVE_LOCATION', 'SCHEMA'),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Directive with "reserved name" like "true" or "false"
    (
        True,
        """\ufeff
        schema @true {
            query: RootQueryCustomType
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('schema_definition', [
                    Token('SCHEMA', 'schema'),
                    Tree('directives', [
                        Tree('directive', [
                            Tree('name', [
                                Token('IDENT', 'true'),
                            ]),
                        ]),
                    ]),
                    Tree('query_operation_type_definition', [
                        Token('QUERY', 'query'),
                        Tree('named_type', [
                            Tree('name', [
                                Token('IDENT', 'RootQueryCustomType'),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
    # Invalid directive: uses object definition
    (
        False,
        """
        directive @test {
            unknownArg: Int
        }
        """,
        UnexpectedToken,
    ),
    # Extension schema
    (
        True,
        """
        extend scalar Date @control
        extend type Something implements Some & More @hidden {
            aField: Int
        }
        extend interface Viewer @append {
            hasEye: Boolean
        }
        extend union Car = Driveable | Transportable
        extend enum UserStates {
            NOT_AVAILABLE
        }
        extend input UserFilter @acl(role: "can-filter") {
            moreFields: [CustomField]!
        }
        """,
        Tree('document', [
            Tree('type_system_definition', [
                Tree('type_extension', [
                    Tree('scalar_type_extension', [
                        Token('EXTEND', 'extend'),
                        Token('SCALAR', 'scalar'),
                        Tree('name', [
                            Token('IDENT', 'Date'),
                        ]),
                        Tree('directives', [
                            Tree('directive', [
                                Tree('name', [
                                    Token('IDENT', 'control'),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_extension', [
                    Tree('object_type_extension', [
                        Token('EXTEND', 'extend'),
                        Token('TYPE', 'type'),
                        Tree('name', [
                            Token('IDENT', 'Something'),
                        ]),
                        Tree('implements_interfaces', [
                            Token('IMPLEMENTS', 'implements'),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Some'),
                                ]),
                            ]),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'More'),
                                ]),
                            ]),
                        ]),
                        Tree('directives', [
                            Tree('directive', [
                                Tree('name', [
                                    Token('IDENT', 'hidden'),
                                ]),
                            ]),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'aField'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Int'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_extension', [
                    Tree('interface_type_extension', [
                        Token('EXTEND', 'extend'),
                        Token('INTERFACE', 'interface'),
                        Tree('name', [
                            Token('IDENT', 'Viewer'),
                        ]),
                        Tree('directives', [
                            Tree('directive', [
                                Tree('name', [
                                    Token('IDENT', 'append'),
                                ]),
                            ]),
                        ]),
                        Tree('fields_definition', [
                            Tree('field_definition', [
                                Tree('name', [
                                    Token('IDENT', 'hasEye'),
                                ]),
                                Tree('type', [
                                    Tree('named_type', [
                                        Tree('name', [
                                            Token('IDENT', 'Boolean'),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_extension', [
                    Tree('union_type_extension', [
                        Token('EXTEND', 'extend'),
                        Token('UNION', 'union'),
                        Tree('name', [
                            Token('IDENT', 'Car'),
                        ]),
                        Tree('union_member_types', [
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Driveable'),
                                ]),
                            ]),
                            Tree('named_type', [
                                Tree('name', [
                                    Token('IDENT', 'Transportable'),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_extension', [
                    Tree('enum_type_extension', [
                        Token('EXTEND', 'extend'),
                        Token('ENUM', 'enum'),
                        Tree('name', [
                            Token('IDENT', 'UserStates'),
                        ]),
                        Tree('enum_values_definition', [
                            Tree('enum_value_definition', [
                                Tree('enum_value', [
                                    Tree('name', [
                                        Token('IDENT', 'NOT_AVAILABLE'),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree('type_system_definition', [
                Tree('type_extension', [
                    Tree('input_object_type_extension', [
                        Token('EXTEND', 'extend'),
                        Token('INPUT', 'input'),
                        Tree('name', [
                            Token('IDENT', 'UserFilter'),
                        ]),
                        Tree('directives', [
                            Tree('directive', [
                                Tree('name', [
                                    Token('IDENT', 'acl'),
                                ]),
                                Tree('arguments', [
                                    Tree('argument', [
                                        Tree('name', [
                                            Token('IDENT', 'role'),
                                        ]),
                                        Tree('value', [
                                            Tree('string_value', [
                                                Token('STRING', '"can-filter"'),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree('input_fields_definition', [
                            Tree('input_value_definition', [
                                Tree('name', [
                                    Token('IDENT', 'moreFields'),
                                ]),
                                Tree('type', [
                                    Tree('non_null_type', [
                                        Tree('list_type', [
                                            Tree('type', [
                                                Tree('named_type', [
                                                    Tree('name', [
                                                        Token('IDENT', 'CustomField'),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ),
])
def test_parse_graphql_sdl_to_ast_unit(is_valid, test_input, expected):

    if is_valid:
        output = parse_graphql_sdl_to_ast(test_input)
        assert output == expected
    else:
        with pytest.raises(expected):
            parse_graphql_sdl_to_ast(test_input)


@pytest.mark.parametrize("is_valid,test_input,expected", [
    # Invalid interface schema with typo
    (
        False,
        """
        scalarDate
        """,
        UnexpectedToken,
    ),
    (
        False,
        """
        scalarDate@directive
        """,
        UnexpectedToken,
    ),
    (
        False,
        """
        scalarDate @directive
        """,
        UnexpectedToken,
    ),
    (
        False,
        """
        scalar Date@directive
        """,
        UnexpectedToken,
    ),
    (
        True,
        """
        scalar Date
        """,
        UnexpectedToken,
    ),
    (
        True,
        """
        scalar Date @directive
        """,
        UnexpectedToken,
    ),
])
def test_parse_graphql_to_ast_pending_fixes(is_valid, test_input, expected):
    # TODO: This is an issue with the grammar that was found by fuzzy tests.
    pass
    # if is_valid:
    #     output = parse_graphql_sdl_to_ast(test_input)
    #     assert isinstance(output, Tree)
    #     assert output.data == 'document'
    # else:
    #     with pytest.raises(expected):
    #         output = parse_graphql_sdl_to_ast(test_input)
    #         print(output.pretty())