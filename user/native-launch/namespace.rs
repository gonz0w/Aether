// SPDX-License-Identifier: BSD-2-Clause
// Trusted user-space mapping, not an authority boundary against its own process.
pub struct Entry<'a> {
    pub name: &'a [u8],
    pub executable: u64,
}
pub struct Namespace<'a> {
    pub entries: &'a [Entry<'a>],
}
impl Namespace<'_> {
    pub fn lookup(&self, name: &[u8]) -> Result<u64, i64> {
        if name.len() > 31 {
            return Err(-36);
        }
        if name.is_empty()
            || name == b"."
            || name == b".."
            || name
                .iter()
                .any(|c| !c.is_ascii_alphanumeric() && !b"-_.".contains(c))
        {
            return Err(-22);
        }
        // No fallback to another namespace, PATH, cwd or raw numeric grants.
        for entry in self.entries {
            if name == entry.name {
                return if entry.executable == 0 {
                    Err(-13)
                } else {
                    Ok(entry.executable)
                };
            }
        }
        Err(-2)
    }
}
