# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


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
