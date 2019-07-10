# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pytz
import re
import time
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC
from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _


class IFIAttendanceLeave(models.Model):

    _inherit = "hr.leave"

    @api.multi
    def write(self, vals):
        res = super(IFIAttendanceLeave, self).write(vals)
        if vals.get('state', False):
            for r in self:
                if r.state not in ['cancel', 'refuse']:
                    attendance = self.env['hr.attendance'].search([('check_in', '<', r.date_to),
                                                                   ('check_out', '>', r.date_from)])
                    if attendance:
                        attendance.unlink()
        return res

