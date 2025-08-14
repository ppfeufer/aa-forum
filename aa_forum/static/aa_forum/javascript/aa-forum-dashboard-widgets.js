/* global aaForumDashboardWidgetsOverride, bootstrap, objectDeepMerge, fetchGet */

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
let aaForumDashboardWidgetsSettings = aaForumDashboardWidgetsDefaults;

if (typeof aaForumDashboardWidgetsOverride !== 'undefined') {
    aaForumDashboardWidgetsSettings = objectDeepMerge(
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
    fetchGet({
        url: aaForumDashboardWidgetsSettings.widget.unreadTopics.url.ajax,
        responseIsJson: false
    })
        .then((data) => {
            if (data !== '') {
                aaForumUnreadTopicsWidgetContent.innerHTML = data;

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
            console.error(error);
        });
}
