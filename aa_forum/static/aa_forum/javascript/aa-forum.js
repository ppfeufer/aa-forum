/* global aaForumJsSettingsDefaults, aaForumJsSettingsOverride, objectDeepMerge */

/* jshint -W097 */
'use strict';

// Build the settings object
let aaForumJsSettings = typeof aaForumJsSettingsDefaults !== 'undefined' ? aaForumJsSettingsDefaults : null;

if (aaForumJsSettings && typeof aaForumJsSettingsOverride !== 'undefined') {
    aaForumJsSettings = objectDeepMerge(
        aaForumJsSettings,
        aaForumJsSettingsOverride
    );
}
