# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed


## [0.9.4] - 2019-3-18
### Added
- venv is now fully contained in project to attempt to make setup on new computers easier
- Zebra library now internal to project to fix dependency problem on Windows
- Log to text file option
- Optionally specify location of log and member databases
### Changed
- New pandas testing in chartsHelper
- Fixed bug where an invalid DOB could cause a member to be un-editable

## [0.9.3] - 2019-3-1
### Added
- AdminApp, a sandbox to do one off functions that don't belong in the main UI
    - Includes it's own console and easy (but ugly) button creation
- dbManage.py is now documented
- Members can now be soft-deleted. Their info is not removed from the database, but the member has a hidden "deleted" attribute added to their profile. Deleted members will not be shown in search results.
### Changed
- Buttons in search windows have been revised
- Fixed Sign-Offs in search window

## [0.9.2] - 2019-2-25

### Added

- Zebra Printer support

### Changed

- Member scan fields are now searchable

## [0.9.1] - 2018-12-22
### Added
- Implemented Member Skills Sign Offs 
### Changed
- Signoffs enabled by default

## [0.9.0] - 2018-12-21
### Added
- Student annual and Trial membership options
- Editable expiration date in update member window
- Dynamically displayed punch/expiration date in update member window 
- Linked members stored in DB
- Configuration options in config.py
- Now displays time until expiration for time based members
- Members can now only log in once a day
- Member signoffs window (disabled in config)

### Changed
- Split large files into more reasonable chunks
- Membership options now live in config.py
- The window that pops up when a member logs in now automatically closes itself after 3 seconds