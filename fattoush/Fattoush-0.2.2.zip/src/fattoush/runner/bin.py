#!/usr/bin/env python
# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
This script uses fattoush to run lettuce
"""


def console():
    from fattoush.config import FattoushConfigGroup
    FattoushConfigGroup.from_cli_args().run()


if __name__ == '__main__':
    console()