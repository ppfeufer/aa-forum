/* global aaForumDashboardWidgetsSettings, bootstrap */

'use strict';

const aaForumDashboardWidgets = document.getElementById('aa-forum-dashboard-widgets');
const aaForumUnreadTopicsWidget = document.getElementById('aa-forum-dashboard-widget-unread-topics');

if (aaForumUnreadTopicsWidget) {
    const aaForumUnreadTopicsWidgetContent = aaForumUnreadTopicsWidget.querySelector('.aa-forum-dashboard-widget-unread-topics-content');

    fetch(aaForumDashboardWidgetsSettings.unreadTopics.ajaxUrl)
        .then((response) => {
            if (response.ok) {
                return response.text();
            }
            throw new Error('Something went wrong');
        })
        .then((responseText) => {
            // console.log('Unread Forum Topics Widget: ', responseText);

            if (responseText !== '') {
                aaForumUnreadTopicsWidgetContent.innerHTML = responseText;

                // Show the widget area
                const showWidgetArea = new bootstrap.Collapse(aaForumDashboardWidgets, { // eslint-disable-line no-unused-vars
                    show: true
                });

                // Show the widget
                const showWidget = new bootstrap.Collapse(aaForumUnreadTopicsWidget, { // eslint-disable-line no-unused-vars
                    show: true
                });

                // Initialize Bootstrap tooltips
                [].slice.call(document.querySelectorAll('[data-bs-tooltip="aa-forum-tooltip"]'))
                    .map((tooltipTriggerEl) => {
                        return new bootstrap.Tooltip(tooltipTriggerEl);
                    });
            }
        })
        .catch((error) => {
            console.log(error);
        });
}
