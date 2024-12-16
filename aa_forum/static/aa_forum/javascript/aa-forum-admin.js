/* global aaForumJsSettings */

$(document).ready(() => {
    'use strict';

    const sortableCategories = $('.categories-sortable');

    /**
     * Sort categories via drag and drop
     */
    sortableCategories.sortable({
        placeholder: 'aa-forum-ui-placeholder',
        connectWith: '.categories_sortable',
        containment: 'parent',
        start (e, ui) {
            // Get the instance of the sortable.
            // Instance method is new to jquery ui 1.11, for previous versions
            // you can use $(this).data()['ui-sortable'];
            const sort = sortableCategories.sortable('instance');

            // this makes the placeholder fit with the row that's being dragged
            ui.placeholder.height(ui.helper.height());

            // The Containment property of the sortable instance is different
            // as the containment option. The property is calculated
            // from the option. You need to adjust bottom coordinates
            // to take into account the row you just removed from it, and the click offset.
            sort.containment[3] += ui.helper.height() * 2.5;

            // Since your handle is centered, and pointer coordinates are used
            // for sortable, but top coordinates are used for containment,
            // you can have issues with the top row. Adjusting with the click offset
            // will resolve the issue.
            sort.containment[1] -= sort.offset.click.top;
        },
        update () {
            const categories = [];

            $('.categories-sortable .category-sortable').each((index, element) => {
                $(element).attr('data-position', index);

                categories.push({
                    catId: $(element).data('category-id'),
                    catOrder: index
                });
            });

            // Update DB
            $.post(
                aaForumJsSettings.url.categoryOrder,
                {
                    categories: JSON.stringify(categories),
                    csrfmiddlewaretoken: aaForumJsSettings.form.csrfToken
                }
            );
        }
    }).disableSelection();

    $('.categories-sortable select').SumoSelect(
        {okCancelInMulti: true, selectAll: true}
    );

    /**
     * Sort boards via drag and drop
     */
    if ('undefined' !== typeof aaForumJsSettings.categoriesWithBoards && aaForumJsSettings.categoriesWithBoards.length > 0) {
        $(aaForumJsSettings.categoriesWithBoards).each((key, element) => {
            $(aaForumJsSettings.categoriesWithBoards[key]).sortable({
                placeholder: 'aa-forum-ui-placeholder',
                connectWith: aaForumJsSettings.categoriesWithBoards[key],
                containment: 'parent',
                start (e, ui) {
                    // Get the instance of the sortable.
                    // Instance method is new to jquery ui 1.11, for previous versions
                    // you can use $(this).data()['ui-sortable'];
                    const sort = $(element).sortable('instance');

                    // this makes the placeholder fit with the row that's being dragged
                    ui.placeholder.height(ui.helper.height());

                    // The Containment property of the sortable instance is different
                    // as the containment option. The property is calculated
                    // from the option. You need to adjust bottom coordinates
                    // to take into account the row you just removed from it, and the click offset.
                    sort.containment[3] += ui.helper.height() * 2.5;

                    // Since your handle is centered, and pointer coordinates are used
                    // for sortable, but top coordinates are used for containment,
                    // you can have issues with the top row. Adjusting with the click offset
                    // will resolve the issue.
                    sort.containment[1] -= sort.offset.click.top;
                },
                update () {
                    const boards = [];

                    $(aaForumJsSettings.categoriesWithBoards[key] + ' li.board-sortable').each((index, element) => {
                        $(element).attr('data-position', index);

                        boards.push({
                            boardId: $(element).data('board-id'),
                            boardOrder: index
                        });
                    });

                    // Update DB
                    $.post(
                        aaForumJsSettings.url.boardOrder,
                        {
                            boards: JSON.stringify(boards),
                            csrfmiddlewaretoken: aaForumJsSettings.form.csrfToken
                        }
                    );
                }
            }).disableSelection();
        });
    }

    /**
     * Sort child boards via drag and drop
     */
    if ('undefined' !== typeof aaForumJsSettings.boardsWithChildren && aaForumJsSettings.boardsWithChildren.length > 0) {
        $(aaForumJsSettings.boardsWithChildren).each((key, element) => {
            $(aaForumJsSettings.boardsWithChildren[key]).sortable({
                placeholder: 'aa-forum-ui-placeholder',
                connectWith: aaForumJsSettings.boardsWithChildren[key],
                containment: 'parent',
                start (e, ui) {
                    // Get the instance of the sortable.
                    // Instance method is new to jquery ui 1.11, for previous versions
                    // you can use $(this).data()['ui-sortable'];
                    const sort = $(element).sortable('instance');

                    // this makes the placeholder fit with the row that's being dragged
                    ui.placeholder.height(ui.helper.height());

                    // The Containment property of the sortable instance is different
                    // as the containment option. The property is calculated
                    // from the option. You need to adjust bottom coordinates
                    // to take into account the row you just removed from it, and the click offset.
                    sort.containment[3] += ui.helper.height() * 2.5;

                    // Since your handle is centered, and pointer coordinates are used
                    // for sortable, but top coordinates are used for containment,
                    // you can have issues with the top row. Adjusting with the click offset
                    // will resolve the issue.
                    sort.containment[1] -= sort.offset.click.top;
                },
                update () {
                    const childBoards = [];

                    $(aaForumJsSettings.boardsWithChildren[key] + ' li.child-board-sortable').each((index, element) => {
                        $(element).attr('data-position', index);

                        childBoards.push({
                            boardId: $(element).data('board-id'),
                            boardOrder: index
                        });
                    });

                    // Update DB
                    $.post(
                        aaForumJsSettings.url.boardOrder,
                        {
                            boards: JSON.stringify(childBoards),
                            csrfmiddlewaretoken: aaForumJsSettings.form.csrfToken
                        }
                    );
                }
            }).disableSelection();
        });
    }
});
