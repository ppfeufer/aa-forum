/**
 * Replace oembed YouTube video with an iframe
 *
 * CKEditor5 oembed plugin is used to embed YouTube videos, and browsers cannot render the oembed element.
 * This function replaces the oembed element with an iframe and is using the YouTube-nocookie domain.
 *
 * @param {string} url The YouTube video URL
 * @returns {`<div class="oembed-video youtube-oembed-video"><iframe src="${string}" title="YouTube video player" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>`}
 */
const youtubeOembedToIframe = (url) => {
    const videoId = new URLSearchParams(new URL(url).search).get('v'); // jshint ignore:line
    const videoUrl = `https://www.youtube-nocookie.com/embed/${videoId}`;
    const divClasses = 'oembed-video youtube-oembed-video';
    const iframeTitle = 'YouTube video player';
    const iframeAllow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';

    return `<div class="${divClasses}"><iframe src="${videoUrl}" title="${iframeTitle}" allow="${iframeAllow}" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>`;
};


/**
 * Look for oembed elements and replace them with iframes
 */
const checkForOembed = () => {
    'use strict';

    $('.ck-content figure.media oembed').filter((_, element) => {
        // Check if the source is a YouTube video
        const source = $(element).attr('url');

        if (source.includes('youtube.com/watch')) {
            $(element).replaceWith(youtubeOembedToIframe(source));
        }
    });
};

// Run the checkForOembed function when the document is ready
$(document).ready(() => {
    'use strict';

    checkForOembed();
});
