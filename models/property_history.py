from odoo import models, fields


class PropertyHistory(models.Model):
    _name = 'property.history'
    _description = 'Property History Model'

    user_id = fields.Many2one('res.users')
    property_id = fields.Many2one('property')
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()