cmtconv - CMT (Cassette Tape) Image Generation/Conversion
==========================================================

### Playing CMT (Cassette Tape) Images

`b8tool/bin/cmtconv` is used to generate `.wav` files that can be played
into microcomputers. It can be handy to play these directly from your
development host, and even more handy to add an separate audio interface
(usually USB) to dedicate to this. On Linux systems, `pactl list short
sinks` will show a list of all sink (output) numbers, names and other
information. A name from this list can be passed to `paplay -d NAME
.build/obj/exe/…/….wav` to load the image on your microcomputer.

Recording should be done not with `parec` (which always writes the output
in raw format) but `parecord` (use SIGINT to stop recording):

    parecord --file-format=wav --format=u8 --channels=1 -d SRCNAME FILE.wav

The `pavucontrol` window can be used to view levels during recording and
playback.
