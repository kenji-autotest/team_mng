# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import json
import logging

from odoo import fields
from odoo.tools import config

_logger = logging.getLogger(__name__)
try:
    from cryptography.fernet import Fernet
except (ImportError, IOError) as err:
    _logger.debug(err)

if config.get('encryption_key', False):
    encryption_key = config['encryption_key'].encode()
else:
    _logger.warning("encryption_key is not set in configuration parameters."
                    "Using default key! This is not secure!")
    encryption_key = "uumO_L_e_PI6seDtKGoqr7LANf-ozaZxwf0ziki2_nw=".encode()
fernet = Fernet(encryption_key)


def monkey_patch(cls):
    """ Return a method decorator to monkey-patch the given class. """

    def decorate(func):
        name = func.__name__
        func.super = getattr(cls, name, None)
        setattr(cls, name, func)
        return func

    return decorate


#
# Implement encrypt fields by monkey-patching fields.Field
#

fields.Field.__doc__ += """

        .. _field-encrypted:

        .. rubric:: Encrypted fields

        ...

        :param encrypt: the name of the field where encrypted the value of this
         field must be stored.
"""


@monkey_patch(fields.Field)
def _get_attrs(self, model, name):
    attrs = _get_attrs.super(self, model, name)
    if attrs.get('encrypt'):
        # by default, encrypt fields are not stored and not copied
        attrs['store'] = False
        attrs['copy'] = attrs.get('copy', False)
        attrs['compute'] = self._compute_encrypt
        if not attrs.get('readonly'):
            attrs['inverse'] = self._inverse_encrypt
    return attrs


@monkey_patch(fields.Field)
def _compute_encrypt(self, records):
    for record in records:
        values = record[self.encrypt] or {}
        record[self.name] = values.get(self.name)
    if self.relational:
        for record in records:
            record[self.name] = record[self.name].exists()


@monkey_patch(fields.Field)
def _inverse_encrypt(self, records):
    for record in records:
        values = record[self.encrypt] or {}
        value = self.convert_to_read(
            record[self.name], record,
            use_name_get=False
        )
        if value:
            if values.get(self.name) != value:
                values[self.name] = value
                record[self.encrypt] = values
        else:
            if self.name in values:
                values.pop(self.name)
                record[self.encrypt] = values


#
# Definition and implementation of encrypted fields
#

class Encrypted(fields.Field):
    """ Encrypted fields provide the storage for encrypt fields. """
    type = 'encrypted'
    _slots = {
        'prefetch': False,  # not prefetched by default
    }
    column_type = ('bytea', 'bytea')

    def convert_to_column(self, value, record, values=None):
        return fernet.encrypt(json.dumps(value).encode())

    def convert_to_cache(self, value, record, validate=True):
        # cache format: dict
        value = value or {}
        return value if isinstance(value, dict) else \
            json.loads(fernet.decrypt(bytes(value)).decode())


fields.Encrypted = Encrypted
