# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pytz
import re
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IFIAttendanceLeave(models.Model):

    _inherit = "hr.leave"

    @api.multi
    def write(self, vals):
        res = super(IFIAttendanceLeave, self).write(vals)
        if vals.get('state', False):
            for r in self:
                if r.state not in ['cancel', 'refuse']:
                    attendance = self.env['hr.attendance'].search([('check_in', '<', r.request_date_to),
                                                                   ('check_out', '>', r.request_date_from)])
                    if attendance:
                        attendance.unlink()
        return res

