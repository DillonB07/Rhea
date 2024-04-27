# Rhea

Rhea is a virtual assistant that I am developing to help with my day to day life. I am open 
sourcing this project so that anyone may use it if they wish.

## Purpose

Rhea is designed to be a virtual assistant that can help with a variety of tasks. Here are some examples of what I would like to be able to do with Rhea:
- Manage my calendar
- Manage my to-do list
- Manage my alarms
- Send emails
- Message people on various platforms (Discord, Slack)
- Play music from Spotify or Navidrome
- Control micro:bit powered lights

## API Features
- Music Control
  - Subsonic

## Structure

The project is structured as a monorepo to make it easy for me to manage.
Here's what the folders do:
- `server` - A Flask server which serves as the backend for the assistant. This is essentially an API for the various frontends to interact with however it also includes a basic React frontend.
- `discord` - A Discord user app to allow me to interact with the assistant through 
  user-specific application commands.
- `slack` - A Slack bot to allow me to interact with the assistant through a Slack bot.
- `voice` - A voice assistant created with Python that uses natural language to interact with Rhea.

### Credits

Some code has been taken from the following repositories and has been modified to fit Rhea's purpose.

- [kutu-dev/disopy](https://github.com/kutu-dev/disopy)
