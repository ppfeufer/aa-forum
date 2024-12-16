/* global aaForumJsSettingsDefaults, aaForumJsSettingsOverride */

/* jshint -W097 */
'use strict';

/**
 * Checks if the given item is a plain object, excluding arrays and dates.
 *
 * @param {*} item - The item to check.
 * @returns {boolean} True if the item is a plain object, false otherwise.
 */
function isObject (item) {
    return (
        item && typeof item === 'object' && !Array.isArray(item) && !(item instanceof Date)
    );
}

/**
 * Recursively merges properties from source objects into a target object. If a property at the current level is an object,
 * and both target and source have it, the property is merged. Otherwise, the source property overwrites the target property.
 * This function does not modify the source objects and prevents prototype pollution by not allowing __proto__, constructor,
 * and prototype property names.
 *
 * @param {Object} target - The target object to merge properties into.
 * @param {...Object} sources - One or more source objects from which to merge properties.
 * @returns {Object} The target object after merging properties from sources.
 */
function deepMerge (target, ...sources) {
    if (!sources.length) {
        return target;
    }

    // Iterate through each source object without modifying the `sources` array.
    sources.forEach(source => {
        if (isObject(target) && isObject(source)) {
            for (const key in source) {
                if (isObject(source[key])) {
                    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
                        continue; // Skip potentially dangerous keys to prevent prototype pollution.
                    }

                    if (!target[key] || !isObject(target[key])) {
                        target[key] = {};
                    }

                    deepMerge(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            }
        }
    });

    return target;
}

// Build the settings object
let aaForumJsSettings = typeof aaForumJsSettingsDefaults !== 'undefined' ? aaForumJsSettingsDefaults : null; // eslint-disable-line no-unused-vars

if (aaForumJsSettings && typeof aaForumJsSettingsOverride !== 'undefined') {
    aaForumJsSettings = deepMerge( // eslint-disable-line no-unused-vars
        aaForumJsSettings,
        aaForumJsSettingsOverride
    );
}
