Just type into any related field, such as Customer on a Sale Order.

Smart search widens fuzzy searches only (operators `ilike` and `like`).
Exact lookups (`=`, `=ilike`, ...) keep Odoo's own matching, and so does
import, which resolves related records by name: a value that is one record's
name and another record's phone or city links the named record. To turn smart
search off for a call, pass `name_search_extended=False` in the context.
