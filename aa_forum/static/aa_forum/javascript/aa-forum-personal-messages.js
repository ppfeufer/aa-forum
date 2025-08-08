/* global aaForumJsSettings, fetchGet, fetchPost */

$(document).ready(() => {
    'use strict';

    const buttonReadMessage = $('button.btn-read-personal-message');

    $(buttonReadMessage).on('click', (event) => {
        const element = $(event.currentTarget);
        const sender = element.data('sender');
        const recipient = element.data('recipient');
        const message = element.data('message');
        const messageFolder = element.data('message-folder');

        fetchPost({
            url: aaForumJsSettings.url.readMessage,
            csrfToken: aaForumJsSettings.form.csrfToken,
            payload: {
                sender: sender,
                recipient: recipient,
                message: message
            },
            responseIsJson: false
        })
            .then((data) => {
                if (undefined === data || data === '') {
                    return;
                }

                const messageContainer = $(`#aa-forum-personal-message-id-${message} .card-aa-forum-personal-messages-message`);
                messageContainer.html(data).removeClass('d-none');

                if (messageFolder === 'inbox') {
                    $(`#aa-forum-personal-message-id-${message} .card-aa-forum-personal-messages-item`)
                        .removeClass('panel-aa-forum-personal-messages-item-unread');

                    // Get new unread count
                    fetchGet({url: aaForumJsSettings.url.unreadMessagesCount})
                        .then((data) => {
                            if (data.unread_messages_count === 0) {
                                $('.aa-forum-badge-personal-messages-unread-count').remove();
                            } else {
                                $('.aa-forum-badge-personal-messages-unread-count')
                                    .html(data.unread_messages_count);
                            }
                        })
                        .catch((error) => {
                            console.error('Error fetching unread messages count:', error);
                        });
                }
            })
            .catch((error) => {
                console.error('Error reading message:', error);
            });
    });
});
