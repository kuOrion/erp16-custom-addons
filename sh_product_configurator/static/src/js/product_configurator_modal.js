odoo.define('website_sale_product_configurator.OptionalProductsModal', function (require) {
    "use strict";

const { OptionalProductsModal } = require('@sale_product_configurator/js/product_configurator_modal');
const ajax = require('web.ajax');

OptionalProductsModal.include({

    willStart: async function () {
        
        // ✅ Custom condition check
        var parentInit =  await this._super.apply(this, arguments);

        if(localStorage.getItem('sh_active_model') == 'product.product'){
                var self = this;
                ;
                var uri = this._getUri("/sale_product_configurator/show_advanced_configurator");
                var getModalContent = ajax.jsonRpc(uri, 'call', {
                    mode: self.mode,
                    product_id: self.rootProduct.product_id,
                    variant_values: self.rootProduct.variant_values,
                    product_custom_attribute_values: self.rootProduct.product_custom_attribute_values,
                    pricelist_id: self.pricelistId || false,
                    add_qty: self.rootProduct.quantity,
                    force_dialog: self.forceDialog,
                    no_attribute: self.rootProduct.no_variant_attribute_values,
                    custom_attribute: self.rootProduct.product_custom_attribute_values,
                    context: _.extend({'quantity': self.rootProduct.quantity}, this.context),
                    sh_active_model: localStorage.getItem('sh_active_model'),
                })
                .then(function (modalContent) {
                    if (modalContent) {
                        var $modalContent = $(modalContent);

                        $modalContent.find('input[type="radio"]:checked').prop('checked', false);
                        $modalContent.find('option:selected').prop('selected', false);

                        $modalContent = self._postProcessContent($modalContent);
                        self.$content = $modalContent;
                    } else {
                        self.trigger('options_empty');
                        self.preventOpening = true;
                    }
                });

                localStorage.removeItem('sh_active_model');
                return Promise.all([getModalContent, parentInit]);
        }
        else{
            // 🔁 Fallback to original willStart if condition not met
            return parentInit
        }

    },


    shGetAndCreateSelectedProducts: async function (sh_product_id) {
        ;
        var self = this;
        const products = [];
        let productCustomVariantValues;
        let noVariantAttributeValues;
        ;
        for (const product of self.$modal.find('.js_product.in_cart')) {
            var $item = $(product);
            var quantity = parseFloat($item.find('input[name="add_qty"]').val().replace(',', '.') || 1);
            var parentUniqueId = product.dataset.parentUniqueId;
            var uniqueId = product.dataset.uniqueId;
            productCustomVariantValues = $item.find('.custom-attribute-info').data("attribute-value") || self.getCustomVariantValues($item);
            noVariantAttributeValues = $item.find('.no-attribute-info').data("attribute-value") || self.getNoVariantAttributeValues($item);

            const productID = await self.updateProduct(
                $item,
                sh_product_id,
                parseInt($item.find('input.product_id').val(), 10),
                parseInt($item.find('input.product_template_id').val(), 10),
                true
            );
            products.push({
                'product_id': productID,
                'product_template_id': parseInt($item.find('input.product_template_id').val(), 10),
                'quantity': quantity,
                'parent_unique_id': parentUniqueId,
                'unique_id': uniqueId,
                'product_custom_attribute_values': productCustomVariantValues,
                'no_variant_attribute_values': noVariantAttributeValues
            });
        }
        return products;
    },

    _onModalReady: function () {
        var self = this;

        // Use setTimeout to ensure DOM is ready
        setTimeout(function() {
            const attributeParentMapEl = self.$modal.find('#attribute_parent_map');
            if (!attributeParentMapEl.length) {
                console.warn("Attribute parent map not found in modal.");
                return;
            }
            const attributeParentMap = JSON.parse(attributeParentMapEl.val());

            const $attributeGroups = self.$modal.find('.variant_attribute');

            // Helper function to recursively hide children and their descendants
            function hideChildren(attributeId) {
                Object.keys(attributeParentMap).forEach(childAttrId => {
                    if (attributeParentMap[childAttrId].parent_attribute_id === attributeId) {
                        const $childGroup = self.$modal.find(`.variant_attribute[data-attribute_id="${childAttrId}"]`);
                        if ($childGroup.is(':visible')) {
                            $childGroup.hide();
                            $childGroup.find('input[type="radio"]:checked, select').prop('checked', false);
                            // Recursively hide grandchildren
                            hideChildren(parseInt(childAttrId));
                        }
                    }
                });
            }

            // Helper function to show direct children that match the selected parent value
            function showChildren(attributeId, valueId) {
                Object.keys(attributeParentMap).forEach(childAttrId => {
                    if (attributeParentMap[childAttrId].parent_attribute_id === attributeId &&
                        attributeParentMap[childAttrId].parent_value_id === valueId) {
                        self.$modal.find(`.variant_attribute[data-attribute_id="${childAttrId}"]`).show();
                        // If this child has a pre-selected value, recursively show its children
                        const $selectedInputOfChild = self.$modal.find(`.variant_attribute[data-attribute_id="${childAttrId}"]`).find('input[type="radio"]:checked, select option:selected');
                        if ($selectedInputOfChild.length && $selectedInputOfChild.val()) {
                            const selectedValueIdOfChild = parseInt($selectedInputOfChild.val());
                            showChildren(parseInt(childAttrId), selectedValueIdOfChild);
                        }
                    }
                });
            }

            // Initially hide all child attributes
            $attributeGroups.each(function () {
                const $this = $(this);
                const attributeId = parseInt($this.data('attribute_id'));
                if (attributeParentMap[attributeId]) {
                    $this.hide();
                }
            });

            // On initial load, check selected parents and show their children
            $attributeGroups.each(function () {
                const $this = $(this);
                const attributeId = parseInt($this.data('attribute_id'));
                const isParent = Object.values(attributeParentMap).some(parentInfo => parentInfo.parent_attribute_id === attributeId);

                if (isParent) {
                    const $selectedInput = $this.find('input[type="radio"]:checked, select option:selected');
                    if ($selectedInput.length && $selectedInput.val()) {
                        const selectedValueId = parseInt($selectedInput.val());
                        showChildren(attributeId, selectedValueId);
                    }
                }
            });

            // Add change listener to all attribute value inputs
            self.$modal.on('change', 'input[type="radio"][name^="ptal-"], select[name^="ptal-"]', function () {
                const $changedInput = $(this);
                const $attributeGroup = $changedInput.closest('.variant_attribute');
                const selectedAttributeId = parseInt($attributeGroup.data('attribute_id'));
                const selectedValueId = parseInt($changedInput.val());

                // First, hide all children and their descendants of the changed attribute
                hideChildren(selectedAttributeId);

                // Then, show only the relevant children and their descendants for the newly selected value
                if ($changedInput.is(':checked') || $changedInput.is('select')) {
                    showChildren(selectedAttributeId, selectedValueId);
                }
            });
        }, 100); // 100ms delay
    },

});

});
