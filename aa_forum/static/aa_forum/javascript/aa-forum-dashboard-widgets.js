/* global aaForumDashboardWidgetsOverride, bootstrap, deepMerge */

/* jshint -W097 */
'use strict';

const aaForumDashboardWidgetsDefaults = {
    wrapper: {
        element: document.getElementById('aa-forum-dashboard-widgets')
    },
    widget: {
        unreadTopics: {
            element: document.getElementById('aa-forum-dashboard-widget-unread-topics'),
            contentElementClass: 'aa-forum-dashboard-widget-unread-topics-content'
        }
    }
};

/**
 * Forum dashboard widgets settings.
 *
 * @type {Object}
 */
let aaForumDashboardWidgetsSettings = aaForumDashboardWidgetsDefaults; // eslint-disable-line no-unused-vars
if (typeof aaForumDashboardWidgetsOverride !== 'undefined') {
    aaForumDashboardWidgetsSettings = deepMerge( // eslint-disable-line no-unused-vars
        aaForumDashboardWidgetsDefaults,
        aaForumDashboardWidgetsOverride
    );
}

/**
 * Check if the unread topics widget element exists.
 */
if (aaForumDashboardWidgetsSettings.widget.unreadTopics.element !== null) {
    const aaForumUnreadTopicsWidgetContent = aaForumDashboardWidgetsSettings.widget.unreadTopics.element.querySelector(
        `.${aaForumDashboardWidgetsSettings.widget.unreadTopics.contentElementClass}`
    );

    /**
     * Fetch the unread topics widget content via AJAX.
     */
    fetch(aaForumDashboardWidgetsSettings.widget.unreadTopics.url.ajax)
        .then((response) => {
            if (response.ok) {
                return response.text();
            }

            throw new Error('Something went wrong');
        })
        .then((responseText) => {
            if (responseText !== '') {
                aaForumUnreadTopicsWidgetContent.innerHTML = responseText;

                // Show the widget area
                const showWidgetArea = new bootstrap.Collapse(aaForumDashboardWidgetsSettings.wrapper.element, { // eslint-disable-line no-unused-vars
                    show: true
                });

                // Show the widget
                const showWidget = new bootstrap.Collapse(aaForumDashboardWidgetsSettings.widget.unreadTopics.element, { // eslint-disable-line no-unused-vars
                    show: true
                });

                // Initialize Bootstrap tooltips
                [].slice.call(document.querySelectorAll('[data-bs-tooltip="aa-forum"]'))
                    .map((tooltipTriggerEl) => {
                        return new bootstrap.Tooltip(tooltipTriggerEl);
                    });
            }
        })
        .catch((error) => {
            console.log(error);
        });
}
