/* global bootstrap */

[].slice.call(document.querySelectorAll('[data-bs-tooltip="aa-forum"]'))
    .map((tooltipTriggerEl) => {
        'use strict';

        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
