odoo.define('clickable_tags_widget', function (require) {
"use strict";

var RelFields = require('web.relational_fields');
var fieldRegistry = require('web.field_registry');

var clickableTags = RelFields.FieldMany2ManyTags.extend({
    tag_template: "ClickableTag",

    events: _.extend({}, RelFields.FieldMany2ManyTags.prototype.events, {
        "click span.o_badge_text": "open_element",
        //"click div.badge_pill": "open_element",
    }),

    init: function() {
        this._super.apply(this, arguments);
        this.help_title = this.nodeOptions.help_title;
    },
    open_element: function(event){
        if (!$(event.target).prop('special_click')) {
            var id = $(event.currentTarget).parent().data('id');
            //var id = $(event.currentTarget).data('id');
            if (id) {
                //this.trigger_up('open_record', { id: id, target: event.target });
                var action = {
                    'type': 'ir.actions.act_window',
                    'res_model': this.field.relation,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': id,
                    'target': 'current',
                };
                this.do_action(action);
            }
        }
    },
});

fieldRegistry.add('clickable_tags', clickableTags);

return {
    clickableTags: clickableTags,
};
});