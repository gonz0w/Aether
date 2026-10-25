# Serial SESSION inputs

Three LF-terminated command lines preserve the accepted SESSION command sequence.
Send command1 only at the first real `$ ` prompt, command2 after its returned
prompt, command3 after the next prompt. Never preload later commands. No prompt
is expected after exit0. See [handoff](../SESSION-SERIAL.md). Native NOT RUN.
Original source and helper remain unchanged. The manifest pins all inputs.
