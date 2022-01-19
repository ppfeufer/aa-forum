/* global categoriesWithBoards, boardsWithChildren, aaForumAdminSettings */

$(function () {
    'use strict';

    /**
     * Sort categories via drag and drop
     */
    $('.categories-sortable').sortable({
        placeholder: 'aa-forum-ui-placeholder',
        connectWith: '.categories_sortable',
        containment: 'parent',
        start (e, ui) {
            // get the instance of the sortable.
            // instance method is new to jquery ui 1.11, for previous versions
            // you can use $(this).data()['ui-sortable'];
            const sort = $(this).sortable('instance');

            // this makes the placeholder fit with the row that's being dragged
            ui.placeholder.height(ui.helper.height());

            // containment property of the sortable instance is different
            // as the containment option. The property is calculated
            // from the option. You need to adjust bottom coordinates
            // to take into account the row you just removed from it, and the click offset.
            sort.containment[3] += ui.helper.height() * 2.5;

            // Since your handle is centered, and pointer coordinates are used
            // for sortable, but top coordinates are used for containment
            // you can have issues with top row. Adjusting with the click offset
            // will resolve the issue.
            sort.containment[1] -= sort.offset.click.top;
        },
        update () {
            const categories = [];

            $('.categories-sortable .category-sortable').each(function (index) {
                $(this).attr('data-position', index);

                categories.push({
                    catId: $(this).data('category-id'),
                    catOrder: index
                });
            });

            // Update DB
            $.post(
                aaForumAdminSettings.urls.categoryOrder,
                {
                    categories: JSON.stringify(categories),
                    csrfmiddlewaretoken: aaForumAdminSettings.form.csrfToken
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
    if ('undefined' !== typeof categoriesWithBoards && categoriesWithBoards.length > 0) {
        $(categoriesWithBoards).each(function (key) {
            $(categoriesWithBoards[key]).sortable({
                placeholder: 'aa-forum-ui-placeholder',
                connectWith: categoriesWithBoards[key],
                containment: 'parent',
                start (e, ui) {
                    // get the instance of the sortable.
                    // instance method is new to jquery ui 1.11, for previous versions
                    // you can use $(this).data()['ui-sortable'];
                    const sort = $(this).sortable('instance');

                    // this makes the placeholder fit with the row that's being dragged
                    ui.placeholder.height(ui.helper.height());

                    // containment property of the sortable instance is different
                    // as the containment option. The property is calculated
                    // from the option. You need to adjust bottom coordinates
                    // to take into account the row you just removed from it, and the click offset.
                    sort.containment[3] += ui.helper.height() * 2.5;

                    // Since your handle is centered, and pointer coordinates are used
                    // for sortable, but top coordinates are used for containment
                    // you can have issues with top row. Adjusting with the click offset
                    // will resolve the issue.
                    sort.containment[1] -= sort.offset.click.top;
                },
                update () {
                    const boards = [];

                    $(categoriesWithBoards[key] + ' li.board-sortable').each(function (index) {
                        $(this).attr('data-position', index);

                        boards.push({
                            boardId: $(this).data('board-id'),
                            boardOrder: index
                        });
                    });

                    // Update DB
                    $.post(
                        aaForumAdminSettings.urls.boardOrder,
                        {
                            boards: JSON.stringify(boards),
                            csrfmiddlewaretoken: aaForumAdminSettings.form.csrfToken
                        }
                    );
                }
            }).disableSelection();
        });
    }

    /**
     * Sort child boards via drag and drop
     */
    if ('undefined' !== typeof boardsWithChildren && boardsWithChildren.length > 0) {
        $(boardsWithChildren).each(function (key) {
            $(boardsWithChildren[key]).sortable({
                placeholder: 'aa-forum-ui-placeholder',
                connectWith: boardsWithChildren[key],
                containment: 'parent',
                start (e, ui) {
                    // get the instance of the sortable.
                    // instance method is new to jquery ui 1.11, for previous versions
                    // you can use $(this).data()['ui-sortable'];
                    const sort = $(this).sortable('instance');

                    // this makes the placeholder fit with the row that's being dragged
                    ui.placeholder.height(ui.helper.height());

                    // containment property of the sortable instance is different
                    // as the containment option. The property is calculated
                    // from the option. You need to adjust bottom coordinates
                    // to take into account the row you just removed from it, and the click offset.
                    sort.containment[3] += ui.helper.height() * 2.5;

                    // Since your handle is centered, and pointer coordinates are used
                    // for sortable, but top coordinates are used for containment
                    // you can have issues with top row. Adjusting with the click offset
                    // will resolve the issue.
                    sort.containment[1] -= sort.offset.click.top;
                },
                update () {
                    const childBoards = [];

                    $(boardsWithChildren[key] + ' li.child-board-sortable').each(function (index) {
                        $(this).attr('data-position', index);

                        childBoards.push({
                            boardId: $(this).data('board-id'),
                            boardOrder: index
                        });
                    });

                    // Update DB
                    $.post(
                        aaForumAdminSettings.urls.boardOrder,
                        {
                            boards: JSON.stringify(childBoards),
                            csrfmiddlewaretoken: aaForumAdminSettings.form.csrfToken
                        }
                    );
                }
            }).disableSelection();
        });
    }
});
