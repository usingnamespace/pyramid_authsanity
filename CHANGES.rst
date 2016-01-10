0.1.0a2
=======

- Bert was asleep at the keyboard, the fix below is now actually properly fixed
  by decoding to ascii, which is safe because it is base64.

0.1.0a1
=======

- Ticket value is now a string instead of binary, this way Python 3's
  json.dumps() will be able to serialize the value sent to the sources
  remember function.


0.1.0a0
=======

 - Initial release.
