
Assessed Course Work 1.0 – Work Requirements
1. Design and develop a GUI-based LSB Replacement steganography and steganalysis program.
➢ Attempt to meet at least the basic program requirements listed
➢ Test program thoroughly before the demo
2. This program can be written in a language of your choice (eg. Python, C, Java) or customized
from a downloaded one.
3. You may not use online steganography portals.
4. You may use genAI tools as an assistant to augment the process of completing your
assignment, such as to understand concepts or questions related to the assignment;
generate ideas for the assignment, code; or get suggestions for code improvement.
5. Remember, genAI is not likely to generate a response that would be seen as quality work
and any code generated should be debugged and improved. It is each team member’s
responsibility—not the tool’s—to fully understand, ensure the quality, integrity, and
accuracy of the assignment you submit.
6. Conduct the demo with clear, comprehensive explanation and with minimal to no errors.
7. Demo dates: Weeks 5 and 6 (Thursday 3rd and 10th October 2024; Fridays 4th and 11th
October 2024) – to accommodate 28 teams with only 3 instructors. Teams order will be
swapped for ACW2.
8. Work in your own team and be responsible for each member’s role/task allocations.
9. All team members must be present on the demo dates. Members who are absent will be
separately assessed. Zero marks awarded for absence without valid reason eg. MC
10. No code submission or report is needed.
Assessed Course Work 1.0 – Program Requirements:
1. Support steganographic encode and decode of a TEXT file payload with different cover
object types as follows:
➢ Image files (eg. GIF, BMP, PNG) – at least 1 type
➢ Audio-visual files (eg. mp3, mp4, wav) – at least 1 type, preferred1
➢ Examples:
Example Payload Cover Object
1. Text file (Contents) Image file (eg. bmp)
2. Text file (Contents) Audio file (eg. wav)
1 Optional but will earn bonus points if successfully implemented
SIT Internal
3. Text file (Contents) Video file (eg. mp4)
2. Number of LSBs to use must be selectable from bits 1 to 8 of the cover object. Selection of
number of LSBs to be implemented as part of GUI. User can select the number of bits to
hide, starting from bit 0 (see following examples).
➢ Examples:
No. of LSB Cover
Object Bits Selected
Bit(s) used Display / Play Cover Object and Stego
Object
1 Bit 0 Any distortion?
4 Bits 0, 1, 2, and 3 Any distortion?
6 Bits 0, 1, 2, 3, 4, and 5 Any distortion? (Should start to see)
3. Drag and drop, and explorer-type functionality as part of GUI to select both cover and stego
objects and payload preferred2
4. Program to implement limit check and display error message should selected payload be
too large for selected cover object.
5. GUI able to play payload / display both cover and stego objects for comparison.
6. Work in your own team and be responsible for each member’s role/task allocations.
Assessed Course Work 1.0 – Rubrics (20%)
1. Support for range of cover object types:
➢ Support for different cover object types?
2. Supports the use of up to 8 bits of the cover object for payload hiding and retrieval:
➢ Able to use up to 8 LSBs (bits 0, 1, 2, 3, 4, 5, 6 and 7) of the cover object’s bytes?
3. GUI design:
➢ Facilitates selection of payload, stego and cover objects via drag and drop/explorer style
interaction?
➢ Facilitates play / display of cover and stego objects for comparison?
➢ Facilitates selection of LSBs of the cover object to use eg. from bits 0 to 7?
4. Understanding and contribution: individual
5. Innovation (optional2): Examples: TEXT to TEXT (white spaces)? Additional payload types
supported beyond TEXT? .mp4 as cover object type?
2 Optional but will earn bonus points if successfully implemented
