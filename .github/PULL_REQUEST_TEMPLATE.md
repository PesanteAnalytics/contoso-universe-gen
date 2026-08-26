<!--
Thanks for contributing. Keep whichever parts of this are useful and delete the
rest — it is a prompt, not a form to complete.
-->

## What this changes

<!-- One or two sentences. Link the issue it closes, if there is one. -->

## Why

<!--
The problem, not the diff. If you measured something, put the number here —
"the catalogue goes from 14 to 18 subcategories" says more than "adds a
category".
-->

## How you checked it

<!--
CI runs ruff and the test suite on Python 3.12 and 3.13. What did you verify
that CI cannot? Generating data and looking at it counts, and for anything
touching the generators it is the thing that matters most.
-->

```bash
# the command you ran
```

## If this touches the generators

- [ ] `cug generate --strict` passes — foreign key integrity is clean
- [ ] The generated data looks right, not just the tests
- [ ] Nothing silently lost entries from a pool while being split or refactored

## If this adds a product category

- [ ] The YAML lives in `cug/categories/builtin/` and its filename matches its `plugin_id`
- [ ] It is listed in `enabled` in `cug/configs/default.toml` — otherwise generation ignores it
- [ ] Every `display_names` block has all eight languages
- [ ] It shows up in `DimProduct`, not only in `cug categories`

## If this adds a language

- [ ] `_GEO_BY_LANG` in `cug/i18n/geography.py` — cities hang off their own country
- [ ] Name pools in `cug/generators/customers.py`
- [ ] The README coverage table reflects the new depth
- [ ] Existing locales are unchanged — check the pools, not only that tests pass

<!--
Formatting note: please do not run `ruff format`. It is not adopted here and
would rewrite thousands of lines around your change. `ruff check` is the gate.
-->
