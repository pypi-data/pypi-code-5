#     Copyright 2013, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Code templates for local and module level (global) uses of exec/eval.

"""

exec_template = """\
PyObjectTemporary globals( %(globals_identifier)s );
PyObjectTemporary locals( %(locals_identifier)s );

PyObjectTemporary code( COMPILE_CODE( %(source_identifier)s, %(filename_identifier)s, %(mode_identifier)s, %(future_flags)s ) );

PyObject *result = EVAL_CODE( code.asObject0(), globals.asObject0(), locals.asObject0() );
Py_DECREF( result );"""

exec_copy_back_template = """
PyObject *locals_source = NULL;

if ( locals.asObject0() == locals_dict.asObject0() )
{
    locals_source = locals.asObject0();
}
else if ( globals.asObject0() == locals_dict.asObject0() )
{
    locals_source = globals.asObject0();
}

if ( locals_source != NULL )
{
%(store_locals_code)s
}"""
