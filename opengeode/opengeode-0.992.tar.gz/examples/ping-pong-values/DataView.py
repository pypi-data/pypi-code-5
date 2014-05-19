#!/usr/bin/env python
# ASN.1 Data model
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
asn1Files.append("DataView.asn")
asn1Modules.append("TASTE-Dataview")
exportedTypes["TASTE-Dataview"] = ["T-INTEGER", "T-SEQ", "T-POS"]
exportedVariables["TASTE-Dataview"] = ["myVar"]
importedModules["TASTE-Dataview"] = []
types["T-INTEGER"] = {
    "Line": 3, "CharPositionInLine": 0, "type": {
        "Line": 3, "CharPositionInLine": 14, "Kind": "IntegerType", "Min": "0", "Max": "255"
    }
}

types["T-SEQ"] = {
    "Line": 5, "CharPositionInLine": 0, "type": {
        "Line": 5, "CharPositionInLine": 10, "Kind": "SequenceType", "Children": {
            "hello": {
                "Optional": "False", "Line": 6, "CharPositionInLine": 1, "type": {
                    "Line": 6, "CharPositionInLine": 7, "Kind": "IntegerType", "Min": "0", "Max": "10"
                }
            }, "world": {
                "Optional": "False", "Line": 7, "CharPositionInLine": 1, "type": {
                    "Line": 7, "CharPositionInLine": 7, "Kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
                        "hop": {
                            "IntValue": 0, "Line": 7, "CharPositionInLine": 20, "EnumID": "hop"
                        }, "hips": {
                            "IntValue": 1, "Line": 7, "CharPositionInLine": 25, "EnumID": "hips"
                        }
                    }
                }
            }, "howareyou": {
                "Optional": "False", "Line": 8, "CharPositionInLine": 8, "type": {
                    "Line": 8, "CharPositionInLine": 18, "Kind": "ChoiceType", "Children": {
                        "choice-A": {
                            "Line": 8, "CharPositionInLine": 27, "EnumID": "choice_A_PRESENT", "type": {
                                "Line": 8, "CharPositionInLine": 36, "Kind": "IntegerType", "Min": "MIN", "Max": "MAX"
                            }
                        }, "choice-B": {
                            "Line": 8, "CharPositionInLine": 45, "EnumID": "choice_B_PRESENT", "type": {
                                "Line": 8, "CharPositionInLine": 54, "Kind": "ReferenceType", "ReferencedTypeName": "T-INTEGER", "Min": "0", "Max": "255"
                            }
                        }
                    }
                }
            }
        }
    }
}

types["T-POS"] = {
    "Line": 11, "CharPositionInLine": 0, "type": {
        "Line": 11, "CharPositionInLine": 10, "Kind": "SequenceType", "Children": {
            "x": {
                "Optional": "False", "Line": 12, "CharPositionInLine": 1, "type": {
                    "Line": 12, "CharPositionInLine": 3, "Kind": "ReferenceType", "ReferencedTypeName": "T-INTEGER", "Min": "0", "Max": "255"
                }
            }, "y": {
                "Optional": "False", "Line": 13, "CharPositionInLine": 1, "type": {
                    "Line": 13, "CharPositionInLine": 3, "Kind": "SequenceType", "Children": {
                        "a": {
                            "Optional": "False", "Line": 13, "CharPositionInLine": 14, "type": {
                                "Line": 13, "CharPositionInLine": 16, "Kind": "BooleanType"
                            }
                        }, "b": {
                            "Optional": "False", "Line": 13, "CharPositionInLine": 25, "type": {
                                "Line": 13, "CharPositionInLine": 27, "Kind": "SequenceOfType", "Min": "3", "Max": "3", "type": {
                                    "Line": 13, "CharPositionInLine": 49, "Kind": "BooleanType"
                                }
                            }
                        }
                    }
                }
            }, "z": {
                "Optional": "False", "Line": 14, "CharPositionInLine": 2, "type": {
                    "Line": 14, "CharPositionInLine": 4, "Kind": "ReferenceType", "ReferencedTypeName": "T-SEQ"
                }
            }
        }
    }
}
