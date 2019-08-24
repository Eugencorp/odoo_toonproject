/**/
odoo.define('my_field_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var fieldRegistry = require('web.field_registry');

var colorField = AbstractField.extend({
    className: 'o_int_colorpicker',
    tagName: 'span',
    supportedFieldTypes: ['integer'],

    init: function () {
        this._super.apply(this, arguments);
    },
    _renderEdit: function () {
        this.$el.empty();
        this.evalTwick();

    },
    _renderReadonly: function () {
        this.evalTwick();
    },
    evalTwick: function(){
        //alert('Alert!');
        $('.no_open .o_data_row td').click(function(evt){evt.stopPropagation();});
    },

});

fieldRegistry.add('int_color', colorField);

return {
    colorField: colorField,
};
});
