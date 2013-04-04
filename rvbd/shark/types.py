# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""This file includes all the types that are exposed to the user during
script creation
"""

__all__=['Operation', 'Key', 'Value']

class Operation(object):
    """Enumeration of the possible operations that can be performed on a fields.
    """
    sum = 'SUM'
    avg = 'AVG'
    timeavg = 'TIME_AVG'
    max = 'MAX'
    min = 'MIN'
    none = 'NONE'
    
               
class Field(object):
    def __init__(self, field, operation=Operation.sum, autogen=False,
                 key=False, description=None, default_value=None):

        #do str(field) because field can be a Field instance itself.
        field_string = str(field).replace('::', '.')
        self.field = field
        self.field_string = field_string
        self.operation = operation
        self.autogen = autogen
        self.key = key
        self.description = description
        self.default_value = default_value
            
    def __str__(self):
        return self.field_string
    
class Key(Field):
    """This class can be used to identify a fields as a key in a view
    """
    def __init__(self, field, description=None, default_value=None):
        super(Key, self).__init__(field, key=True, operation=Operation.none,
                                  description=description, default_value=default_value)
        
class Value(Field):
    """This class can be used to identify a fields as a value in a view
    """
    def __init__(self, field, operation=Operation.sum, description=None, default_value=None):
        super(Value, self).__init__(field, operation=operation,
                                    description=description, default_value=default_value)
