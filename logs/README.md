# Logs Directory

This directory contains application logs for the LinkedIn Job & Internship Bot.

## Log Files

- `linkedin_bot.log` - Main application log with rotating file handler
- `linkedin_bot.log.1`, `linkedin_bot.log.2`, etc. - Backup log files (auto-rotated)

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Something unexpected happened but the app is still working
- **ERROR**: Serious problem occurred, function or operation failed
- **CRITICAL**: Very serious error occurred, application may not continue

## Structured Logging

When `STRUCTURED_LOGGING=true` is set, logs are output in JSON format for better parsing and analysis.

## Log Rotation

Log files are automatically rotated when they reach 10MB in size, keeping up to 5 backup files.
