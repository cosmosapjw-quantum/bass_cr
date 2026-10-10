# First execution and capture issue

First solver/validation campaign exited 0 with all 25 acceptance rows passing.
The pretty JSON packet exceeded the tool capture budget (107105 output tokens;
tool returned a truncated capture). This is a packaging/output-capture failure,
not a scientific validation failure. The entire received partial capture is
retained in evidence/FIRST_RUN_CAPTURE.log. Its validation prefix is intact and
stored in evidence/VALIDATION.json. Full packet bytes were not persisted by the
process. No claim of complete packet export is made until a bounded, approved
export computes and actually persists those bytes. No repair has been used.
