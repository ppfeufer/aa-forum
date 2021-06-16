# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- SQL script to drop all tables

## Changed

- Improved model design for better data consistency, performance and compliance with Django conventions
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
