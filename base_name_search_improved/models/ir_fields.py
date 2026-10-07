# Copyright 2026 Bemade Inc. (https://www.bemade.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrFieldsConverter(models.AbstractModel):
    _inherit = "ir.fields.converter"

    def db_id_for(self, model, field, subfield, value, savepoint):
        """Import resolves related records by their name, never by smart
        search fields, whatever operator core uses for the lookup."""
        converter = self.with_context(name_search_extended=False)
        return super(IrFieldsConverter, converter).db_id_for(
            model, field, subfield, value, savepoint
        )
