Make sure that the count returned after `test2` is `2` and not `1`. This means that the second connection reconnected to the previous analysis and recovered the old state.

You can simulate a disconnect by calling `d.socket.close()`.
