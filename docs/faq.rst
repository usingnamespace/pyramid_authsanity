Frequently Asked Questions
==========================

Why tickets?
~~~~~~~~~~~~

If you have a web application that uses a simple signed cookie that contains
information about the signed in user, the login will not expire until the
cookie's expiration. This can leave gaps in security.

Take the scenario of an employee that uses their own device for business, they
log in in the morning before heading into the office and the cookie is set to
authenticate them for 12 hours. They go buy some coffee and put their phone
down. Walking out they leave the phone on a table. Once they find out they
notify the company about the lost phone, however since the authentication
cookie is their username, there is no way to terminate the existing session,
and were an attacker able to use their phone they would be able to continue
using the web application for the next 12 hours.

Tickets are stored server side, and for each device/login there will be a
unique ticket. These can be individually removed, and as soon as it is removed
the authentication is no longer valid.

Facebook/Google for example also allow the user to view their sessions, and
terminate one, or all of them. This ticket based system allows for the same
user interaction, thereby allowing more control over who is logged in or why.

If a user changes their password, tickets give the ability to log out all
pre-existing sessions so that the user is required to login again on any and
all devices.

What is session fixation?
~~~~~~~~~~~~~~~~~~~~~~~~~

Session fixation is an attack that permits an attacker to hijack a valid
session. Generally this is done by going to the website and retrieving an
session, that session is then given to the victim. As soon as the victim logs
in, the attacker who still has the same session token is able to see what is
being stored in the session which may potentially leak data. For authentication
policies that store the authentication in the session this would give the
attacker full control over the victim's account.

You stop session fixation by dropping the session when going across an
authentication boundary (login/logout). This will recreate the session from
scratch, which leaves the attacker with a session that is worthless.

Vary headers
~~~~~~~~~~~~

When an HTTP request is made, the content is usually cached for as long as
possible to avoid having to do more trips to the backend server (for reverse
proxies) and more requests to the server for browsers. However proxies and
browsers can't know that the page for example contains information that is
dependent on a particular HTTP header, that is where the ``vary`` HTTP header
comes in.

Using ``vary`` you can tell the proxies or web browser that this page is to be
cached, but it is dependent on a particular header. For example ``vary:
cookie`` means the cache is allowed to return the page without requesting
information from the backend server so long the cookie the client sends is the
exact same as at the time of the previous response generated.

For more take a look at `RFC7231 section 7.1.4
<http://tools.ietf.org/html/rfc7231#section-7.1.4>`__ which explains what this
header does and means.

