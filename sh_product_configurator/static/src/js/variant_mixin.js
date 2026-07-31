odoo.define('sale_product_configurator.VariantMixin', function (require) {'use strict';

var VariantMixin = require('sale.VariantMixin');
const ajax = require('web.ajax');


VariantMixin.updateProduct = function ($container,shProductId, productId, productTemplateId, useAjax) {
        ;
        productId = parseInt(productId);
        productTemplateId = parseInt(productTemplateId);
        var productReady = Promise.resolve();
//        if (productId) {
//            productReady = Promise.resolve(productId);
//        } else {
        var params = {
            sh_product_id: shProductId,
            product_template_id: productTemplateId,
            product_template_attribute_value_ids:JSON.stringify(VariantMixin.getSelectedVariantValues($container)),
        };

        var route = '/update_product_variant';
        if (useAjax) {
            productReady = ajax.jsonRpc(route, 'call', params);
        } else if (Boolean(this._rpc)) {
            // HACK to combine owl and non owl calls
            productReady = this._rpc({route: route, params: params});
        } else {
            productReady = this.rpc(route, params);
        }
//        }

        return productReady;
    };


VariantMixin.shSelectOrCreateProduct = function ($container, productId, productTemplateId, useAjax) {
        ;
        productId = parseInt(productId);
        productTemplateId = parseInt(productTemplateId);
        var productReady = Promise.resolve();
        /*if (productId) {
            productReady = Promise.resolve(productId);
        } else {*/
        var params = {
            product_template_id: productTemplateId,
            product_template_attribute_value_ids:
                JSON.stringify(VariantMixin.getSelectedVariantValues($container)),
        };

        var route = '/sale/create_product_variant';
        if (useAjax) {
            productReady = ajax.jsonRpc(route, 'call', params);
        } else if (Boolean(this._rpc)) {
            // HACK to combine owl and non owl calls
            productReady = this._rpc({route: route, params: params});
        } else {
            productReady = this.rpc(route, params);
        }
        /*}*/

        return productReady;
    };





return VariantMixin;

});
