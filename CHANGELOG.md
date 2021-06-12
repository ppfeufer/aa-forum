# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [0.0.1-alpha.4] - 2021-06-12

### Added

- Messages can now be modified by their author or anyone with the `manage_forum`
  permission

### Fixed

- `time_modified` timestamps for messages


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
