====================
django-fileprocessor
====================

A prototype project for something we have been needing all along: efficient
file processing - from within templates!

Right now, if you are like me, you probably use something like easy_thumbnail
for scaling of images for your website. You might even have written some code
to extract thumbnails from PDF files or from video files. All really great work!

BUT. As our applications relying on this stuff might actually scale up a bit,
the amount of work our application servers are doing WHILE RENDERING THE TEMPLATE
can quickly become excessive. At the same time, if these servers were just doing
what they should be, namely data <-> view interactions, this would not be happening.

Moreover: if your server is, in principle, able to handle a mentioning on some
lame but immensely popular blog - why should it not be in practice? Because, 
right now - if you use easy_thumbnails - your server will block while rendering
templates until your thumbnails are gone.

So here is my concept solution:
When we need to do something with a file, while rendering a template, we first
put out a request. This request can be put out to some other server, but for 
small instances it can easily be the same server - just some other CPU doing the
work. This 'remote tag' basically passes any contents between the {% fileprocessor %}
and {% endfileprocessor %} along to this other server as a parameter (so far
called instructions), telling it what to do and where to get stuff from.

The remote server writes this to the database, generates a checksum thereof and
parses the instructions just well enough to generate some kind of representation
(ie. and image tag) of the stuff that will be rendered _later_.

After the HTML has been sent out to the client, the client will start making
individual requests for the URL's referred to in the representation code generate
while rendering the template. Calling these URL's directly triggers processing
the file in any possible way, according to the instructions in the database. When
this is done, the file is written to some kind of storage, somewhere and a redirect
to this file is generated.

On subsequent requests, all the 'file processing server' does is blurt out redirects
to that some old file. But as these are permanent redirects, they should also be
cached by the client which ought to be quite efficient. Furthermore, the template
rendering results can and should also be cached: we do not have to reach out to
the server all of the time to retreive the same kind of data.

So that's it. A work in progress. Feel free to join in. :)