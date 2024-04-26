cmtconv - CMT (Cassette Tape) Image Generation/Conversion
==========================================================

### Playing CMT (Cassette Tape) Images

`cmtconv` is used to generate `.wav` files that can be played into
microcomputers. It can be handy to play these directly from your
development host, and even more handy to add an separate audio interface
(usually USB) to dedicate to this.

To load `cmtconv` output into your microcomputer from a Linux system, you
can list the names and numbers of your "sinks" (outputs), and then play the
file to a given sink (name or number) from that list with:

    pactl list short sinks
    paplay -d SINK …/….wav

Recording should be done not with `parec` (which always writes the output
in raw format) but `parecord` (use SIGINT to stop recording):

    parecord --file-format=wav --format=u8 --channels=1 -d SRCNAME FILE.wav

The `pavucontrol` window can be used to view levels during recording and
playback.


Similar and Related Tools
-------------------------

- MAME [Castool]: Converts various formats (CoCo `.CAS`, C64 `.TAP`, etc.
  etc.) to WAV files for use with MAME.
- [minimodem]: A command-line program which generates/decodes FSK audio at
  any specified baud rate using various framing protocols. Supports many
  standard FSK protocols, including Bell103, Bell202, RTTY, TTY/TDD, NOAA
  SAME, and Caller-ID. This can decode, at least to some degree, certain
  FSK cassette tape formats as well.



<!-------------------------------------------------------------------->
[Castool]: https://docs.mamedev.org/tools/castool.html
[minimodem]: https://github.com/kamalmostafa/minimodem
