# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [0.1.0-beta.3] - 2021-07-07

### Added

- Youtube embed plugin for CKEditor

### Changed

- Default config for CKEditor (see [Readme](README.md) for details) to implement the
  Youtube embed plugin and to remove the obsolete Flash embed


## [0.1.0-beta.2] - 2021-07-05

### Changed

- Setup classifier and pyupgrade check, since we aim to support AA 2.8.x with its
  current minimum Python version of 3.6


## [0.1.0-beta.1] - 2021-07-04

## \o/ FIRST PUBLIC BETA \o/

### Added

- Title attribute to last message in forum index
- "Mark all messages as read" button to forum index
- Counter for unread topics on forum link in navigation


## [0.0.1-alpha.11] - 2021-06-28

### Fixed

- `Topic.MultipleObjectsReturned: get() returned more than one Topic -- it returned 2!`
  when a board was restricted to more than 1 group


## [0.0.1-alpha.10] - 2021-06-28

### ⚠️ Migration Reset ⚠️

**Before** you update to this version, run the following command:

```shell
python manage.py migrate aa_forum zero
```

**After** you updated run:

```shell
python manage.py migrate aa_forum
```

### Added

- Unread messages functionality
- Version to static files to break browser caches on version updates
- New topic view now also has the bread crumb navigation
- Ability to create new boards with a new category
- Clear form button in forms that need it

### Changed

- Search function behavior. Up until now, the search function was looking for the
  whole search phrase, which is not the desired behavior. Now it checks if at least
  one word of the search phrase is in the message. This might give you more results
  but also doesn't miss the result you were looking for.
- Slugs consolidated
- Internal URLs reworked
- Pagination URLs reworked

### Fixed

- Appearance for multi select dropdown when dark mode is used


## [0.0.1-alpha.9] - 2021-06-17

### Added

- Search functionality

### Fixed

- A bug that prevented the forum index to load after removing a message or even a topic


## [0.0.1-alpha.8] - 2021-06-16

### ⚠️ Migration Reset ⚠️

**Before** you update to this version, run the following command:

```shell
python manage.py migrate aa_forum zero
```

**After** you updated run:

```shell
python manage.py migrate aa_forum
```

### Added

- SQL script to drop all tables

### Changed

- Improved model design for better data consistency, performance and compliance with
  Django conventions
- Improved queries to reduce page load time for all main views


## [0.0.1-alpha.7] - 2021-06-14

### Added

- Warning when replying on locked topics
- "Re:" on last message subject on forum index, if the last message in this board
  isn't the last message in the respective topic

### Fixed

- After creating a new topic, the user now returns to the newly created topic
  instead of the board view
- Vertical alignment of the topic names in board view


## [0.0.1-alpha.6] - 2021-06-13

### Fixed

- Date and time format in the message header
- The editor now uses the space it has and doesn't sit in its corner any longer
  Add the following to your `local.py`
  ```python
  CKEDITOR_CONFIGS = {"default": {"width": "100%", "height": "45vh"}}
  ```
- Lightbox doesn't put the complete message in the modal anymore, now just the image
  that has been clicked


## [0.0.1-alpha.5] - 2021-06-13

### Added

- Messages can now be modified by their author or anyone with the `manage_forum`
  permission
- Messages can now be deleted by users with the `manage_forum` permission. Keep in
  mind, if the last message of a topic is deleted, the topic will be removed as well.

### Fixed

- `time_modified` timestamps for messages
- Topic does not exist error when trying to view a topic that indeed does not exist
  (anymore)
- An issue where the initialization of the lightbox modal would interfere with other
  modals in a topic view. Even when there was no image that needs a lightbox.
- Consistent button style


## [0.0.1-alpha.4] - 2021-06-12

### Added

- A note when replying to a topic while not being on the last page of it
- Ability to lock and unlock topics for forum managers
- Ability to set/unset topics as "Sticky" for forum managers
- Ability to delete topics for forum managers
- Some "read_by" marker in preparation for the "Unread Messages" functionality

### Changed

- Implemented a simpler way to get a setting from the DB


## [0.0.1-alpha.3] - 2021-06-11

### Added

- Topic pagination in board view

### Changed

- Removed the page number from pagination links when navigating to the first page.
  It's not needed there ...


## [0.0.1-alpha.2] - 2021-06-11

### Fixed

- Missing prefix added to "New Category" form


## [0.0.1-alpha.1] - 2021-06-11

### Added

- First version for Alpha testing
