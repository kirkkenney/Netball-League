# Netball League Project

This project is built with the purpose of allowing local netball hobbyists
to manage their teams within the league, to allow organisers of the league
to arrange match fixtures, easily communicate with team captains etc.


## The project is *currently* a work in progress


# Project Requirements And Considerations

## League Structure And Data

The league is managed and overseen by a Chair and league representatives.
The Chair and reps set match fixtures, approve the registration of new players,
disqualify players etc. They can be said, therefore, to have the highest
admin privileges.

Team captains register new players to their team (need to be approved by
Chair / reps), and must select an umpire on a per-match basis. As part of this
project, I decided it would also be useful for each team to have a private
message board, with the ability for team captains to email their players from
within the application.

Each match is umpired by a selected player from the home team, and both team captains
must sign off on the final score.

Data within the application should be able to frequently traverse the database
models in order to set preliminary values, update those values, and where appropriate
send the updated data to a different database table (eg captain adds a player to
the PendingUser table; Chair/reps review the application and if approved, the new
player is removed from PendingUser and sent to User table)

## Privacy and Security

The application should serve as a platform for the league participants only.
Therefore, the home page only displays a limited number of past and previous matches.
All other pages/information etc requires user login. Users cannot register freely,
they must be registered by their team captain.

## UX Considerations

The application should be easily navigable and allow players to quickly and easily access:
 - League information/updates/scores
 - Their team information including the private message board
 - View information about opposing teams

In building the application, I also took the view that any users with edit permissions
(team captains, chair, reps) should be able to easily update data from within the application.
All users with the required permissions therefore have access to a 'Dashboard' page,
as well as dynamically inserted edit permissions within the relevant pages.

## To Do

* Tidy up styling.

* Add confirmation modals before allowing user to delete data

~~* Bug currently prevents a user from being deleted if the user has posts~~
   * Added a fix to delete all posts associated with user first

 ~~* Passwords are currently set to 'password' by default for testing purposes. This
 needs to be amended so that they are automatically assigned a generated token as
 their password, and emailed a reset link to manually update it.~~

   * Passwords now set using bcrypt library

 ~~* Add a new Posts database model, page and form. Allow players to add posts
 to their team's message board. Add a conditional check to allow team captain
 to send their post as an email to all the team's players~~

~~* Update matches page template to allow umpire to update the score, only
 to be displayed if both team capains approve. Captains to add players to
 the match.~~

 ~~* Update database tables and relevant pages to include 'approved by' info,
 and timestamp appropriate updates (approved Users, set/approve match scores)~~

 ~~* Clean up code, add comments~~
