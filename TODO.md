# TODO

- Investigate crash when closing the macro editor tab after editing a macro; reproduce steps and guard the shutdown flow so PyQt quits cleanly.
- Persist macros globally instead of per-profile so profiles only store extension settings, per-layer keymaps, and per-layer RGB mappings.
- Mirror the per-key RGB editor grid across both axes so the preview aligns with the physical LED layout.
