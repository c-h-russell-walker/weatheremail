# Notes:
### (primarily about scaling parts of this application) broken down by module/file/function

## weatheremail.base.models
If we're using Django >=1.10 it couldn't hurt to leverage the BigAutoField for the primary key of
`WeatherUser` - it's a 64 bit integer as opposed to the default 32 bit
https://docs.djangoproject.com/en/1.10/ref/models/fields/#bigautofield

## weatheremail.libs.wunderground.api
This is the client for the actual HTTP requests to the API - I think we can do these requests ahead of time for the
tasks etc. but more on that to come.  Main thing we should consider is whatever API we do use if we can make batched
requests and get data back for multiple locations at once.

## weatheremail.emails.tasks
### `EmailUsersPeriodicTask`
Using .iterator() is better for memory consumption - from the docs:
"iterator() will read results directly, without doing any caching at the QuerySet"

Also using values_list for memory consumption - from the docs:
"...values_list() ... intended as optimizations for a specific use case: retrieving
a subset of data without the overhead of creating a model instance"

We should concern ourselves with batching also so this scales to millions - basically we'd figure out what a
good batch size might be to select that many rows from the DB at once and since it's only a SELECT we don't have
to worry about any data alteration - just worry about sending multiple emails to the same person but I don't think
it would be too hard to keep track of current place in rows.
Also considering the ORM is doing basically nothing we could also write a raw query for PSQL, MySQL etc.
if we saw any benefit from that.

### `SendWeatherEmail`
So the main Task here - this is where we could make some pretty good and new architectural decisions.
There's no reason we need to make API requests for the same actual location (not user location) more than once - meaning
no point in making the same call for Boston, MA repeatedly.
Also we shouldn't have the tasks spun up for each user wait synchronously on those API calls.

So my thoughts are that we could have another periodic task or tasks that fire before the current one.
This task could make the API calls for each unique location we have in our DB and save the results to another table
maybe or some sort of cache like Redis even.  We want today's weather to be relatively recent - that could be
monitored - what the difference in email sent time to time that the current weather was fetched.

Another thought is we can get the historical data used for average temperature really at any point - we could
decide on when it would be considered 'stale' for a location re-fetch (thinking about using a postsave signal
for when a user signs up and if we don't have historical data for their location fetch it then).
We could have a wunderground wrapper that returns the data if we have it in our DB (or cache) and if not does an
on-the-fly API call.  That should take care of the edge case where a user signs up with a new location we haven't
gotten the data for yet.


#### *MISC
We obviously shouldn't use my personal gmail account with built in Django email functionality if
we want to scale ;-)
I assume we'd have a queue of emails with the HTML all rendered and reeady to go using a third party service.
