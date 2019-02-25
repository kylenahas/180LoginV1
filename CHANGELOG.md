# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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