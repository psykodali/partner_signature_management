from odoo import models, fields

class PartnerPartnershipType(models.Model):
    _name = 'partner.partnership.type'
    _description = 'Partner Partnership Type'
    _order = 'sequence, id'

    name = fields.Char(string='Type Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)
