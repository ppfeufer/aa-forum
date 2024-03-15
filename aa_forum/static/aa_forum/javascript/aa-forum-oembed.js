/**
 * Replace oembed YouTube video with an iframe
 *
 * CKEditor5 oembed plugin is used to embed YouTube videos, and browsers cannot render the oembed element.
 * This function replaces the oembed element with an iframe and is using the YouTube-nocookie domain.
 *
 * @param {string} url The YouTube video URL
 * @returns {`<div class="oembed-video youtube-oembed-video"><iframe src="https://www.youtube-nocookie.com/embed/${string}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>`}
 */
const youtubeOembedToIframe = (url) => {
    'use strict';

    let videoId = url.split('v=')[1];
    const ampersandPosition = videoId.indexOf('&');

    if (ampersandPosition !== -1) {
        videoId = videoId.substring(0, ampersandPosition);
    }

    return `<div class="oembed-video youtube-oembed-video"><iframe src="https://www.youtube-nocookie.com/embed/${videoId}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>`;
};


/**
 * Look for oembed elements and replace them with iframes
 */
const checkForOembed = () => {
    'use strict';

    // Find all oembed elements and loop through them
    $('.ck-content figure.media oembed').each((index, element) => {
        const source = $(element).attr('url');

        // Check if the source is a YouTube video
        if (source.includes('youtube.com/watch')) {
            // Replace the oembed element with an iframe
            $(element).replaceWith(youtubeOembedToIframe(source));
        }
    });
};


$(document).ready(() => {
    'use strict';

    // Run the checkForOembed function when the document is ready
    checkForOembed();
});
