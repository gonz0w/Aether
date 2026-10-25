/* Compile-only probe: no libc, OS calls, entry point, or target runtime claim. */
unsigned long aether_probe_add(unsigned long left, unsigned long right)
{
    return left + right;
}
