# Copyright 2026 Bemade Inc. (https://www.bemade.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged

IR_MODEL = "odoo.addons.base_name_search_improved.models.ir_model"


@tagged("post_install", "-at_install")
class ExactLookupCase(TransactionCase):
    """Smart search widens fuzzy searches only.

    An exact lookup -- operator ``=``, as Odoo's import resolves a related
    record by name -- must keep Odoo's own matching, or a value that is one
    record's name and another's phone, city or zip resolves to the wrong one.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        model_partner = cls.env.ref("base.model_res_partner")
        model_partner.name_search_ids = cls.env.ref("base.field_res_partner__phone")
        model_partner.use_smart_name_search = True
        cls.Partner = cls.env["res.partner"]
        cls.named = cls.Partner.create({"name": "555 0199", "is_company": True})
        cls.phoned = cls.Partner.create(
            {"name": "Phone Owner", "phone": "555 0199", "is_company": True}
        )
        cls.phone_only = cls.Partner.create(
            {"name": "Other Owner", "phone": "555 0142", "is_company": True}
        )

    def _ids(self, *args, **kwargs):
        return [pid for pid, _name in self.Partner.name_search(*args, **kwargs)]

    def test_fuzzy_operators_use_smart_search(self):
        self.assertIn(self.phone_only.id, self._ids("555 0142"))
        self.assertIn(self.phone_only.id, self._ids("555 0142", operator="like"))

    def test_exact_operators_keep_odoo_matching(self):
        for operator in ("=", "=ilike", "=like"):
            self.assertEqual(self._ids("555 0199", operator=operator), [self.named.id])
            self.assertEqual(self._ids("555 0142", operator=operator), [])

    def test_context_switches_smart_search_off(self):
        plain = self.Partner.with_context(name_search_extended=False)
        self.assertEqual(plain.name_search("555 0142"), [])

    def test_import_links_the_named_record(self):
        result = self.Partner.load(
            ["name", "parent_id"], [["Imported Person", "555 0199"]]
        )
        self.assertFalse(result["messages"], "no 'multiple matches' warning")
        self.assertEqual(self.Partner.browse(result["ids"]).parent_id, self.named)

    def test_import_never_matches_smart_fields(self):
        # Import resolves names without smart search, whatever operator it
        # uses: widen the allowed operators to '=' to take that guard away.
        with patch(f"{IR_MODEL}.ALLOWED_OPS", {"ilike", "like", "="}):
            self.assertIn(self.phone_only.id, self._ids("555 0142", operator="="))
            result = self.Partner.load(
                ["name", "parent_id"], [["Imported Person", "555 0142"]]
            )
        self.assertFalse(result["ids"], "a phone number is not a partner name")
        self.assertTrue(result["messages"])


@tagged("post_install", "-at_install")
class SmartSearchOrderCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        model_partner = cls.env.ref("base.model_res_partner")
        model_partner.name_search_ids = cls.env.ref("base.field_res_partner__phone")
        model_partner.use_smart_name_search = True
        cls.Partner = cls.env["res.partner"]
        # Created in reverse of the model's order (by name).
        cls.zed = cls.Partner.create({"name": "Zed Ordering", "phone": "777 0101"})
        cls.abe = cls.Partner.create({"name": "Abe Ordering", "phone": "777 0102"})

    def test_smart_results_keep_model_order(self):
        """Matches found only by smart search follow the model's order, so a
        limit keeps the first ones, not whichever the database returns."""
        self.assertEqual(
            [pid for pid, _n in self.Partner.name_search("777 010", limit=1)],
            [self.abe.id],
        )
        self.assertEqual(
            [pid for pid, _n in self.Partner.name_search("777 010")],
            [self.abe.id, self.zed.id],
        )
