/* global personalMessagesSettings */

$(function () {
    'use strict';

    const buttonReadMessage = $('button.btn-read-personal-message');

    $(buttonReadMessage).on('click', function () {
        const element = $(this);
        const sender = element.data('sender');
        const recipient = element.data('recipient');
        const message = element.data('message');
        const url = personalMessagesSettings.urlReadMessage;
        const csrfMiddlewareToken = personalMessagesSettings.csrfToken;

        const posting = $.post(
            url,
            {
                csrfmiddlewaretoken: csrfMiddlewareToken,
                sender: sender,
                recipient: recipient,
                message: message
            }
        );

        posting.done((data) => {
            if (data.replace(/\s/g, '') === '') {
                return;
            }

            const messageContainer = $('.aa-forum-personal-messages-message');

            messageContainer.html('');
            messageContainer.html(data);

            $('html, body').animate(
                {scrollTop: messageContainer.offset().top - 50}, 500
            );

            // Remove unread marking (bold font)
            $('#aa-forum-personal-message-id-' + message)
                .removeClass('panel-aa-forum-personal-messages-item-unread');
        });
    });
});
