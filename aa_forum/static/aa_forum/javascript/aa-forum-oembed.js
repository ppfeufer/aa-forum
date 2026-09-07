/* global aaForumJsSettings */

$(document).ready(() => {
    'use strict';

    /**
     * Get the MIME type for a given video file extension
     *
     * @param {string} ext - The video file extension (e.g., 'mp4', 'webm', 'ogg', 'mov')
     * @returns {string} - The corresponding MIME type for the video file extension
     * @private
     */
    const _mimeTypeForExt = (ext) => {
        switch (ext.toLowerCase()) {
            case 'mov':
                return 'video/quicktime';

            default:
                return 'video/' + ext.toLowerCase();
        }
    };

    /**
     * Replace oembed YouTube video with an iframe
     *
     * CKEditor5 oembed plugin is used to embed YouTube videos, and browsers cannot render the oembed element.
     * This function replaces the oembed element with an iframe and is using the YouTube-nocookie domain.
     *
     * @param {string} url - The YouTube video URL
     * @returns {string} - The iframe HTML string
     * @private
     */
    const _youtubeOembedToIframe = (url) => {
        const videoId = new URLSearchParams(new URL(url).search).get('v'); // jshint ignore:line
        const videoUrl = `https://www.youtube-nocookie.com/embed/${videoId}`;
        const divClasses = 'oembed-video youtube-video';
        const iframeTitle = 'YouTube video player';
        const iframeAllow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';

        return `<div class="${divClasses}"><iframe class="youtube-video" src="${videoUrl}" title="${iframeTitle}" allow="${iframeAllow}" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>`;
    };

    /**
     * Convert a video link to a video element
     *
     * @param {string} url - The video URL
     * @returns {string} - The video element
     * @private
     */
    const _videoLinkToVideoElement = (url) => {
        // Determine extension (strip query string)
        const path = url.split('?')[0];
        const ext = (path.split('.').pop() || '').toLowerCase();
        const mime = _mimeTypeForExt(ext);

        return `<figure class="media"><div class="oembed-video ${ext}-video"><video controls><source src="${url}" type="${mime}">${aaForumJsSettings.l10n.video.elementNotSupported}</video></div></figure>`;
    };

    /**
     * Check for oembed elements in the CKEditor content and replace YouTube oembed with an iframe
     */
    const checkForOembed = () => {
        $('.ck-content figure.media oembed').filter((_, element) => {
            // Check if the source is a YouTube video
            const source = $(element).attr('url');

            if (source.includes('youtube.com/watch')) {
                $(element).replaceWith(_youtubeOembedToIframe(source));
            }
        });
    };

    /**
     * Check for video links in the CKEditor content and replace them with video elements
     */
    const checkForVideoLinks = () => {
        // Configure allowed video file extensions here
        const allowedVideoFormats = ['mp4'];

        // Helper: build a regex-friendly alternation from allowed formats
        const allowedFormatsPattern = allowedVideoFormats.map(f => f.replace(/[^a-z0-9]/gi, '')).join('|');

        // Replace explicit links (<a href="...mp4">) with <video>, but only when
        // the link is the only content on its line/parent (no other text or elements).
        $('.ck-content a').each((_, element) => {
            const a = $(element);
            const source = a.attr('href');

            // If the anchor has no href, skip it
            if (!source) {
                return;
            }

            // Build a regex to match the allowed video extensions at the end of the URL (before any query string)
            const anchorExtRegex = new RegExp('\\.(' + allowedFormatsPattern + ')(?:$|\\?)', 'i');

            // If the anchor's href does not end with an allowed video extension, skip it
            if (!anchorExtRegex.test(source)) {
                return;
            }

            // Check if the anchor is the only content in its parent (ignoring whitespace and <br> elements)
            const parent = a.parent()[0];

            // If the parent is null or undefined, we cannot proceed
            if (!parent) {
                return;
            }

            const childNodes = Array.prototype.slice.call(parent.childNodes);
            const segments = [];
            let current = [];

            // Split the parent's child nodes into segments separated by <br> elements
            childNodes.forEach((node) => {
                if (node.nodeType === 1 && node.tagName && node.tagName.toLowerCase() === 'br') {
                    segments.push(current);

                    current = [];
                } else {
                    current.push(node);
                }
            });

            segments.push(current);

            // Find the segment that contains this anchor
            let segIndex = -1;

            for (let si = 0; si < segments.length; si++) {
                if (segments[si].indexOf(a[0]) !== -1) {
                    segIndex = si;

                    break;
                }
            }

            if (segIndex === -1) {
                return;
            }

            const seg = segments[segIndex];
            let segmentHasOnlyAnchorAndWhitespace = true;

            for (let i = 0; i < seg.length; i++) {
                const node = seg[i];

                if (node === a[0]) {
                    continue;
                }

                if (node.nodeType === 3) { // text
                    if (node.nodeValue && node.nodeValue.trim() !== '') {
                        segmentHasOnlyAnchorAndWhitespace = false;

                        break;
                    }
                } else if (node.nodeType === 1) { // element
                    // Any element (other than the anchor itself) means the anchor is not alone
                    segmentHasOnlyAnchorAndWhitespace = false;

                    break;
                }
            }

            if (segmentHasOnlyAnchorAndWhitespace) {
                // Replace the anchor with a video element
                a.replaceWith(_videoLinkToVideoElement(source));
            }
        });

        // Also handle plain-text URLs inside the editor content (not wrapped in <a>),
        // e.g. when a user pastes a raw URL into the text. We find text nodes and
        // replace any mp4 URLs with a <video> element. We avoid replacing text inside
        // anchors or already-embedded media.
        // Match http(s) or protocol-relative URLs that end with one of the allowed extensions
        const urlRegex = new RegExp('((?:https?:)?\\/\\/[\\w\\-@:%_+.~#?&/=]*?\\.(' + allowedFormatsPattern + ')(?:\\?[^\\s]*)?)', 'gi');

        $('.ck-content').find('*').addBack().contents().filter((_, node) => {
            // keep only text nodes
            return node.nodeType === 3;
        }).each((_, textNode) => {
            const parent = $(textNode).parent();

            // Skip if inside an anchor or inside an oembed/video wrapper
            if (parent.closest('a').length || parent.closest('.oembed-video, figure.media').length) {
                return;
            }

            const text = textNode.nodeValue;

            if (!text || !urlRegex.test(text)) {
                // Reset lastIndex in case of global regex reuse
                urlRegex.lastIndex = 0;

                return;
            }

            // Only convert allowedFormatsPattern URLs that are on their own line.
            // Split the text node by line breaks and replace lines that contain
            // only an allowedFormatsPattern URL (optionally with a query string) with a <video> element.
            const urlLineRegex = new RegExp('^(?:https?:)?\\/\\/[\\w\\-@:%_+.~#?&/=]*?\\.(' + allowedFormatsPattern + ')(?:\\?[^\\s]*)?$', 'i');

            const lines = text.split(/\r?\n/);
            const newNodes = [];

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const trimmed = line.trim();

                if (trimmed && urlLineRegex.test(trimmed)) {
                    // Create video element from the matched URL
                    const video = $(_videoLinkToVideoElement(trimmed));

                    // Append as DOM node(s)
                    video.each((_, video) => {
                        newNodes.push(video);
                    });
                } else {
                    // Preserve the original text (including spacing) as a text node
                    newNodes.push(document.createTextNode(line));
                }

                // Re-insert the line break as a text node if it wasn't the last line
                if (i < lines.length - 1) {
                    newNodes.push(document.createTextNode('\n'));
                }
            }

            // Replace the original text node with the constructed nodes
            $(textNode).replaceWith(newNodes);
        });
    };

    checkForOembed();
    checkForVideoLinks();
});
