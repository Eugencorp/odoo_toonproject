var oldList = require('web.ListView.List');
var newList = oldList.extend({
        row_clicked: function (e, view) {
			if( this.view.is_action_enabled('open') )
				this._super.apply(this, arguments);
		},
    });
var fieldRegistry = require('web.field_registry');
fieldRegistry.add('toonproject.newList', newList);
