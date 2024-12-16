/* global aaForumJsSettings */

$(document).ready(() => {
    'use strict';

    const buttonReadMessage = $('button.btn-read-personal-message');

    $(buttonReadMessage).on('click', (event) => {
        const element = $(event.currentTarget);
        const sender = element.data('sender');
        const recipient = element.data('recipient');
        const message = element.data('message');
        const messageFolder = element.data('message-folder');

        const getMessageToRead = $.post(
            aaForumJsSettings.url.readMessage,
            {
                csrfmiddlewaretoken: aaForumJsSettings.form.csrfToken,
                sender: sender,
                recipient: recipient,
                message: message
            }
        );

        getMessageToRead.done((data) => {
            if (undefined === data || data === '') {
                return;
            }

            const messageContainer = $(`#aa-forum-personal-message-id-${message} .card-aa-forum-personal-messages-message`);
            messageContainer.html(data).removeClass('d-none');

            if (messageFolder === 'inbox') {
                const urlUnreadMessagesCount = aaForumJsSettings.url.unreadMessagesCount;

                $(`#aa-forum-personal-message-id-${message} .card-aa-forum-personal-messages-item`)
                    .removeClass('panel-aa-forum-personal-messages-item-unread');

                // Get new unread count
                const getUnreadMessageCount = $.get(urlUnreadMessagesCount);

                getUnreadMessageCount.done((data) => {
                    if (data.unread_messages_count > 0) {
                        $('.aa-forum-badge-personal-messages-unread-count')
                            .html(data.unread_messages_count);
                    }

                    if (data.unread_messages_count === 0) {
                        $('.aa-forum-badge-personal-messages-unread-count').remove();
                    }
                });
            }
        });
    });
});
