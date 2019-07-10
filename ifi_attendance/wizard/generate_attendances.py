# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError, ValidationError


class GenerateAppraisals(models.TransientModel):
    _name = 'generate.attendance.batches'
    _description = 'Generate Attendances'

    date_from = fields.Datetime(required=True, default=fields.Datetime.now())
    date_to = fields.Datetime(required=True, default=fields.Datetime.now())

    @api.multi
    @api.constrains('expired_date', 'review_expired_date', 'date')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('Date To must greater than Date From'))

    @api.multi
    def action_generate_attendance(self):
        date_from = fields.Datetime.from_string(self.date_from)
        date_to = fields.Datetime.from_string(self.date_to)
        delta = date_to - date_from
        for d in range(delta.days + 1):
            date = date_from + timedelta(days=d)
            self.env['hr.attendance'].daily_auto_checkin(date)
