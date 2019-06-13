# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, exceptions


class IFIGoal(models.Model):
    _inherit = 'gamification.goal'

    @api.depends('current', 'target_goal', 'definition_id.condition')
    def _get_completion(self):
        """Return the percentage of completeness of the goal, between 0 and 100"""
        for goal in self:
            if not goal.target_goal or goal.target_goal == 0:
                goal.completeness = 100.0
            else:
                if goal.definition_condition == 'higher':
                    if goal.current >= goal.target_goal:
                        goal.completeness = 100.0
                    else:
                        goal.completeness = round(100.0 * goal.current / goal.target_goal, 2)
                elif goal.current < goal.target_goal:
                    # a goal 'lower than' has only two values possible: 0 or 100%
                    goal.completeness = 100.0
                else:
                    goal.completeness = 0.0