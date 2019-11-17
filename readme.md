[x] User can register an account with his username, email, password.
[x] User should see appropriate flash messages depending on the situation (email taken? username taken? email too short?).
[x] User can login with their credentials.
[x] User should see appropriate flash messages depending on the situation upon loggin in(wrong email, wrong password?).

[x] User can access a route which renders a form which allows them to create a new blog.

[x] User should be able to see all the blogs with title, body, author name, datetime created/ updated with maximum 100 characters, and the newest blogs will be on top.

[x] User can then see full details of each blog (include comments feature which mentioned below) when he click on the blog title (direct them to another route).

[x] User can edit/delete their own blogs but not others.

[x] User can access a route which renders all the blogs which belong to the current_user.

[x] User cannot create the blogs or access to "create blog" screen unless they're signed in.

[x] User can only sign out once signed in, links and urls should be disabled too.

[x] User can see comments which belong to each blog.

[x] User should be able to comment on each blog too, also edit and delete their own comments but not others.

[x] User can delete any comments on their own posts regardless of original user.

[x] User should be able to sort the list of blogs (newest first/last).

Rockets 🚀
[x] User can see a count of how many comments each blog has (on both all blogs and single blog page).
[ ] Implement: Vote or Like system, each user can only like or vote up/down once. If he attempts to do it again, return his action to 0 then allow him to vote/like again.
[ ] Following feature, a user can follow other users, and will see all the blogs from them.
[ ] A page that show some statistics, e.g top bloggers, top vote/like blogs, top blogs which have most comments.