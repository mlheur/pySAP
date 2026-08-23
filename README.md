# pySAP

My "Simple-As-Possible" CPU emulator, in python.

This project started as a self-edification assignment,
to help me understand the contents of binary ROM files,
such as Vic-20 emulators, video game console emulators,
and custom phone & tablet operating systems.

It was highly inspired by Ben Eater's breadboard CPU.

Since those ROM binaries are purely assembled code + data,
understanding their contents becomes obvious after 'inventing'
a machine that uses assembled code + data.

In this specific case, the 'ROM' for the SAP CPU is the
the lookup table used by the instruction decoder to set
the control lines based on the instruction's bits and
the various flag bits.  In the current version, that table
is built dynamically at startup to simplify the process
of adding more instructions.  An unfortunate trade-off is
the deprecation of that depercation of that binary LUT
residing in the source files.
