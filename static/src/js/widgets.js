odoo.define('my_field_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var fieldRegistry = require('web.field_registry');
var basicFields = require('web.basic_fields');
var FieldChar = basicFields.FieldChar;

var colorField = FieldChar.extend({
    className: 'o_video_preview',
    tagName: 'span',
    supportedFieldTypes: ['char'],
	events: {
		'click .video': 'clickVideo',
	},

    init: function () {
        this._super.apply(this, arguments);
    },

    _renderReadonly: function () {
		this.$el.empty();
		this.$el.append($('<video>', {
			'src':this.value, 
			'type':'video/mp4',
			'controls': true,
		}));

    },

	clickVideo: function(ev) {

	},
});

fieldRegistry.add('video_preview', colorField);

return {
    colorField: colorField,
};
});
	