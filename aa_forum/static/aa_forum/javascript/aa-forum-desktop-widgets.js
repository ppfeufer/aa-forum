/* global aaForumDashboardWidgetsSettings, bootstrap */

'use strict';

/**
 * Performs a deep merge of objects and returns a new object.
 * Does not modify objects (immutable) and merge arrays via concatenation.
 *
 * @param {...object} objects - Objects to merge
 * @returns {object} New object with merged key/values
 */
const mergeOptions = (...objects) => {
    const isObject = obj => obj && typeof obj === 'object';

    return objects.reduce((prev, obj) => {
        Object.keys(obj).forEach(key => {
            const pVal = prev[key];
            const oVal = obj[key];

            if (Array.isArray(pVal) && Array.isArray(oVal)) {
                // prev[key] = pVal.concat(...oVal);
                prev[key] = [...new Set([...oVal, ...pVal])];
            } else if (isObject(pVal) && isObject(oVal)) {
                prev[key] = mergeOptions(pVal, oVal);
            } else {
                prev[key] = oVal;
            }
        });

        return prev;
    }, {});
};

const aaForumDashboardWidgetsDefaults = {
    wrapper: {
        element: document.getElementById('aa-forum-dashboard-widgets')
    },
    unreadTopicsWidget: {
        element: document.getElementById('aa-forum-dashboard-widget-unread-topics'),
        contentElementClass: 'aa-forum-dashboard-widget-unread-topics-content'
    },
};

/**
 * Forum dashboard widgets settings.
 *
 * @type {Object}
 */
const aaForumDashboardWidgets = mergeOptions(
    aaForumDashboardWidgetsDefaults,
    aaForumDashboardWidgetsSettings
);

/**
 * Check if the unread topics widget element exists.
 */
if (aaForumDashboardWidgets.unreadTopicsWidget.element !== null) {
    const aaForumUnreadTopicsWidgetContent = aaForumDashboardWidgets.unreadTopicsWidget.element.querySelector(
        `.${aaForumDashboardWidgets.unreadTopicsWidget.contentElementClass}`
    );

    /**
     * Fetch the unread topics widget content via AJAX.
     */
    fetch(aaForumDashboardWidgetsSettings.unreadTopicsWidget.ajaxUrl)
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
                const showWidgetArea = new bootstrap.Collapse(aaForumDashboardWidgets.wrapper.element, { // eslint-disable-line no-unused-vars
                    show: true
                });

                // Show the widget
                const showWidget = new bootstrap.Collapse(aaForumDashboardWidgets.unreadTopicsWidget.element, { // eslint-disable-line no-unused-vars
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
