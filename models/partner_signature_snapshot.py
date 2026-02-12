from odoo import models, fields, api

class PartnerSignatureSnapshot(models.Model):
    _name = 'partner.signature.snapshot'
    _description = 'Partner Signature Statistics Snapshot'
    _order = 'snapshot_date desc, partner_id'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade', index=True)
    snapshot_date = fields.Date(string='Snapshot Date', required=True, default=fields.Date.context_today, index=True)
    
    # Snapshot of computed fields (for reporting)
    signature_transaction_count = fields.Integer(string='Signature Count (All Time)')
    signature_transaction_count_this_year = fields.Integer(string='Signature Count This Year')
    client_count = fields.Integer(string='Number of Clients')
    current_transaction_price = fields.Float(string='Current Transaction Price', digits=(10, 4))
    paid_transactions_this_year = fields.Float(string='Paid Transactions This Year', digits=(10, 2))
    overpaid = fields.Float(string='Overpaid', digits=(10, 2))
    pending_transactions = fields.Integer(string='Pending Transactions')
    forecast_transaction_price = fields.Float(string='Forecast Transaction Price', digits=(10, 4))
    
    # Partner info (denormalized for easier reporting)
    partner_name = fields.Char(string='Partner Name', related='partner_id.name', store=True)
    is_partner = fields.Boolean(string='Is Partner', related='partner_id.is_partner', store=True)
    partnership_status = fields.Selection(related='partner_id.partnership_status', store=True)
    
    _sql_constraints = [
        ('unique_partner_date', 'UNIQUE(partner_id, snapshot_date)', 
         'Only one snapshot per partner per date is allowed!')
    ]
    
    @api.model
    def create_snapshots(self):
        """
        Create/update snapshots for all partners.
        This method is called by the scheduled action.
        """
        today = fields.Date.context_today(self)
        partners = self.env['res.partner'].search([('is_partner', '=', True)])
        
        for partner in partners:
            # Check if snapshot already exists for today
            existing = self.search([
                ('partner_id', '=', partner.id),
                ('snapshot_date', '=', today)
            ], limit=1)
            
            snapshot_vals = {
                'partner_id': partner.id,
                'snapshot_date': today,
                'signature_transaction_count': partner.signature_transaction_count,
                'signature_transaction_count_this_year': partner.signature_transaction_count_this_year,
                'client_count': partner.client_count,
                'current_transaction_price': partner.current_transaction_price,
                'paid_transactions_this_year': partner.paid_transactions_this_year,
                'overpaid': partner.overpaid,
                'pending_transactions': partner.pending_transactions,
                'forecast_transaction_price': partner.forecast_transaction_price,
            }
            
            if existing:
                existing.write(snapshot_vals)
            else:
                self.create(snapshot_vals)
        
        return True
    
    def action_update_all_snapshots(self):
        """
        Button action to manually trigger snapshot creation for all partners.
        Shows a notification when complete.
        """
        self.create_snapshots()
        
        # Return notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Partner snapshots have been updated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

