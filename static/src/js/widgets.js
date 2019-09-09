odoo.define('my_field_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var fieldRegistry = require('web.field_registry');

var colorField = AbstractField.extend({
    className: 'o_video_preview',
    tagName: 'span',
    supportedFieldTypes: ['char'],
    events: {

    },
    init: function () {
        this._super.apply(this, arguments);
    },
    _renderEdit: function () {
		this.$el.empty();

    },
    _renderReadonly: function () {
		this.$el.append($('<video>', {
			'src':this.value, 
			'type':'video/mp4',
			'controls': true,
		}));

    },


});

fieldRegistry.add('video_preview', colorField);

return {
    colorField: colorField,
};
});
	