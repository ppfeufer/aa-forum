/* global CKEDITOR */

$(function() {
    'use strict';

    if (typeof CKEDITOR !== 'undefined') {
        $('form').on('reset', function(e) {
            if ($(CKEDITOR.instances).length) {
                for (let key in CKEDITOR.instances) {
                    let instance = CKEDITOR.instances[key];

                    if ($(instance.element.$).closest('form').attr('name') === $(e.target).attr('name')) {
                        instance.setData(instance.element.$.defaultValue);
                    }
                }
            }
        });
    }
});
