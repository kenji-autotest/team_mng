# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    ttype = fields.Selection(selection_add=[('encrypted', 'encrypted')])
    encryption_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Encryption Field',
        ondelete='cascade',
        domain="[('ttype','=','encrypted')]",
        help="If set, this field will be stored encrypted in encryption field,"
             "instead of having its own database column. "
             "This cannot be changed after creation.",
    )

    @api.multi
    def write(self, vals):
        def changing_storing_sys(f):
            if 'encryption_field_id' in vals:
                if f.encryption_field_id.id != vals['encryption_field_id']:
                    return True
            return False

        # Limitation: renaming a encrypt field or changing the storing system
        # is currently not allowed
        if 'encryption_field_id' in vals or 'name' in vals:
            for field in self:
                if changing_storing_sys(field):
                    raise UserError(_(
                        'Changing the storing system for field '
                        '"%s" is not allowed.'
                    ) % field.name)

                if field.encryption_field_id and (field.name != vals['name']):
                    raise UserError(_(
                        'Renaming encrypt field "%s" is not allowed'
                    ) % field.name)

        return super(IrModelFields, self).write(vals)

    def _reflect_field_params(self, field):
        params = super(IrModelFields, self)._reflect_field_params(field)

        params['encryption_field_id'] = None
        if getattr(field, 'encrypt', None):
            model = self.env[field.model_name]
            encryption_field = model._fields.get(field.encrypt)
            if encryption_field is None:
                raise UserError(_(
                    "Encryption field `%s` not found for encrypt"
                    "field `%s`!") % (field.encrypt, field.name))
            encryption_record = self._reflect_field(encryption_field)
            params['encryption_field_id'] = encryption_record.id

        return params

    def _instanciate_attrs(self, field_data):
        attrs = super(IrModelFields, self)._instanciate_attrs(field_data)
        if field_data.get('encryption_field_id'):
            encryption_record = self.browse(field_data['encryption_field_id'])
            attrs['encrypt'] = encryption_record.name
        return attrs


class TestEncrypted(models.TransientModel):
    _name = 'encrypted_fields.test'

    encrypted = fields.Encrypted()
    encrypted_password = fields.Encrypted()
    boolean = fields.Boolean(encrypt='encrypted')
    integer = fields.Integer(encrypt='encrypted')
    float = fields.Float(encrypt='encrypted')
    char = fields.Char(encrypt='encrypted')
    password = fields.Char(encrypt='encrypted_password')
    selection = fields.Selection(
        selection=[('one', 'One'), ('two', 'Two')],
        encrypt='encrypted'
    )
    html = fields.Html(encrypt='encrypted')
    partner = fields.Many2one('res.partner', encrypt='encrypted')
