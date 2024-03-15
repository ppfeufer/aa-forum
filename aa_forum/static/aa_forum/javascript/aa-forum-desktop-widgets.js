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

                const showWidgetArea = new bootstrap.Collapse(aaForumDashboardWidgets, { // eslint-disable-line no-unused-vars
                    show: true
                });

                const showWidget = new bootstrap.Collapse(aaForumUnreadTopicsWidget, { // eslint-disable-line no-unused-vars
                    show: true
                });
            }
        })
        .catch((error) => {
            console.log(error);
        });
}
