/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";

patch(ListRenderer.prototype, "sh_product_configurator.ListRenderer", {
    /**
     * @override
     */
    isSortable(column) {
        if (this.props.list.resModel === 'product.template.attribute.line' && column.name === 'attribute_id') {
            return false;
        }
        return this._super(column);
    }
});
