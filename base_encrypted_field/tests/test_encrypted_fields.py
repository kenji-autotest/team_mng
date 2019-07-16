# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests import common
from cryptography.fernet import Fernet

from ..models.fields import encryption_key

fernet = Fernet(encryption_key)


class TestSparseFields(common.TransactionCase):

    def test_encrypt(self):
        """ test encrypt fields. """
        record = self.env['encrypted_fields.test'].create({})
        self.assertFalse(record.encrypted)
        self.assertFalse(record.encrypted_password)

        partner = self.env.ref('base.main_partner')
        values = [
            ('boolean', True),
            ('integer', 42),
            ('float', 3.14),
            ('char', 'John'),
            ('selection', 'two'),
            ('html', '<p>Hello World!</p>'),
            ('partner', partner.id),
            ('password', 'mystrongpass'),
        ]
        for n, (key, val) in enumerate(values[:-1]):
            record.write({key: val})
            self.assertEqual(record.encrypted, dict(values[:n + 1]))
        record.write(dict([values[-1]]))
        self.assertEqual(record.encrypted_password, dict([values[-1]]))

        for key, val in values[:-2]:
            self.assertEqual(record[key], val)
        self.assertEqual(record.partner, partner)

        for n, (key, val) in enumerate(values[:-1]):
            record.write({key: False})
            self.assertEqual(record.encrypted, dict(values[:-1][n + 1:]))
        record.write({values[-1][0]: False})
        self.assertEqual(record.encrypted_password, {})

        # check reflection of encrypt fields in 'ir.model.fields'
        names = [name for name, _ in values[:-1]]
        domain = [
            ('model', '=', 'encrypted_fields.test'),
            ('name', 'in', names)
        ]
        fields = self.env['ir.model.fields'].search(domain)
        self.assertEqual(len(fields), len(names))
        for field in fields:
            if "serialization_field_id" in field:
                self.assertEqual(
                    field.serialization_field_id.name,
                    'encrypted'
                )
