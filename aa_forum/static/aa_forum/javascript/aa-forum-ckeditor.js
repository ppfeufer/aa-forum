$(document).ready(() => {
    'use strict';

    $('form').on('reset', (e) => {
        const domEditableElement = document.querySelector(`#${$(e.target).attr('id')} .ck-editor__editable`);
        const editorInstance = domEditableElement.ckeditorInstance;

        editorInstance.setData('');
    });
});
